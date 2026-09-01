from django.contrib import admin
from .models import Commande, LigneCommande, Paiement


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 1


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'statut', 'date_creation', 'montant_total')
    list_filter = ('statut',)
    inlines = [LigneCommandeInline]


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('commande', 'methode', 'statut', 'date_paiement')
    list_filter = ('methode', 'statut')