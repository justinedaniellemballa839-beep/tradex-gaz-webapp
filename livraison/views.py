from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from comptes.decorators import role_required
from .models import Livraison


@role_required('livreur')
def liste_livraisons(request):
    """
    Cas d'utilisation "consulter livraison".
    Affiche les livraisons en attente (que n'importe quel livreur peut prendre)
    et celles déjà prises en charge par ce livreur précis.
    """
    en_attente = Livraison.objects.filter(statut=Livraison.Statut.EN_ATTENTE)
    mes_livraisons = Livraison.objects.filter(livreur=request.user, statut=Livraison.Statut.EN_COURS)
    return render(request, 'livraison/liste.html', {
        'en_attente': en_attente,
        'mes_livraisons': mes_livraisons,
    })


@role_required('livreur')
def prendre_en_charge(request, livraison_id):
    """Un livreur s'attribue une livraison en attente."""
    livraison = get_object_or_404(Livraison, id=livraison_id, statut=Livraison.Statut.EN_ATTENTE)
    livraison.livreur = request.user
    livraison.statut = Livraison.Statut.EN_COURS
    livraison.date_prise_en_charge = timezone.now()
    livraison.save()
    messages.success(request, "Livraison prise en charge.")
    return redirect('detail_livraison', livraison_id=livraison.id)


@role_required('livreur')
def detail_livraison(request, livraison_id):
    """
    Cas d'utilisation "localiser lieu de livraison" (l'adresse du client)
    et "contacter client" (son numéro de téléphone), regroupés ici.
    """
    livraison = get_object_or_404(Livraison, id=livraison_id, livreur=request.user)
    return render(request, 'livraison/detail.html', {'livraison': livraison})


@role_required('livreur')
def confirmer_livraison(request, livraison_id):
    """Cas d'utilisation "confirmer livraison"."""
    livraison = get_object_or_404(Livraison, id=livraison_id, livreur=request.user)
    livraison.statut = Livraison.Statut.LIVREE
    livraison.date_livraison = timezone.now()
    livraison.save()

    livraison.commande.statut = livraison.commande.Statut.LIVREE
    livraison.commande.save()

    messages.success(request, "Livraison confirmée !")
    return redirect('liste_livraisons')