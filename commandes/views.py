from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
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
    une vraie API Mobile Money (ce sera fait en Phase 8).
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