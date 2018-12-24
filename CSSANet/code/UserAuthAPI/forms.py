###############################################################################
#                    Desinged & Managed by Josh.Le.LU                         #
#                                                                             #
#                     █████╗ ██╗     ██╗ ██████╗███████╗                      #
#                    ██╔══██╗██║     ██║██╔════╝██╔════╝                      #
#                    ███████║██║     ██║██║     █████╗                        #
#                    ██╔══██║██║     ██║██║     ██╔══╝                        #
#                    ██║  ██║███████╗██║╚██████╗███████╗                      #
#                    ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝                      #
#        An agile web application platform bulit on top of Python/django      #
#                                                                             #
#                Proprietary version made for myCSSA project                  #
#                             Version: 0.6a(C)                                #
#                                                                             #
###############################################################################
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from UserAuthAPI import models
import re


class BasicSiginInForm(forms.Form):

    email = forms.CharField()
    telNumber = forms.CharField()
    password = forms.CharField(widget= forms.PasswordInput())
    confirmPassword = forms.PasswordInput(attrs={'class':''})


    def checkEmail(self):
        data_email = self.cleaned_data['email']
        # print(email)
        userQuery = models.User.objects.filter(email=data_email).first()

        if userQuery is None:
            # 长度小于100
            if len(data_email) > 100:
                raise ValidationError(_('邮箱长度过长'))
            # 验证邮箱输入格式
            regex_email = re.compile(
                r'(^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$)')
            if not regex_email.match(data_email):
                raise ValidationError(_('非法的邮箱名'))
        else:
            raise ValidationError(_('邮箱已被占用'))
        # Remember to always return the cleaned data.
        return data_email

    # 电话号码的验证
    def checkTelNumber(self):
        data_telNumber = self.cleaned_data['telNumber']
        # 对于澳洲号码的验证
        if data_telNumber[0:2] == '04':
            if len(data_telNumber) != 10:
                raise ValidationError(_('无效的电话号码'))
        # 对于中国号码的验证
        elif data_telNumber[0:5] == '+861':
            if len(data_telNumber) != 14:
                raise ValidationError(_('无效的电话号码'))
        else:
            raise ValidationError(_('无效的电话号码'))
        return data_telNumber
    
    def passwordIntegrityCheck(self):
        return None
        

class UserInfoForm(forms.ModelForm):
    avatar = forms.FileField()
    inforcardBg = forms.FileField()
    
    class Meta:
        model = models.UserProfile
        fields = '__all__'