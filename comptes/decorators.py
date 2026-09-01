from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


def role_required(role):
    """
    Décorateur réutilisable : vérifie que l'utilisateur connecté
    a bien le rôle attendu (ex: 'gerant_station', 'livreur', 'administrateur').
    Si ce n'est pas le cas, on refuse l'accès (erreur 403).
    """
    def verificateur(user):
        if user.is_authenticated and user.role == role:
            return True
        raise PermissionDenied

    def decorateur(vue):
        return login_required(user_passes_test(verificateur)(vue))

    return decorateur