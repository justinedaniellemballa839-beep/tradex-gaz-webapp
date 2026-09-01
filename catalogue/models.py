from django.db import models
from django.conf import settings


class ProduitGaz(models.Model):
    """
    Une bouteille de gaz proposée à la vente.
    Correspond au cas d'utilisation "consulter produit de gaz".
    """
    nom = models.CharField(max_length=100, verbose_name="Nom")
    poids_kg = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Poids (kg)")
    prix = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Prix (FCFA)")
    description = models.TextField(blank=True, verbose_name="Description")
    stock_disponible = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    image = models.ImageField(upload_to='produits/', blank=True, null=True, verbose_name="Image")
    actif = models.BooleanField(default=True, verbose_name="Actif (visible sur le site)")

    def __str__(self):
        return f"{self.nom} ({self.poids_kg} kg)"

    class Meta:
        verbose_name = "Produit de gaz"
        verbose_name_plural = "Produits de gaz"


class PointDistribution(models.Model):
    """
    Un point physique où le gaz est disponible/livré.
    Correspond au cas d'utilisation "rechercher les points de distribution".
    """
    nom = models.CharField(max_length=150, verbose_name="Nom")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    quartier = models.CharField(max_length=100, blank=True, verbose_name="Quartier")
    adresse = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    actif = models.BooleanField(default=True, verbose_name="Actif")

    def __str__(self):
        return f"{self.nom} - {self.ville}"

    class Meta:
        verbose_name = "Point de distribution"
        verbose_name_plural = "Points de distribution"


class Avis(models.Model):
    """
    Un avis laissé par un client sur un produit.
    Cas d'utilisation : le client le crée (Phase 3/4),
    le gérant de station le consulte/modère (Phase 5).
    """
    produit = models.ForeignKey(ProduitGaz, on_delete=models.CASCADE, related_name='avis')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.PositiveSmallIntegerField(verbose_name="Note (1 à 5)")
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(default=True, verbose_name="Approuvé (visible publiquement)")

    def __str__(self):
        return f"Avis de {self.client.username} sur {self.produit.nom} ({self.note}/5)"

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-date_creation']
class Approvisionnement(models.Model):
    """
    Un réapprovisionnement de stock effectué par le gérant de station.
    Cas d'utilisation : "gérer approvisionnements".
    Chaque approvisionnement validé augmente le stock du produit concerné.
    """
    produit = models.ForeignKey(ProduitGaz, on_delete=models.CASCADE, related_name='approvisionnements')
    quantite = models.PositiveIntegerField(verbose_name="Quantité ajoutée")
    fournisseur = models.CharField(max_length=150, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    gerant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"+{self.quantite} {self.produit.nom} ({self.date_creation:%d/%m/%Y})"

    class Meta:
        verbose_name = "Approvisionnement"
        verbose_name_plural = "Approvisionnements"
        ordering = ['-date_creation']