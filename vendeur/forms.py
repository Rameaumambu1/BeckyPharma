from django import forms

class LoginForm(forms.Form):
    code = forms.CharField(max_length=10, label="Code Employé")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].label = 'Code'
        self.fields['code'].widget.attrs.update({
            'type': 'text',
            'placeholder': "Ex : EMP-2025-001",
            'class': 'form-control',
            'required': 'required',
            'id': 'code'
        })
