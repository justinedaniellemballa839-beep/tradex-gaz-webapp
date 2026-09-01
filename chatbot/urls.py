from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('reinitialiser/', views.reinitialiser_chat, name='reinitialiser_chat'),
]