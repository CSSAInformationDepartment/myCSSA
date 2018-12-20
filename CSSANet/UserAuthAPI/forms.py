from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re


class ValidationForm(forms.Form):

    email = forms.CharField()

    def checkEmail(self):
        data_email = self.cleaned_data['email']

        # 长度小于100
        if len(data_email) > 100:
            raise ValidationError(_('邮箱长度过长'))

        # 验证邮箱输入格式
        regex_email = re.compile(r'(^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$)')
        if not regex_email.match(data_email):
            raise ValidationError(_('非法的邮箱名'))
        
        # Remember to always return the cleaned data.
        return data
