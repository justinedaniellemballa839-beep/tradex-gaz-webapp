from django.shortcuts import render
from .models import ProduitGaz, PointDistribution


def liste_produits(request):
    """
    Cas d'utilisation "consulter produit de gaz" : affiche tous
    les produits actifs, visibles par n'importe qui (visiteur ou client).
    """
    produits = ProduitGaz.objects.filter(actif=True)
    return render(request, 'catalogue/produits.html', {'produits': produits})


def liste_points_distribution(request):
    """
    Cas d'utilisation "rechercher les points de distribution".
    Pour l'instant une simple liste ; la recherche par ville/carte
    viendra en Phase 8 avec l'API de géolocalisation.
    """
    points = PointDistribution.objects.filter(actif=True)
    return render(request, 'catalogue/points_distribution.html', {'points': points})