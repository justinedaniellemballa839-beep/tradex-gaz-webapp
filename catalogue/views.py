from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from comptes.decorators import role_required
from .models import ProduitGaz, PointDistribution, Approvisionnement, Avis
from .forms import ApprovisionnementForm, StockForm, AvisForm
from commandes.models import LigneCommande

SEUIL_ALERTE_STOCK = 10


def liste_produits(request):
    """Cas d'utilisation "consulter produit de gaz" (public)."""
    produits = ProduitGaz.objects.filter(actif=True)
    return render(request, 'catalogue/produits.html', {'produits': produits})


def liste_points_distribution(request):
    """Cas d'utilisation "rechercher les points de distribution" (public)."""
    points = PointDistribution.objects.filter(actif=True)
    return render(request, 'catalogue/points_distribution.html', {'points': points})


@role_required('gerant_station')
def gerer_stock(request):
    """Cas d'utilisation "gérer le stock"."""
    produits = ProduitGaz.objects.all()
    return render(request, 'catalogue/gerant/stock.html', {'produits': produits})


@role_required('gerant_station')
def modifier_stock(request, produit_id):
    """Permet d'ajuster manuellement le stock d'un produit précis."""
    produit = get_object_or_404(ProduitGaz, id=produit_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock mis à jour.")
            return redirect('gerer_stock')
    else:
        form = StockForm(instance=produit)
    return render(request, 'catalogue/gerant/modifier_stock.html', {'form': form, 'produit': produit})


@role_required('gerant_station')
def gerer_approvisionnements(request):
    """
    Cas d'utilisation "gérer approvisionnements".
    Chaque approvisionnement validé augmente automatiquement le stock.
    """
    if request.method == 'POST':
        form = ApprovisionnementForm(request.POST)
        if form.is_valid():
            approvisionnement = form.save(commit=False)
            approvisionnement.gerant = request.user
            approvisionnement.save()

            produit = approvisionnement.produit
            produit.stock_disponible += approvisionnement.quantite
            produit.save()

            messages.success(request, "Approvisionnement enregistré, stock mis à jour.")
            return redirect('gerer_approvisionnements')
    else:
        form = ApprovisionnementForm()

    approvisionnements = Approvisionnement.objects.all()[:20]
    return render(request, 'catalogue/gerant/approvisionnements.html', {
        'form': form,
        'approvisionnements': approvisionnements,
    })


@role_required('gerant_station')
def alertes_stock(request):
    """Cas d'utilisation "consulter alertes de stock"."""
    produits_en_alerte = ProduitGaz.objects.filter(stock_disponible__lt=SEUIL_ALERTE_STOCK)
    return render(request, 'catalogue/gerant/alertes_stock.html', {
        'produits_en_alerte': produits_en_alerte,
        'seuil': SEUIL_ALERTE_STOCK,
    })


@role_required('gerant_station')
def previsions_demande(request):
    """
    Cas d'utilisation "prévoir la demande" et "consulter prévisions IA".
    Utilise Gemini pour une vraie analyse en langage naturel,
    basée sur l'historique réel des commandes.
    """
    previsions = list(
        LigneCommande.objects
        .values('produit__nom')
        .annotate(quantite_moyenne=Avg('quantite'), nombre_commandes=Count('id'))
        .order_by('-quantite_moyenne')
    )

    from chatbot.services import analyser_previsions
    analyse_ia = analyser_previsions(previsions)

    return render(request, 'catalogue/gerant/previsions.html', {
        'previsions': previsions,
        'analyse_ia': analyse_ia,
    })


@role_required('gerant_station')
def gerer_avis(request):
    """Cas d'utilisation "gérer avis clients"."""
    if request.method == 'POST':
        avis_id = request.POST.get('avis_id')
        action = request.POST.get('action')
        avis = get_object_or_404(Avis, id=avis_id)
        if action == 'approuver':
            avis.approuve = True
            avis.save()
        elif action == 'rejeter':
            avis.approuve = False
            avis.save()
        elif action == 'supprimer':
            avis.delete()
        return redirect('gerer_avis')

    avis = Avis.objects.all()
    return render(request, 'catalogue/gerant/avis.html', {'avis': avis})


@login_required
def laisser_avis(request, produit_id):
    """
    Cas d'utilisation implicite du client : laisser un avis
    (nécessaire pour que le gérant puisse ensuite le "gérer").
    """
    produit = get_object_or_404(ProduitGaz, id=produit_id)

    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.produit = produit
            avis.client = request.user
            avis.save()
            messages.success(request, "Merci pour ton avis !")
            return redirect('liste_produits')
    else:
        form = AvisForm()

    return render(request, 'catalogue/laisser_avis.html', {'form': form, 'produit': produit})