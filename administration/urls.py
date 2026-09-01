from django.urls import path
from . import views

urlpatterns = [
    path('', views.tableau_de_bord, name='tableau_de_bord'),
    path('comptes/', views.gerer_comptes, name='gerer_comptes'),
    path('comptes/<int:utilisateur_id>/', views.modifier_compte, name='modifier_compte'),
    path('rapports/', views.rapports_globaux, name='rapports_globaux'),
    path('livraisons/', views.gerer_livraisons, name='gerer_livraisons'),
    path('livraisons/<int:livraison_id>/', views.modifier_statut_livraison, name='modifier_statut_livraison'),
]