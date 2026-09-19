from .models import Notification


def notifier(destinataire, titre, message, lien=''):
    """Point d'entrée unique pour créer une notification, appelé depuis les autres apps."""
    Notification.objects.create(
        destinataire=destinataire, titre=titre, message=message, lien=lien
    )


def notifier_role(role, titre, message, lien=''):
    """Notifie tous les utilisateurs actifs ayant un rôle donné (gérants, admins)."""
    from comptes.models import Utilisateur
    destinataires = Utilisateur.objects.filter(role=role, is_active=True)
    for utilisateur in destinataires:
        notifier(utilisateur, titre, message, lien)
