from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Categorie, Produit, Employe, Vente, Achat

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'categorie', 'prix_unitaire', 'quantite_stock', 'description')
    list_filter = ('categorie',)
    search_fields = ('nom', 'description')

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('id', 'prenom', 'nom', 'telephone', 'code')
    search_fields = ('prenom', 'nom', 'code')

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit', 'employe', 'quantite', 'date_vente', 'montant_total')
    list_filter = ('date_vente', 'employe', 'produit')
    date_hierarchy = 'date_vente'
    search_fields = ('produit__nom', 'employe__prenom', 'employe__nom', 'employe__code')

@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ('id', 'produit', 'employe', 'quantite', 'prix_achat_unitaire', 'date_achat', 'montant_total')
    list_filter = ('date_achat', 'employe', 'produit')
    date_hierarchy = 'date_achat'
    search_fields = ('produit__nom', 'employe__prenom', 'employe__nom', 'employe__code')
