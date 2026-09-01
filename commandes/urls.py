from django.urls import path
from . import views

urlpatterns = [
    path('nouvelle/', views.passer_commande, name='passer_commande'),
    path('<int:commande_id>/paiement/', views.effectuer_paiement, name='effectuer_paiement'),
    path('<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('', views.historique_commandes, name='historique_commandes'),
]