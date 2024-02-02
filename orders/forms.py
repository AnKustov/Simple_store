from django import forms
from .models import *


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'phone_number', 'city', 'delivery']

    widgets = {
        'delivery': forms.TextInput(attrs={'class': 'form-control'}),
    }