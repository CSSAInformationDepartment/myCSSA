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
import base64
import os

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _

from UserAuthAPI import models


def get_file_extension(file):
    name, extension = os.path.splitext(file.name)
    if extension == '.png':
        return 'png'
    return 'jpeg'

# 电话号码的验证


def CheckTelNumber(value):
    data_telNumber = value
    # 对于澳洲号码的验证
    if data_telNumber[0:2] == '04':
        if len(data_telNumber) != 10:
            raise ValidationError(_("Invalid Mobile Phone Number"))
    # 对于中国号码的验证
    elif data_telNumber[0:3] == '+861':
        if len(data_telNumber) != 14:
            raise ValidationError(_('Invalid Mobile Phone Number'))
    else:
        raise ValidationError(_('Invalid Mobile Phone Number'))


class BasicSiginInForm(forms.ModelForm):
    email = forms.EmailField()
    telNumber = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirmPassword = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm ')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(
                    "The two password fields must match.")
        return password_confirm

    def save(self, commit=True):
        user = super(BasicSiginInForm, self).save(commit=False)
        user.email = user.email.lower()
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = models.User
        fields = ('email', 'telNumber', 'password')


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = '__all__'


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ('firstNameEN', 'lastNameEN', 'firstNameCN',
                  'lastNameCN', 'address', 'postcode')


class UserAvatarUpdateForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    cropped_b64 = forms.CharField()

    class Meta:
        model = models.UserProfile
        fields = ('avatar',)

    def save(self):
        form = super().save(commit=False)

        self.cleaned_data.get('x')
        self.cleaned_data.get('y')
        self.cleaned_data.get('width')
        self.cleaned_data.get('height')
        img_b64 = self.cleaned_data.get('cropped_b64')

        format, imgstr = img_b64.split(';base64,')
        ext = format.split('/')[-1]

        # Patch to avoid incorrect padding caused by some browsers
        missing_padding = len(imgstr) % 4
        if missing_padding:
            imgstr += b'=' * (4 - missing_padding)

        decoded_file = ContentFile(
            base64.b64decode(imgstr), name='avatar_lg.' + ext)
        form.avatar = decoded_file

        super().save()
        return form


class UserAcademicForm(forms.ModelForm):
    class Meta:
        model = models.UserAcademic
        fields = ('userProfile', 'degree', 'uniMajor')


class MigrationForm(forms.Form):
    membershipId = forms.CharField(required=False)
    studentId = forms.CharField(required=False)
    dateOfBirth = forms.DateField(required=False)
    telNumber = forms.CharField(required=False)
    email = forms.EmailField(required=False)


class EasyRegistrationForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ('gender', 'dateOfBirth', 'studentId', 'firstNameEN',
                  'lastNameEN', 'studentId', 'membershipId')
