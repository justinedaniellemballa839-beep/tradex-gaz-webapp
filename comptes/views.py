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