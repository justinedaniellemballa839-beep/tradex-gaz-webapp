from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur


class InscriptionForm(UserCreationForm):
    """
    Formulaire d'inscription pour le visiteur qui devient client.
    On part du formulaire Django standard (UserCreationForm, qui gère
    déjà le mot de passe en toute sécurité) et on ajoute nos champs.
    """
    email = forms.EmailField(required=True, label="Email")
    telephone = forms.CharField(required=True, label="Téléphone", max_length=20)
    ville = forms.CharField(required=True, label="Ville")

    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'telephone', 'ville', 'password1', 'password2')

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.email = self.cleaned_data['email']
        utilisateur.telephone = self.cleaned_data['telephone']
        utilisateur.ville = self.cleaned_data['ville']
        utilisateur.role = Utilisateur.Role.CLIENT
        if commit:
            utilisateur.save()
        return utilisateur
class ProfilForm(forms.ModelForm):
    """
    Formulaire permettant à un utilisateur connecté de modifier
    ses propres informations (cas d'utilisation "gérer son profil").
    """
    class Meta:
        model = Utilisateur
        fields = ('email', 'telephone', 'ville')