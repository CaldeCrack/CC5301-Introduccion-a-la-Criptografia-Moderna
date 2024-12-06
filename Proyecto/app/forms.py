from django import forms

class MensajeForm(forms.Form):
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}))
