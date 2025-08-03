from django.urls import path, include
from . import views
# suivi/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProduitViewSet, VenteViewSet, AchatViewSet, EmployeViewSet

router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'ventes', VenteViewSet)
router.register(r'achats', AchatViewSet)
router.register(r'employes', EmployeViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    
    path('', views.index, name='accueil'),

    path('login/', views.login_employe, name='login_employe'),
    path('logout/', views.logout_employe, name='logout_employe'),
    # autres routes
    path('valider-commande/', views.valider_commande, name='valider_commande'),
    path('connexion/', views.login_employe, name='login_employe'),

    path('produits/', views.produits_view, name='produits'),

    path('produits/restocker/', views.restocker_produit, name='restocker_produit'),
    path('produits/supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
]
