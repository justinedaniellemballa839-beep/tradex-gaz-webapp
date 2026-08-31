from django.urls import path
from . import views

urlpatterns = [
    path('produits/', views.liste_produits, name='liste_produits'),
    path('points-distribution/', views.liste_points_distribution, name='liste_points_distribution'),
]