from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from comptes.decorators import role_required
from comptes.models import Utilisateur
from commandes.models import Commande
from livraison.models import Livraison
from catalogue.models import ProduitGaz
from .forms import UtilisateurAdminForm, StatutLivraisonForm


@role_required('administrateur')
def tableau_de_bord(request):
    """
    Cas d'utilisation "superviser opérations".
    Vue d'ensemble rapide de l'activité de la plateforme.
    """
    contexte = {
        'nombre_utilisateurs': Utilisateur.objects.count(),
        'nombre_commandes': Commande.objects.count(),
        'commandes_en_attente': Commande.objects.filter(statut=Commande.Statut.EN_ATTENTE).count(),
        'livraisons_en_cours': Livraison.objects.filter(statut=Livraison.Statut.EN_COURS).count(),
        'produits_en_rupture': ProduitGaz.objects.filter(stock_disponible=0).count(),
    }
    return render(request, 'administration/tableau_de_bord.html', contexte)


@role_required('administrateur')
def gerer_comptes(request):
    """Cas d'utilisation "gérer les comptes utilisateurs"."""
    utilisateurs = Utilisateur.objects.all().order_by('role', 'username')
    return render(request, 'administration/comptes.html', {'utilisateurs': utilisateurs})


@role_required('administrateur')
def modifier_compte(request, utilisateur_id):
    """Permet de changer le rôle ou d'activer/désactiver un compte précis."""
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    if request.method == 'POST':
        form = UtilisateurAdminForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte mis à jour.")
            return redirect('gerer_comptes')
    else:
        form = UtilisateurAdminForm(instance=utilisateur)
    return render(request, 'administration/modifier_compte.html', {'form': form, 'utilisateur': utilisateur})


@role_required('administrateur')
def rapports_globaux(request):
    """Cas d'utilisation "consulter rapports globaux"."""
    ventes_par_produit = (
        Commande.objects.filter(statut__in=['confirmee', 'en_livraison', 'livree'])
        .values('lignes__produit__nom')
        .annotate(quantite_totale=Sum('lignes__quantite'), nombre_commandes=Count('id'))
        .order_by('-quantite_totale')
    )
    return render(request, 'administration/rapports.html', {'ventes_par_produit': ventes_par_produit})


@role_required('administrateur')
def gerer_livraisons(request):
    """Cas d'utilisation "changer statut de livraison" (vue d'ensemble + modification directe)."""
    livraisons = Livraison.objects.all().order_by('-id')
    return render(request, 'administration/livraisons.html', {'livraisons': livraisons})


@role_required('administrateur')
def modifier_statut_livraison(request, livraison_id):
    """Change manuellement le statut d'une livraison précise."""
    livraison = get_object_or_404(Livraison, id=livraison_id)
    if request.method == 'POST':
        form = StatutLivraisonForm(request.POST, instance=livraison)
        if form.is_valid():
            form.save()
            messages.success(request, "Statut de livraison mis à jour.")
            return redirect('gerer_livraisons')
    else:
        form = StatutLivraisonForm(instance=livraison)
    return render(request, 'administration/modifier_statut_livraison.html', {'form': form, 'livraison': livraison})