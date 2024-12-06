from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MensajeForm(forms.Form):
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}))

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
