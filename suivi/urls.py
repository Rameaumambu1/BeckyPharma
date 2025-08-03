from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.connexion_chef, name='connexion_chef'),
    path('employes/', views.employes, name='employes'),
    path('logout/', views.deconnexion, name='logout'),
    path('', views.dashboard, name='dashboard'),  # si elle existe
    path('employes/supprimer/<int:id>/', views.supprimer_employe, name='supprimer_employe'),

]
