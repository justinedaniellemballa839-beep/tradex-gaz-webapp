from django.db import models
from django.conf import settings
from commandes.models import Commande


class Livraison(models.Model):
    """
    Le suivi de livraison d'une commande, géré par un livreur.
    Créée automatiquement dès qu'une commande est payée.
    """
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente d\'un livreur'
        EN_COURS = 'en_cours', 'En cours de livraison'
        LIVREE = 'livree', 'Livrée'

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='livraison')
    livreur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'livreur'}, related_name='livraisons'
    )
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    date_prise_en_charge = models.DateTimeField(null=True, blank=True)
    date_livraison = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Livraison commande #{self.commande.id} - {self.get_statut_display()}"

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"