from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Une notification adressée à un utilisateur précis, liée
    à une action réelle du système (pas décorative).
    """
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    titre = models.CharField(max_length=150)
    message = models.CharField(max_length=255)
    lien = models.CharField(max_length=255, blank=True, help_text="Chemin relatif vers la page concernée")
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.destinataire.username} - {self.titre}"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']
