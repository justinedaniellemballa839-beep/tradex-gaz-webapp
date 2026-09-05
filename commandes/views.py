from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import Commande, LigneCommande, Paiement
from .forms import CommandeForm, PaiementForm


@login_required
def passer_commande(request):
    """Cas d'utilisation "passer une commande"."""
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.client = request.user
            commande.save()

            produit = form.cleaned_data['produit']
            quantite = form.cleaned_data['quantite']
            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix,
            )
            messages.success(request, "Commande créée ! Passe maintenant au paiement.")
            return redirect('effectuer_paiement', commande_id=commande.id)
    else:
        form = CommandeForm()

    return render(request, 'commandes/passer_commande.html', {'form': form})


@login_required
def effectuer_paiement(request, commande_id):
    """
    Cas d'utilisation "effectuer paiement".
    Paiement simulé pour l'instant : on ne contacte pas encore
    une vraie API Mobile Money (décision assumée, RCCM requis non disponible).
    """
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)

    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.commande = commande
            paiement.statut = Paiement.Statut.VALIDE
            paiement.date_paiement = timezone.now()
            paiement.save()

            commande.statut = Commande.Statut.CONFIRMEE
            commande.save()

            from livraison.models import Livraison
            Livraison.objects.get_or_create(commande=commande)

            messages.success(request, "Paiement validé ! Ta commande est confirmée.")
            return redirect('detail_commande', commande_id=commande.id)
    else:
        form = PaiementForm()

    return render(request, 'commandes/paiement.html', {'form': form, 'commande': commande})


@login_required
def detail_commande(request, commande_id):
    """Affiche le détail d'une commande, avec son délai estimé."""
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)
    return render(request, 'commandes/detail_commande.html', {'commande': commande})


@login_required
def historique_commandes(request):
    """Cas d'utilisation "consulter historique des commandes"."""
    commandes = request.user.commandes.all()
    return render(request, 'commandes/historique.html', {'commandes': commandes})


@login_required
def telecharger_recu(request, commande_id):
    """
    Génère un reçu PDF téléchargeable, uniquement si le paiement
    de la commande a bien été validé.
    """
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)

    if not hasattr(commande, 'paiement') or commande.paiement.statut != Paiement.Statut.VALIDE:
        messages.error(request, "Aucun reçu disponible : le paiement n'est pas encore validé.")
        return redirect('detail_commande', commande_id=commande.id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_commande_{commande.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    largeur, hauteur = A4

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, hauteur - 60, "Tradex Distrib'IA - Recu de paiement")

    p.setFont("Helvetica", 11)
    y = hauteur - 100
    p.drawString(50, y, f"Commande n : {commande.id}")
    y -= 20
    p.drawString(50, y, f"Client : {commande.client.username}")
    y -= 20
    p.drawString(50, y, f"Date de commande : {commande.date_creation.strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Adresse de livraison : {commande.adresse_livraison}")
    y -= 20
    p.drawString(50, y, f"Methode de paiement : {commande.paiement.get_methode_display()}")
    y -= 20
    p.drawString(50, y, f"Reference : {commande.paiement.reference or 'N/A'}")
    y -= 20
    p.drawString(50, y, f"Date de paiement : {commande.paiement.date_paiement.strftime('%d/%m/%Y %H:%M')}")

    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Produits commandes")
    y -= 20
    p.setFont("Helvetica", 11)
    for ligne in commande.lignes.all():
        p.drawString(50, y, f"{ligne.quantite} x {ligne.produit.nom} - {ligne.sous_total} FCFA")
        y -= 18

    y -= 20
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, f"Total paye : {commande.montant_total} FCFA")

    p.showPage()
    p.save()
    return response