from django import forms
from comptes.models import Utilisateur
from livraison.models import Livraison


class UtilisateurAdminForm(forms.ModelForm):
    """Cas d'utilisation "gérer les comptes utilisateurs" : changer le rôle ou désactiver un compte."""
    class Meta:
        model = Utilisateur
        fields = ('role', 'is_active')


class StatutLivraisonForm(forms.ModelForm):
    """Cas d'utilisation "changer statut de livraison"."""
    class Meta:
        model = Livraison
        fields = ('statut',)