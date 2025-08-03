

from django.forms import DecimalField
from suivi.models import Achat, Produit, Categorie
# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required  # si tu veux restreindre

from suivi.models import Produit, Vente, Employe  # adapte selon ton modèle



from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from suivi.models import Employe
from .forms import LoginForm

from django.utils import timezone
import json


# views.py

def login_employe(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                employe = Employe.objects.get(code=code)
                # Connexion réussie : on peut sauvegarder l'employé dans la session
                request.session['employe_id'] = employe.id
                messages.success(request, f"Bienvenue {employe.prenom} !")
                return redirect('accueil')  # Redirige vers l'interface principale
            except Employe.DoesNotExist:
                form.add_error('code', "Code employé invalide.")
    else:
        form = LoginForm()

    return render(request, 'connexion.html', {'form': form})


def index(request):
    if not request.session.get('employe_id'):
        return redirect('login_employe')

    employe_id = request.session.get('employe_id')
    employe = Employe.objects.get(id=employe_id) # ← On récupère l'objet complet

    produits = Produit.objects.all().select_related('categorie')
    categories = Categorie.objects.all()

    return render(request, 'index.html', {
        'employe': employe,
        'produits': produits,
        'categories': categories
    })

# Tu peux créer un décorateur simple pour protéger tes vues qui nécessitent un employé connecté.




def employe_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'employe_id' not in request.session:
            return redirect('login_employe')
        return view_func(request, *args, **kwargs)
    return wrapper




@csrf_exempt
def valider_commande(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            panier = data.get('panier', [])
            employe_id = request.session.get('employe_id')  # récupère l'ID de l'employé connecté

            if not panier:
                return JsonResponse({'success': False, 'error': 'Le panier est vide.'})

            if not employe_id:
                return JsonResponse({'success': False, 'error': 'Employé non identifié.'})

            employe = Employe.objects.get(id=employe_id)
            stocks = {}

            for item in panier:
                produit_id = item['id'].replace("prod-", "")
                quantite = int(item['quantite'])
                produit = Produit.objects.get(id=produit_id)

                if quantite > produit.quantite_stock:
                    return JsonResponse({'success': False, 'error': f'Stock insuffisant pour {produit.nom}.'})

                # Crée la vente
                Vente.objects.create(
                    produit=produit,
                    employe=employe,
                    quantite=quantite,
                    date_vente=timezone.now()
                )

                # Met à jour le stock
                produit.quantite_stock -= quantite
                produit.save()

                stocks[produit_id] = produit.quantite_stock

            return JsonResponse({'success': True, 'stocks': stocks})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})






def produits_view(request):
    if not request.session.get('employe_id'):
        return redirect('login_employe')

    employe_id = request.session.get('employe_id')
    employe = Employe.objects.get(id=employe_id) # ← On récupère l'objet complet

    if request.method == "POST":
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        prix_unitaire = request.POST.get('prix_unitaire')
        quantite_stock = request.POST.get('quantite_stock')
        pris_achat = request.POST.get('pris_achat')
        try:
            pris_achat = float(pris_achat)
            if pris_achat < 1:
                messages.error(request, "Le prix d'achat doit être un nombre positif.")
                return redirect('produits')
        except:
            messages.error(request, "Prix d'achat invalide.")
            return redirect('produits')


        

        # Validation simple
        if not nom or not prix_unitaire or not quantite_stock:
            messages.error(request, "Merci de remplir tous les champs obligatoires.")
        else:
            try:
                prix_unitaire = float(prix_unitaire)
                quantite_stock = int(quantite_stock)

                # Chercher produit existant par nom (insensible à la casse)
                produit_exist = Produit.objects.filter(nom__iexact=nom).first()

                if produit_exist:
                    # Afficher un message lorsque le produit existe déjà
                    messages.warning(request, f"'{nom}' existe déjà. Veuillez le réapprovisionner via le bouton approprié.")
                    return redirect('produits')

                else:
                    # Création nouveau produit
                    produit = Produit(
                        nom=nom,
                        description=description,
                        prix_unitaire=prix_unitaire,
                        quantite_stock=quantite_stock
                    )
                    produit.save()

                    # Création d’un enregistrement dans Achat
                    Achat.objects.create(
                        produit=produit,
                        quantite=quantite_stock,
                        prix_achat_unitaire=pris_achat,
                        employe=Employe.objects.get(id=request.session['employe_id'])
                    )
                    messages.success(request, f"'{nom}' ajouté avec succès.")

                return redirect('produits')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout : {e}")

    produits = Produit.objects.all()
    return render(request, 'produits.html', {'produits': produits})



def restocker_produit(request):
    if request.method == "POST":
        produit_id = request.POST.get('produit_id')
        quantite = request.POST.get('quantite')
        prix_achat_produit = request.POST.get('prix_achat_produit')
        try:
            prix_achat_produit = float(prix_achat_produit)
            quantite = int(quantite)
            if prix_achat_produit < 1:
                messages.error(request, "Le prix doit être un nombre positif.")
                return redirect('produits')
            if quantite < 1:
                messages.error(request, "La quantité doit être positive.")
                return redirect('produits')
        except:
            messages.error(request, "Valeurs invalides.")
            return redirect('produits')


        produit = get_object_or_404(Produit, id=produit_id)
        produit.quantite_stock += quantite
        produit.save()


        # Créer l'achat
        
        
        montant = prix_achat_produit * quantite
        Achat.objects.create(
            produit=produit,
            quantite=quantite,
            prix_achat_unitaire=prix_achat_produit,
            employe=Employe.objects.get(id=request.session['employe_id'])
        )
        messages.success(request, f"'{produit.nom}' a été réapprovisionné avec succès. {montant} FC")
    return redirect('produits')

def supprimer_produit(request, produit_id):
    if request.method == "POST":
        produit = get_object_or_404(Produit, id=produit_id)
        produit.delete()
        messages.success(request, f"'{produit.nom}' a été supprimé.")
    return redirect('produits')




def logout_employe(request):
    request.session.flush()  # supprime toute la session
    return redirect('login_employe')




# APIRest


from rest_framework import viewsets
# from su.models import Produit, Vente, Achat, Employe
from suivi.serializer import ProduitSerializer, VenteSerializer, AchatSerializer, EmployeSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class VenteViewSet(viewsets.ModelViewSet):
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer

class AchatViewSet(viewsets.ModelViewSet):
    queryset = Achat.objects.all()
    serializer_class = AchatSerializer

class EmployeViewSet(viewsets.ReadOnlyModelViewSet):  # en lecture seule
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
