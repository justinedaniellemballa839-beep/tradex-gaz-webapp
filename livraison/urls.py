from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_livraisons, name='liste_livraisons'),
    path('attribuer/', views.attribuer_livraisons, name='attribuer_livraisons'),
    path('demandes/', views.mes_demandes, name='mes_demandes'),
    path('<int:livraison_id>/accepter/', views.accepter_livraison, name='accepter_livraison'),
    path('<int:livraison_id>/refuser/', views.refuser_livraison, name='refuser_livraison'),
    path('<int:livraison_id>/position/', views.mettre_a_jour_position, name='mettre_a_jour_position'),
    path('<int:livraison_id>/confirmer/', views.confirmer_livraison, name='confirmer_livraison'),
    path('suivi/<int:commande_id>/', views.suivre_livraison, name='suivre_livraison'),
    path('suivi-position/<int:livraison_id>/', views.position_actuelle, name='position_actuelle'),
    path('<int:livraison_id>/', views.detail_livraison, name='detail_livraison'),
]