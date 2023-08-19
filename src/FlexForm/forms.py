from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from EventAPI import models as EventModel

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
        check_duplicate_field_name = FlexFormField.objects.filter(
            Q(form=form_id) & Q(name=name))
        if check_duplicate_field_name:
            raise ValidationError(_(mark_safe('<li>字段名称不可重复</li>')),
                                  code='duplicated field name')


class AttachInfoCollectionForm(forms.ModelForm):
    class Meta:
        model = EventModel.EventAttendentInfoForm
        fields = '__all__'
        widgets = {
            'form': forms.HiddenInput,
        }
        help_texts = {
            'event': _("绑定后，用户将会在确认报名时填写该表的信息"),
        }

    def clean(self):
        super().clean()
        event = self.cleaned_data.get('event')
        form = self.cleaned_data.get('form')
        check_duplicate_config = EventModel.EventAttendentInfoForm.objects.filter(
            Q(event=event) & Q(form=form))
        if check_duplicate_config:
            raise ValidationError(_(mark_safe('<li>此表单已与你选择的活动绑定</li>')),
                                  code='duplicated Flex Form Config')


class UserWriteInForm(forms.ModelForm):
    class Meta:
        model = FlexFormData
        fields = '__all__'
