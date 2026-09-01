from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .services import poser_question


@login_required
def chat(request):
    """
    Cas d'utilisation "interagir avec le chatbot".
    L'historique de la conversation est gardé en session (par utilisateur),
    pour que le chatbot se souvienne du fil de la discussion.
    """
    if 'historique_chat' not in request.session:
        request.session['historique_chat'] = []

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            historique = request.session['historique_chat']
            reponse = poser_question(message, historique)

            historique.append({'role': 'user', 'text': message})
            historique.append({'role': 'model', 'text': reponse})
            request.session['historique_chat'] = historique
            request.session.modified = True

        return redirect('chat')

    return render(request, 'chatbot/chat.html', {'historique': request.session['historique_chat']})


@login_required
def reinitialiser_chat(request):
    """Efface l'historique pour recommencer une conversation à zéro."""
    request.session['historique_chat'] = []
    return redirect('chat')