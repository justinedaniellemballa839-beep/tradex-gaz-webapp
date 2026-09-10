from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from comptes.decorators import role_required
from .models import Livraison


@role_required('gerant_station')
def attribuer_livraisons(request):
    """Le gérant attribue chaque livraison en attente à un livreur précis."""
    from comptes.models import Utilisateur

    if request.method == 'POST':
        livraison_id = request.POST.get('livraison_id')
        livreur_id = request.POST.get('livreur_id')
        livraison = get_object_or_404(Livraison, id=livraison_id, statut=Livraison.Statut.EN_ATTENTE)
        livreur = get_object_or_404(Utilisateur, id=livreur_id, role='livreur')

        livraison.livreur = livreur
        livraison.statut = Livraison.Statut.ASSIGNEE
        livraison.date_assignation = timezone.now()
        livraison.save()

        messages.success(request, f"Livraison assignée à {livreur.username}.")
        return redirect('attribuer_livraisons')

    en_attente = Livraison.objects.filter(statut=Livraison.Statut.EN_ATTENTE)
    livreurs = Utilisateur.objects.filter(role='livreur', is_active=True)
    return render(request, 'livraison/attribuer.html', {'en_attente': en_attente, 'livreurs': livreurs})


@role_required('livreur')
def mes_demandes(request):
    """Livraisons assignées à ce livreur, en attente de son acceptation."""
    demandes = Livraison.objects.filter(livreur=request.user, statut=Livraison.Statut.ASSIGNEE)
    return render(request, 'livraison/demandes.html', {'demandes': demandes})


@role_required('livreur')
def accepter_livraison(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id, livreur=request.user, statut=Livraison.Statut.ASSIGNEE)
    livraison.statut = Livraison.Statut.EN_COURS
    livraison.date_acceptation = timezone.now()
    livraison.save()
    messages.success(request, "Livraison acceptée, bonne route !")
    return redirect('detail_livraison', livraison_id=livraison.id)


@role_required('livreur')
def refuser_livraison(request, livraison_id):
    """La livraison repart en attente, pour qu'un autre livreur puisse l'accepter."""
    livraison = get_object_or_404(Livraison, id=livraison_id, livreur=request.user, statut=Livraison.Statut.ASSIGNEE)
    livraison.livreur = None
    livraison.statut = Livraison.Statut.EN_ATTENTE
    livraison.date_assignation = None
    livraison.save()
    messages.info(request, "Livraison refusée.")
    return redirect('mes_demandes')


@role_required('livreur')
def liste_livraisons(request):
    """Livraisons en cours acceptées par ce livreur."""
    mes_livraisons = Livraison.objects.filter(livreur=request.user, statut=Livraison.Statut.EN_COURS)
    return render(request, 'livraison/liste.html', {'mes_livraisons': mes_livraisons})


@role_required('livreur')
def detail_livraison(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id, livreur=request.user)
    return render(request, 'livraison/detail.html', {'livraison': livraison})


@login_required
def mettre_a_jour_position(request, livraison_id):
    """
    Appelée automatiquement par le navigateur du livreur (JS) pour envoyer
    sa position GPS en temps réel, tant que la livraison est en cours.
    """
    livraison = get_object_or_404(Livraison, id=livraison_id, livreur=request.user, statut=Livraison.Statut.EN_COURS)
    if request.method == 'POST':
        livraison.position_lat = request.POST.get('lat')
        livraison.position_lng = request.POST.get('lng')
        livraison.position_precision = request.POST.get('precision')
        livraison.position_maj_le = timezone.now()
        livraison.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


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


@login_required
def suivre_livraison(request, commande_id):
    """
    Cas d'utilisation implicite du client : suivre sa livraison en temps réel.
    """
    livraison = get_object_or_404(Livraison, commande_id=commande_id, commande__client=request.user)
    return render(request, 'livraison/suivi.html', {'livraison': livraison})


@login_required
def position_actuelle(request, livraison_id):
    """API JSON consultée régulièrement par le navigateur du client pour rafraîchir la carte."""
    livraison = get_object_or_404(Livraison, id=livraison_id, commande__client=request.user)
    return JsonResponse({
        'lat': float(livraison.position_lat) if livraison.position_lat else None,
        'lng': float(livraison.position_lng) if livraison.position_lng else None,
        'precision': livraison.position_precision,
        'statut': livraison.statut,
    })