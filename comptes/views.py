from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import InscriptionForm


def inscription(request):
    """
    Vue d'inscription : un visiteur remplit le formulaire
    et devient automatiquement un client connecté.
    """
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            login(request, utilisateur)
            messages.success(request, "Bienvenue ! Ton compte a été créé avec succès.")
            return redirect('accueil')
    else:
        form = InscriptionForm()

    return render(request, 'comptes/inscription.html', {'form': form})
from django.contrib.auth.decorators import login_required
from .forms import ProfilForm


@login_required
def profil(request):
    """
    Vue "gérer son profil" : accessible uniquement si connecté
    (grâce à @login_required, qui redirige vers la page de connexion sinon).
    """
    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Ton profil a été mis à jour.")
            return redirect('profil')
    else:
        form = ProfilForm(instance=request.user)

    return render(request, 'comptes/profil.html', {'form': form})