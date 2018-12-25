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

# 电话号码的验证
def CheckTelNumber(value):
    data_telNumber = value
    # 对于澳洲号码的验证
    if data_telNumber[0:2] == '04':
        if len(data_telNumber) != 10:
            raise ValidationError(_("Invalid Mobile Phone Number"))
    # 对于中国号码的验证
    elif data_telNumber[0:5] == '+861':
        if len(data_telNumber) != 14:
            raise ValidationError(_('Invalid Mobile Phone Number'))
    else:
       raise ValidationError(_('Invalid Mobile Phone Number'))

class BasicSiginInForm(forms.ModelForm):
    email = forms.EmailField()
    telNumber = forms.CharField(validators=[CheckTelNumber])
    password = forms.CharField(widget= forms.PasswordInput())
    confirmPassword = forms.CharField(widget= forms.PasswordInput())

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm ')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("The two password fields must match.")
        return password_confirm

    def save(self, commit=True):
        user = super(BasicSiginInForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = models.User
        fields = ('email','telNumber','password')

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = '__all__'