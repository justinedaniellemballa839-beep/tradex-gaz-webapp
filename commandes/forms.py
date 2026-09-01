from django import forms
from .models import Commande, Paiement
from catalogue.models import ProduitGaz


class CommandeForm(forms.ModelForm):
    """
    Pour cette première version, un client choisit un seul produit
    et une quantité. On pourra évoluer vers un vrai panier
    multi-produits plus tard si besoin.
    """
    produit = forms.ModelChoiceField(
        queryset=ProduitGaz.objects.filter(actif=True),
        label="Produit souhaité"
    )
    quantite = forms.IntegerField(min_value=1, initial=1, label="Quantité")

    class Meta:
        model = Commande
        fields = ('point_distribution', 'adresse_livraison')


class PaiementForm(forms.ModelForm):
    """Cas d'utilisation "effectuer paiement" (simulé pour l'instant)."""
    class Meta:
        model = Paiement
        fields = ('methode',)