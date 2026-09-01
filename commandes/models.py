from django.db import models
from django.conf import settings
from catalogue.models import ProduitGaz, PointDistribution


class Commande(models.Model):
    """
    Une commande passée par un client.
    Cas d'utilisation : "passer une commande", "consulter historique des commandes".
    """
    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente de paiement'
        CONFIRMEE = 'confirmee', 'Confirmée'
        EN_LIVRAISON = 'en_livraison', 'En cours de livraison'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commandes')
    point_distribution = models.ForeignKey(PointDistribution, on_delete=models.SET_NULL, null=True, blank=True)
    adresse_livraison = models.CharField(max_length=255, verbose_name="Adresse de livraison")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    date_creation = models.DateTimeField(auto_now_add=True)
    delai_estime_heures = models.PositiveIntegerField(default=24, verbose_name="Délai estimé (heures)")

    @property
    def montant_total(self):
        """Calcule le total en additionnant chaque ligne de la commande."""
        return sum(ligne.sous_total for ligne in self.lignes.all())

    def __str__(self):
        return f"Commande #{self.id} - {self.client.username}"

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_creation']


class LigneCommande(models.Model):
    """
    Un produit précis, avec sa quantité, à l'intérieur d'une commande.
    On garde le prix au moment de la commande (prix_unitaire),
    pour que l'historique reste exact même si le prix change plus tard.
    """
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(ProduitGaz, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=0)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"


class Paiement(models.Model):
    """
    Cas d'utilisation "effectuer paiement".
    Pour l'instant simulé (pas encore branché à une vraie API paiement,
    ce sera fait en Phase 8 avec un fournisseur Mobile Money).
    """
    class Methode(models.TextChoices):
        ORANGE_MONEY = 'orange_money', 'Orange Money'
        MTN_MOMO = 'mtn_momo', 'MTN Mobile Money'
        ESPECES = 'especes', 'Espèces à la livraison'

    class Statut(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        VALIDE = 'valide', 'Validé'
        ECHOUE = 'echoue', 'Échoué'

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='paiement')
    methode = models.CharField(max_length=20, choices=Methode.choices)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    reference = models.CharField(max_length=50, blank=True, verbose_name="Référence de transaction")
    date_paiement = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Paiement #{self.id} - {self.get_statut_display()}"