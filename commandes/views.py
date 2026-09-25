import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import Commande, LigneCommande, Paiement
from .forms import CommandeForm, PaiementForm, AnnulationForm
from .utils import calculer_frais_livraison
from notifications.services import notifier, notifier_role


@login_required
def passer_commande(request):
    """Cas d'utilisation "passer une commande"."""
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.client = request.user

            if commande.mode_livraison == Commande.ModeLivraison.LIVRAISON:
                lat = request.POST.get('latitude_client')
                lng = request.POST.get('longitude_client')
                commande.latitude_client = lat or None
                commande.longitude_client = lng or None
                commande.frais_livraison = calculer_frais_livraison(lat, lng, commande.point_distribution)

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


def _creer_livraison_si_necessaire(commande):
    if commande.mode_livraison == Commande.ModeLivraison.LIVRAISON:
        from livraison.models import Livraison
        livraison, _ = Livraison.objects.get_or_create(commande=commande)
        notifier_role(
            'gerant_station',
            "Nouvelle livraison à attribuer",
            f"La commande CMD-{commande.id:06d} attend un livreur.",
            lien=f'/livraison/attribuer/#livraison-{livraison.id}',
        )


def _decrementer_stock(commande):
    """Diminue le stock de chaque produit commandé, une fois le paiement validé."""
    for ligne in commande.lignes.all():
        produit = ligne.produit
        produit.stock_disponible = max(0, produit.stock_disponible - ligne.quantite)
        produit.save()


def _notifier_confirmation(commande):
    notifier(
        commande.client,
        "Commande confirmée",
        f"Ta commande CMD-{commande.id:06d} est confirmée.",
        lien=f'/commandes/{commande.id}/#commande-{commande.id}',
    )


@login_required
def effectuer_paiement(request, commande_id):
    """
    Cas d'utilisation "effectuer paiement".
    Mobile Money : un code de confirmation simulé est exigé (comme un vrai OTP).
    Espèces : validation directe, pas d'OTP nécessaire (paiement à la livraison).
    """
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)

    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            methode = form.cleaned_data['methode']
            numero = form.cleaned_data.get('numero_telephone')

            if methode == Paiement.Methode.ESPECES:
                Paiement.objects.create(
                    commande=commande,
                    methode=methode,
                    statut=Paiement.Statut.EN_ATTENTE,
                )
                commande.statut = Commande.Statut.CONFIRMEE
                commande.save()
                _creer_livraison_si_necessaire(commande)
                _decrementer_stock(commande)
                _notifier_confirmation(commande)
                messages.success(request, "Commande confirmée, tu paieras en espèces à la livraison/au retrait.")
                return redirect('detail_commande', commande_id=commande.id)

            code = f"{random.randint(1000, 9999)}"
            request.session[f'otp_paiement_{commande.id}'] = code
            request.session[f'otp_methode_{commande.id}'] = methode
            request.session[f'otp_numero_{commande.id}'] = numero
            request.session.modified = True

            messages.info(request, f"[SIMULATION] Code de confirmation envoyé par SMS au {numero} : {code}")
            return redirect('confirmer_code_paiement', commande_id=commande.id)
    else:
        form = PaiementForm()

    return render(request, 'commandes/paiement.html', {'form': form, 'commande': commande})


@login_required
def confirmer_code_paiement(request, commande_id):
    """Deuxième étape du paiement Mobile Money : saisie du code reçu (simulé) par SMS."""
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)
    code_attendu = request.session.get(f'otp_paiement_{commande.id}')

    if not code_attendu:
        messages.error(request, "Aucune demande de paiement en attente. Recommence.")
        return redirect('effectuer_paiement', commande_id=commande.id)

    if request.method == 'POST':
        code_saisi = request.POST.get('code', '').strip()
        if code_saisi == code_attendu:
            methode = request.session.pop(f'otp_methode_{commande.id}')
            numero = request.session.pop(f'otp_numero_{commande.id}')
            request.session.pop(f'otp_paiement_{commande.id}')

            Paiement.objects.create(
                commande=commande,
                methode=methode,
                numero_telephone=numero,
                statut=Paiement.Statut.VALIDE,
                date_paiement=timezone.now(),
                reference=f"TDX-{commande.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            )
            commande.statut = Commande.Statut.CONFIRMEE
            commande.save()
            _creer_livraison_si_necessaire(commande)
            _decrementer_stock(commande)
            _notifier_confirmation(commande)

            messages.success(request, "Paiement validé ! Ta commande est confirmée.")
            return redirect('detail_commande', commande_id=commande.id)
        else:
            messages.error(request, "Code incorrect, réessaie.")

    return render(request, 'commandes/confirmer_code.html', {'commande': commande})


@login_required
def detail_commande(request, commande_id):
    """Affiche le détail d'une commande, avec son délai estimé."""
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)
    return render(request, 'commandes/detail_commande.html', {'commande': commande})


