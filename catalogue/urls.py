from django.urls import path
from . import views

urlpatterns = [
    path('produits/', views.liste_produits, name='liste_produits'),
    path('points-distribution/', views.liste_points_distribution, name='liste_points_distribution'),

    path('gerant/stock/', views.gerer_stock, name='gerer_stock'),
    path('gerant/stock/<int:produit_id>/', views.modifier_stock, name='modifier_stock'),
    path('gerant/approvisionnements/', views.gerer_approvisionnements, name='gerer_approvisionnements'),
    path('gerant/alertes-stock/', views.alertes_stock, name='alertes_stock'),
    path('gerant/previsions/', views.previsions_demande, name='previsions_demande'),
    path('gerant/avis/', views.gerer_avis, name='gerer_avis'),
    path('produits/<int:produit_id>/avis/', views.laisser_avis, name='laisser_avis'),
]