import re
from django import forms
from django.core.exceptions import ValidationError
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
    """
    Cas d'utilisation "effectuer paiement".
    Le numéro de téléphone n'est exigé (et validé) que pour
    Orange Money et MTN Mobile Money, pas pour le paiement en espèces.
    """
    class Meta:
        model = Paiement
        fields = ('methode', 'numero_telephone')
        widgets = {
            'numero_telephone': forms.TextInput(attrs={
                'placeholder': 'Ex : 677123456',
                'class': 'form-control',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        methode = cleaned_data.get('methode')
        numero = (cleaned_data.get('numero_telephone') or '').strip()

        if methode in (Paiement.Methode.ORANGE_MONEY, Paiement.Methode.MTN_MOMO):
            if not numero:
                raise ValidationError({
                    'numero_telephone': "Le numéro Mobile Money est obligatoire pour ce mode de paiement."
                })

            numero_nettoye = numero.replace(' ', '').replace('+237', '')
            if not re.match(r'^6[5-9]\d{7}$', numero_nettoye):
                raise ValidationError({
                    'numero_telephone': "Numéro invalide. Format attendu : 9 chiffres commençant par 6 (ex : 677123456)."
                })
            cleaned_data['numero_telephone'] = numero_nettoye

        return cleaned_data