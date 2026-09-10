from django.contrib import admin
from .models import Livraison


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('commande', 'livreur', 'statut', 'date_assignation', 'date_acceptation', 'date_livraison')
    list_filter = ('statut',)