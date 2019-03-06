from django import forms
from .models import *
class MerchantsForm(forms.ModelForm):

    class Meta:
        model = DiscountMerchant
        exclude = ('merchant_add_date',)