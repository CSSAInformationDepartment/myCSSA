

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

############################  WARNING !!! #####################################
#                                                                             #
#    This part of code relates to the proprietary security features of        #
#                        myCSSA Account System                                #
#                                                                             #
#                                                                             #
#                          DO NOT DISCLOSE!                                   #
###############################################################################

import random
import string
import re

from rest_framework import serializers, exceptions
from rest_auth.serializers import LoginSerializer
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.models import TokenModel
from rest_auth.utils import import_callable
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from allauth.account.adapter import DefaultAccountAdapter

from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from UserAuthAPI import models
from django.conf import settings
from django.http import HttpRequest

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

UserModel = get_user_model()

def getRandomStringSubFix():
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    return salt


class APILoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        elif username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs

# This enalbes the fundamental registration
class AcccountInitRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    #firstNameEN = serializers.CharField(required=True, write_only=True)
    #lastNameEN = serializers.CharField(required=True, write_only=True)
    telNumber = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("Occupied E-mail Address."))
        return email

    def validate_telNumber(self,telNumber):
        #telNumber = get_adapter().get_user_search_fields("telNumber")
        telNumberChecker = models.User.objects.filter(telNumber=telNumber)
        if telNumberChecker.exists():
            raise serializers.ValidationError(
                _("Occupied Phone Number"))
        else:
            pass

        return telNumber

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
    #        'first_name': self.validated_data.get('first_name', ''),
    #        'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'telNumber': self.validated_data.get('telNumber',''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.username = self.cleaned_data['email'].split('@')[0] + getRandomStringSubFix()
        user.telNumber = self.cleaned_data['telNumber']
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
#       user.profile.save()
        return user


class UserDetailSerializer(serializers.Serializer):
    class Meta:
        model = models.User
        fields = ('id','firstNameEN','lastNameEN', 'gender',
        'dateOfBirth', 'studentId','address', 'postcode', 'originate')

        read_only_fields = ('id', )

    def update(self, validated_data, instance):

        return instance()

class UserEasyRegistrationSerializer(serializers.Serializer):
    genderChoice = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )

    degreeChoice = (
        ('CR', 'Certificate'),
        ('DP', 'Diploma'),
        ('FN', 'Foundation'),
        ('BA', 'Bachelor'),
        ('MA', 'Master'),
        ('JD', 'Jurum Doctor'),
        ('MD', 'Medical Doctor'),
        ('PhD', 'Doctor of Philosophy'),
    )

    email = serializers.EmailField(required=True)
    telNumber = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    firstNameEN = serializers.CharField(required=True)
    lastNameEN = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=genderChoice, required=True)
    dateOfBirth = serializers.DateField(required=True)
    studentId = serializers.CharField(required=True, max_length=8)
    degree = serializers.ChoiceField(choices=degreeChoice, required=True)
    uniMajor = serializers.CharField(max_length=100, required=True)

    def validate_telNumber(self, value):
        data_telNumber = value
        if (not(data_telNumber[0:2] == '04' or data_telNumber[0:4] == '+861' or \
                data_telNumber[0:4] == '0861' or data_telNumber[0:3] == '861') 
            or (data_telNumber[0:2] == '04' and len(data_telNumber) != 10)\
            or (data_telNumber[0:4] == '+861' and len(data_telNumber) != 14)\
            or (data_telNumber[0:4] == '0861' and len(data_telNumber) != 14)\
            or (data_telNumber[0:4] == '861' and len(data_telNumber) != 13)):
                raise serializers.ValidationError(_("Invalid Mobile Phone Number"))
        
        userQuery = models.User.objects.filter(telNumber=value).first()
        if userQuery is not None:
            raise serializers.ValidationError(_("The contact number has been occupied by exisiting account. Contact support for further information."))
        
        return value

    def validate_email(self, value):
        # regex extracted from https://emailregex.com/
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if(not re.search(regex, value)): 
            raise serializers.ValidationError(_('Invalid email Address'))

        userQuery = models.User.objects.filter(email=value).first()
        if userQuery is not None:
            raise serializers.ValidationError(_("The email address has been occupied by exisiting account. Contact support for further information."))

        return value

    def validate_studentId(self, value):
        if not(len(value) >= 6 and len(value) <= 8):
            raise serializers.ValidationError(_('Invalid student ID'))
        
        userQuery = models.UserProfile.objects.filter(studentId=value).first()
        if userQuery is not None:
            raise serializers.ValidationError(_("The student ID has been occupied by exisiting account. Contact support for further information."))

        return value

    def create(self,validated_data):
        if validated_data.get('telNumber').startswith('0861'):
            validated_data['telNumber'] = '+' + validated_data['telNumber'][1:]
        elif validated_data.get('telNumber').startswith('861'):
            validated_data['telNumber'] = '+' + validated_data['telNumber']

        new_user = models.User.objects.create_user(
            validated_data.get('email'),
            validated_data.get('telNumber'),
            validated_data.get('password')
        )
        
        profile = models.UserProfile.objects.create(
            user = new_user,
            identiyConfirmed = False,
            isValid = False,
            firstNameEN = validated_data.get('firstNameEN'),
            lastNameEN = validated_data.get('lastNameEN'),
            studentId = validated_data.get('studentId'),
            dateOfBirth = validated_data.get('dateOfBirth')
        )

        models.UserAcademic.objects.create(
            userProfile = profile,
            degree = validated_data.get('degree'),
            uniMajor = validated_data.get('uniMajor') 
        )

        return new_user



