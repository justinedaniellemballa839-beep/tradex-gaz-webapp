from django.shortcuts import render


def accueil(request):
    """
    Vue de la page d'accueil.
    Correspond au cas d'utilisation "visiter" du visiteur dans le diagramme :
    n'importe qui (connecté ou non) peut voir cette page.
    """
    return render(request, 'core/accueil.html')