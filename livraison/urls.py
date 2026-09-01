from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_livraisons, name='liste_livraisons'),
    path('<int:livraison_id>/prendre/', views.prendre_en_charge, name='prendre_en_charge'),
    path('<int:livraison_id>/', views.detail_livraison, name='detail_livraison'),
    path('<int:livraison_id>/confirmer/', views.confirmer_livraison, name='confirmer_livraison'),
]