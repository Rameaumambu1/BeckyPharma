import random
from django.db import models

# --- Catégories ---
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# --- Produit ---
class Produit(models.Model):
    nom = models.CharField(max_length=100)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)  # Champ facultatif

    def __str__(self):
        return self.nom


# --- Employé (vendeur) ---
class Employe(models.Model):
    code = models.CharField(max_length=10, unique=True, editable=False)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                random_number = random.randint(1000, 9999)
                generated_code = f"EMP-{random_number}"
                if not Employe.objects.filter(code=generated_code).exists():
                    self.code = generated_code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom} : ({self.code})"

# --- Vente ---
class Vente(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='ventes')
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='ventes')
    quantite = models.PositiveIntegerField()
    date_vente = models.DateTimeField(auto_now_add=True)

    def montant_total(self):
        return self.quantite * self.produit.prix_unitaire

    def __str__(self):
        return f"Vente de {self.produit.nom} le {self.date_vente.date()}"

# --- Achat (réapprovisionnement) ---
class Achat(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='achats')
    quantite = models.PositiveIntegerField()
    prix_achat_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    date_achat = models.DateTimeField(auto_now_add=True)
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='achats')

    def montant_total(self):
        return self.quantite * self.prix_achat_unitaire

    def __str__(self):
        return f"Achat de {self.produit.nom} ({self.quantite}) le {self.date_achat.date()}"
