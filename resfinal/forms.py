from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model 


class RegisterForm(UserCreationForm):
    email=forms.CharField(widget=forms.EmailInput(attrs={"placeholder": "Enter email-address", "class": "form-control"}))
    username=forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Enter email-username", "class": "form-control"}))
    password1=forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Enter password", "class": "form-control"}))
    password2=forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"placeholder": "Confirm password", "class": "form-control"}))
    
    class Meta:
        model = get_user_model()
        fields = ["email", "username", "password1", "password2"]


class UpdateProfileForm(forms.ModelForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={"placeholder": "Enter email-address", "class": "form-control"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Enter username", "class": "form-control"}))

    class Meta:
        model = get_user_model()
        fields = ["email", "username"]

# forms.py

from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    date_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    class Meta:
        model = Booking
        fields = ['username', 'total_members', 'date_time']
