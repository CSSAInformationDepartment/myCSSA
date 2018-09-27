from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import UserProfile

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserProfile
        fields = ("username", "email")