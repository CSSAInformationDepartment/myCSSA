from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from UserAuthAPI import models
from django.utils.safestring import mark_safe
from django.db.models import Q
import re

from .models import *

class NewFlexForm(forms.ModelForm):
    class Meta:
        model = FlexForm
        fields = ('name',)

class AddFlexFormFieldForm(forms.ModelForm):

    class Meta:
        model = FlexFormField
        exclude = ('disabled',)
        help_texts = {
            'name': _("名称最大长度位100，不可重复"),
            'field_type': _("字段数据类型，分为文本(text)和数字(digit)"),
            'max_len': _("该字段允许输入的最大值，系统上限为2000"),

        }
        widgets = {
            'form': forms.HiddenInput,
        }

    def clean(self):
        super().clean()
        name = self.cleaned_data.get('name')
        form_id = self.cleaned_data.get('form')
        check_duplicate_field_name = FlexFormField.objects.filter(Q(form=form_id)&Q(name=name))
        if check_duplicate_field_name:
            raise ValidationError(_(mark_safe('<li>字段名称不可重复</li>')), 
            code='duplicated field name')
        
