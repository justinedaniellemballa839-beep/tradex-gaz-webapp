from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def liste_json(request):
    """Consultée par le clignotant/la cloche pour afficher les dernières notifications."""
    notifs = request.user.notifications.all()[:10]
    non_lues = request.user.notifications.filter(lue=False).count()
    return JsonResponse({
        'non_lues': non_lues,
        'notifications': [
            {
                'id': n.id,
                'titre': n.titre,
                'message': n.message,
                'lien': n.lien,
                'lue': n.lue,
                'date': n.date_creation.strftime('%d/%m %H:%M'),
            }
            for n in notifs
        ],
    })


@login_required
def marquer_lue(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, destinataire=request.user)
    notif.lue = True
    notif.save()
    if notif.lien:
        return redirect(notif.lien)
    return redirect('accueil')


@login_required
def marquer_toutes_lues(request):
    request.user.notifications.filter(lue=False).update(lue=True)
    return JsonResponse({'ok': True})
