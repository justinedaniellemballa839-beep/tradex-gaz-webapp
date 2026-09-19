from django.urls import path
from . import views

urlpatterns = [
    path('liste.json', views.liste_json, name='notifications_liste_json'),
    path('<int:notification_id>/lue/', views.marquer_lue, name='notification_marquer_lue'),
    path('toutes-lues/', views.marquer_toutes_lues, name='notifications_toutes_lues'),
]
