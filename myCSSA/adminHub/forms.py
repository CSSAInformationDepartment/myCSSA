from django import forms
#from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import UserProfile

class UserRegisterForm(forms.ModelForm):
##Form definition for UserRegister.

    class Meta:
        ##Meta definition for UserRegisterform.

        model = UserProfile
        fields = ['identiyConfirmed', 'isValid','avatar','infocardBg']
