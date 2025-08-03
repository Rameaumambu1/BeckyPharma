from django import forms
from .models import Employe





class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['prenom', 'nom', 'telephone']
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prenom'].label = 'Prénom'
        self.fields['prenom'].widget.attrs.update({'placeholder': "Entrez le prénom de l'employé", 'class': 'form-control', 'required': 'required', 'id': 'prenom'})
        
        self.fields['nom'].label = 'Nom'
        self.fields['nom'].widget.attrs.update({'placeholder': "Entrez le nom de l'employé", 'class': 'form-control', 'required': 'required', 'id': 'nom'})
        
        self.fields['telephone'].label = 'Téléphone'
        self.fields['telephone'].widget.attrs.update({'type': 'number', 'placeholder': "Ex : 0812345678", 'class': 'form-control', 'required': 'required', 'id': 'telephone'})
        