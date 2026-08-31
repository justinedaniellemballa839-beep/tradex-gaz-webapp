from django.contrib import admin
from .models import ProduitGaz, PointDistribution


@admin.register(ProduitGaz)
class ProduitGazAdmin(admin.ModelAdmin):
    list_display = ('nom', 'poids_kg', 'prix', 'stock_disponible', 'actif')
    list_filter = ('actif',)


@admin.register(PointDistribution)
class PointDistributionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'quartier', 'telephone', 'actif')
    list_filter = ('ville', 'actif')