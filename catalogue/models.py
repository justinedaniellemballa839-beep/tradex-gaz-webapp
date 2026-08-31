from django.db import models


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