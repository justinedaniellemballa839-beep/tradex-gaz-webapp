from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


class UtilisateurAdmin(UserAdmin):
    """
    On personnalise un peu l'affichage admin pour voir le rôle,
    le téléphone et la ville directement dans la liste des utilisateurs.
    """
    list_display = ('username', 'email', 'role', 'telephone', 'ville', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations complémentaires', {'fields': ('role', 'telephone', 'ville')}),
    )


admin.site.register(Utilisateur, UtilisateurAdmin)