def _restituer_stock(commande):
    for ligne in commande.lignes.all():
        produit = ligne.produit
        produit.stock_disponible += ligne.quantite
        produit.save()


def _calculer_taux_remboursement(commande):
    """
    85% si annulation >24h avant la livraison estimée, 70% entre 12h et 24h,
    50% en dessous de 12h ou si la livraison est déjà en cours.
    """
    from livraison.models import Livraison
    try:
        livraison = commande.livraison
        if livraison.statut == Livraison.Statut.EN_COURS:
            return 50
    except Livraison.DoesNotExist:
        pass

    delai_restant = (
        commande.date_creation + timezone.timedelta(hours=commande.delai_estime_heures)
    ) - timezone.now()
    heures_restantes = delai_restant.total_seconds() / 3600

    if heures_restantes >= 24:
        return 85
    elif heures_restantes >= 12:
        return 70
    else:
        return 50


@login_required
def annuler_commande(request, commande_id):
    """Politique d'annulation : remboursement dégressif selon le délai avant livraison."""
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)

    if commande.statut not in (Commande.Statut.EN_ATTENTE, Commande.Statut.CONFIRMEE):
        messages.error(request, "Cette commande ne peut plus être annulée.")
        return redirect('detail_commande', commande_id=commande.id)

    if request.method == 'POST':
        form = AnnulationForm(request.POST)
        if form.is_valid():
            paiement_valide = hasattr(commande, 'paiement') and commande.paiement.statut == Paiement.Statut.VALIDE

            if paiement_valide:
                taux = _calculer_taux_remboursement(commande)
                commande.taux_remboursement = taux
                commande.montant_rembourse = commande.montant_total * taux / 100
            else:
                commande.taux_remboursement = None
                commande.montant_rembourse = None

            commande.statut = Commande.Statut.ANNULEE
            commande.motif_annulation = form.cleaned_data['motif']
            commande.date_annulation = timezone.now()
            commande.save()

            if paiement_valide:
                _restituer_stock(commande)

            from livraison.models import Livraison
            try:
                livraison = commande.livraison
                if livraison.statut != Livraison.Statut.EN_COURS:
                    livraison.statut = Livraison.Statut.ANNULEE
                    livraison.save()
            except Livraison.DoesNotExist:
                pass

            notifier_role(
                'gerant_station',
                "Commande annulée",
                f"La commande CMD-{commande.id:06d} a été annulée par le client.",
                lien=f'/commandes/{commande.id}/#commande-{commande.id}',
            )

            if commande.montant_rembourse:
                messages.success(request, f"Commande annulée. Remboursement de {commande.montant_rembourse} FCFA ({commande.taux_remboursement}%) à traiter.")
            else:
                messages.success(request, "Commande annulée.")
            return redirect('detail_commande', commande_id=commande.id)
    else:
        form = AnnulationForm()

    return render(request, 'commandes/annuler.html', {'form': form, 'commande': commande})


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
    p.drawString(50, y, f"Commande : CMD-{commande.id:06d}")
    y -= 20
    p.drawString(50, y, f"Client : {commande.client.username}")
    y -= 20
    p.drawString(50, y, f"Date de commande : {commande.date_creation.strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Mode : {commande.get_mode_livraison_display()}")
    y -= 20
    if commande.adresse_livraison:
        p.drawString(50, y, f"Adresse de livraison : {commande.adresse_livraison}")
        y -= 20
    p.drawString(50, y, f"Methode de paiement : {commande.paiement.get_methode_display()}")
    y -= 20
    if commande.paiement.numero_telephone:
        p.drawString(50, y, f"Numero : {commande.paiement.numero_masque()}")
        y -= 20
    p.drawString(50, y, f"Reference : {commande.paiement.reference or 'N/A'}")
    y -= 20
    p.drawString(50, y, f"Date de paiement : {commande.paiement.date_paiement.strftime('%d/%m/%Y %H:%M') if commande.paiement.date_paiement else 'N/A'}")

    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Produits commandes")
    y -= 20
    p.setFont("Helvetica", 11)
    for ligne in commande.lignes.all():
        p.drawString(50, y, f"{ligne.quantite} x {ligne.produit.nom} - {ligne.sous_total} FCFA")
        y -= 18

    if commande.frais_livraison:
        p.drawString(50, y, f"Frais de livraison : {commande.frais_livraison} FCFA")
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, f"Total paye : {commande.montant_total} FCFA")

    p.showPage()
    p.save()
    return response
