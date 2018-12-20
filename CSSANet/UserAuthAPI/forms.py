from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class ValidationForm(forms.Form):
    
    email = forms.CharField()
    
    def checkEmail(self):
        
        

