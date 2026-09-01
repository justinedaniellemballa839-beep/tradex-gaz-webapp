from django.contrib import admin
from .models import Livraison


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('commande', 'livreur', 'statut', 'date_prise_en_charge', 'date_livraison')
    list_filter = ('statut',)