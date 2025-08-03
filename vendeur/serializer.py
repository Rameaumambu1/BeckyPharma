# vendeur/serializer.py
from rest_framework import serializers
from .models import Produit, Vente, Achat, Employe

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

class VenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vente
        fields = '__all__'

class AchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achat
        fields = '__all__'

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ['id', 'nom', 'prenom', 'code']
