from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe


class CarouselInnerForm(forms.ModelForm):
    class Meta:
        model = HomepageCarousels
        fields = '__all__'

    def clean(self):
        super.clean()
        records = HomepageCarousels.objects.all().count()
        if records == 5:
            raise ValidationError(_(mark_safe('<li>已达到上传最大值</li>')), 
            code='Reach maximun submission')