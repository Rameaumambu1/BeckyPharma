from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.contrib.auth import logout
from .models import Vente, Achat

from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from .models import Employe
from .forms import EmployeForm  # à créer ci-dessous
from django.contrib import messages
from django.contrib.auth.models import User

import locale



def connexion_chef(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # redirige vers le tableau de bord (à adapter)
        else:
            messages.error(request, 'Nom d’utilisateur ou mot de passe incorrect.')
    
    return render(request, 'connexion_chef.html')





from datetime import datetime, timedelta
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Vente, Achat
from dateutil.relativedelta import relativedelta

def get_day_range(date):
    start = make_aware(datetime.combine(date, datetime.min.time()))
    end = make_aware(datetime.combine(date, datetime.max.time()))
    return (start, end)

def calculer_total(ventes_queryset):
    montant_total_expr = ExpressionWrapper(
        F('quantite') * F('produit__prix_unitaire'),
        output_field=DecimalField()
    )
    total = ventes_queryset.annotate(montant=montant_total_expr).aggregate(total=Sum('montant'))['total']
    return total or 0





def get_day_range(date):
    start = make_aware(datetime.combine(date, datetime.min.time()))
    end = make_aware(datetime.combine(date, datetime.max.time()))
    return (start, end)

def calculer_total_ventes(ventes_queryset):
    montant_total_expr = ExpressionWrapper(
        F('quantite') * F('produit__prix_unitaire'),
        output_field=DecimalField()
    )
    total = ventes_queryset.annotate(montant=montant_total_expr).aggregate(total=Sum('montant'))['total']
    return total or 0

def calculer_total_achats(achats_queryset):
    montant_total_expr = ExpressionWrapper(
        F('quantite') * F('prix_achat_unitaire'),
        output_field=DecimalField()
    )
    total = achats_queryset.annotate(montant=montant_total_expr).aggregate(total=Sum('montant'))['total']
    return total or 0

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux/mac
locale.setlocale(locale.LC_TIME, 'fr_FR')      # Windows

@login_required(login_url='connexion_chef')
def dashboard(request):
    utilisateur = request.user

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    before_yesterday = today - timedelta(days=2)

    # Filtrage ventes et achats par date
    ventes_today = Vente.objects.filter(date_vente__range=get_day_range(today))
    achats_today = Achat.objects.filter(date_achat__range=get_day_range(today))

    ventes_yesterday = Vente.objects.filter(date_vente__range=get_day_range(yesterday))
    achats_yesterday = Achat.objects.filter(date_achat__range=get_day_range(yesterday))

    ventes_2days = Vente.objects.filter(date_vente__range=get_day_range(before_yesterday))
    achats_2days = Achat.objects.filter(date_achat__range=get_day_range(before_yesterday))

    # Calculs totaux
    total_today = calculer_total_ventes(ventes_today)
    total_yesterday = calculer_total_ventes(ventes_yesterday)
    total_2days = calculer_total_ventes(ventes_2days)

    total_achats_today = calculer_total_achats(achats_today)
    total_achats_yesterday = calculer_total_achats(achats_yesterday)
    total_achats_2days = calculer_total_achats(achats_2days)

    # Calcul bénéfices
    benefice_today = total_today - total_achats_today
    benefice_yesterday = total_yesterday - total_achats_yesterday
    benefice_2days = total_2days - total_achats_2days

    # Historique des 10 derniers mois
    dix_derniers_mois = []
    mois_actuel = today.replace(day=1)

    for i in range(10):
        mois = mois_actuel - relativedelta(months=i)
        debut = make_aware(datetime.combine(mois, datetime.min.time()))
        fin_mois = (mois + relativedelta(months=1)) - timedelta(days=1)
        fin = make_aware(datetime.combine(fin_mois, datetime.max.time()))

        ventes_mois = Vente.objects.filter(date_vente__range=(debut, fin))
        achats_mois = Achat.objects.filter(date_achat__range=(debut, fin))

        total_ventes = calculer_total_ventes(ventes_mois)
        total_achats = calculer_total_achats(achats_mois)
        benefice_mois = total_ventes - total_achats

        dix_derniers_mois.append({
            'mois': mois.strftime("%B %Y"),
            'total': total_ventes,
            'total_achats': total_achats,
            'benefice': benefice_mois,
        })

    return render(request, 'dashboard.html', {
        'utilisateur': utilisateur,
        'ventes_today': ventes_today,
        'achats_today': achats_today,
        'ventes_yesterday': ventes_yesterday,
        'achats_yesterday': achats_yesterday,
        'ventes_2days': ventes_2days,
        'achats_2days': achats_2days,
        'total_today': total_today,
        'total_yesterday': total_yesterday,
        'total_2days': total_2days,
        'total_achats_today': total_achats_today,
        'total_achats_yesterday': total_achats_yesterday,
        'total_achats_2days': total_achats_2days,
        'benefice_today': benefice_today,
        'benefice_yesterday': benefice_yesterday,
        'benefice_2days': benefice_2days,
        'dix_derniers_mois': dix_derniers_mois,
    })





def deconnexion(request):
    logout(request)
    return redirect('connexion_chef')  # Redirige vers la page de connexion



@login_required(login_url='connexion_chef') 
def employes(request):
    utilisateur = request.user
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employes')
    else:
        form = EmployeForm()

    tous_les_employes = Employe.objects.all().order_by('-id')
    return render(request, 'employes.html', {'form': form, 'employes': tous_les_employes, 'utilisateur': utilisateur})



from django.shortcuts import get_object_or_404

def supprimer_employe(request, id):
    employe = get_object_or_404(Employe, id=id)
    employe.delete()
    messages.success(request, "Employé supprimé avec succès.")

    return redirect('employes')
