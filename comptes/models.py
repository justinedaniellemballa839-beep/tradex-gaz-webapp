from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """
    Notre utilisateur personnalisé.
    On part du modèle Django de base (AbstractUser, qui gère déjà
    le mot de passe, le nom d'utilisateur, l'email, etc.)
    et on y ajoute un rôle + des infos utiles au contexte camerounais.
    """

    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        GERANT_STATION = 'gerant_station', 'Gérant de station'
        LIVREUR = 'livreur', 'Livreur'
        ADMINISTRATEUR = 'administrateur', 'Administrateur'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name="Rôle"
    )
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    ville = models.CharField(max_length=100, blank=True, verbose_name="Ville")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"