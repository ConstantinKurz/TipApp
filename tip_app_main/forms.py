from django import forms
from django.template.defaultfilters import default
from .models import Tip

class ContactForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)
