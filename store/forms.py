from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import *
from orders.models import *


class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, label="Ваше ім'я")
    message = forms.CharField(widget=forms.Textarea, label="Повідомлення")


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomPasswordChangeForm(PasswordChangeForm):
    pass

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Выберите CSV-файл')
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    class Media:
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'https://code.jquery.com/ui/1.12.1/jquery-ui.min.js',
        )
        css = {
            'all': (
                'https://code.jquery.com/ui/1.12.1/themes/smoothness/jquery-ui.css',
            )
        }
    