from django import forms
from .models import Avis
from .models import Approvisionnement, ProduitGaz


class ApprovisionnementForm(forms.ModelForm):
    """Cas d'utilisation "gérer approvisionnements"."""
    class Meta:
        model = Approvisionnement
        fields = ('produit', 'quantite', 'fournisseur')


class StockForm(forms.ModelForm):
    """Cas d'utilisation "gérer le stock" : ajuster directement le stock d'un produit."""
    class Meta:
        model = ProduitGaz
        fields = ('stock_disponible',)
class AvisForm(forms.ModelForm):
    """Permet à un client de laisser un avis sur un produit."""
    class Meta:
        model = Avis
        fields = ('note', 'commentaire')
        widgets = {
            'note': forms.Select(choices=[(i, f"{i} / 5") for i in range(1, 6)]),
        }