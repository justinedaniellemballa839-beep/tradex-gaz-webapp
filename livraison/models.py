from django.db import models
from django.conf import settings
from commandes.models import Commande


class Livraison(models.Model):
    """
    Le suivi de livraison d'une commande.
    Nouveau flux : le gérant attribue la livraison à un livreur précis,
    qui doit ensuite l'accepter avant de commencer à livrer.
    """
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente d\'attribution'
        ASSIGNEE = 'assignee', 'Assignée, en attente d\'acceptation'
        EN_COURS = 'en_cours', 'En cours de livraison'
        LIVREE = 'livree', 'Livrée'

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='livraison')
    livreur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'livreur'}, related_name='livraisons'
    )
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    date_assignation = models.DateTimeField(null=True, blank=True)
    date_acceptation = models.DateTimeField(null=True, blank=True)
    date_livraison = models.DateTimeField(null=True, blank=True)

    # Position en temps réel du livreur (mise à jour pendant la course)
    position_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    position_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    position_precision = models.FloatField(null=True, blank=True, help_text="Précision GPS en mètres")

    def __str__(self):
        return f"Livraison commande #{self.commande.id} - {self.get_statut_display()}"

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"