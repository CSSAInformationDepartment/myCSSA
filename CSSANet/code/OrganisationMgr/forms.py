from UserAuthAPI.models import User, UserProfile, CSSACommitteProfile
from LegacyDataAPI.models import LegacyUsers

from django import forms
from django.forms import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _




class BindingMembershipCardForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ('user', 'membershipId')
        help_texts ={
            'membershipId': _("会员卡号最多10位"),
        }
        widgets = {
            'user': forms.HiddenInput,
        }

    def clean(self, *args, **kwargs):

        super().clean()
        membership_Id = self.cleaned_data.get('membershipId')

        prev_member = UserProfile.objects.filter(membershipId=membership_Id).first()
        legacy_member = LegacyUsers.objects.filter(membershipId=membership_Id).first()

        if prev_member or legacy_member:
            raise ValidationError(_(mark_safe('<li>该会员卡状态异常，请更换</li>')), code='abnormal card')


class UserProfileEditForm(forms.ModelForm):
    user = forms.CharField(disabled=True)
    class Meta:
        
        model = UserProfile
        exclude = ('avatar', 'infocardBg', 'identiyConfirmed', 'isValid', 'joinDate', 'dateOfBirth', 'membershipId')

    def clean(self, *args, **kwargs):
        super().clean()
        student_id = self.cleaned_data.get('studentId')
        user_id = self.cleaned_data.get('user')

        duplicated_student_id = UserProfile.objects.exclude(user__pk=user_id).filter(studentId=student_id).first()
        if duplicated_student_id:
            raise ValidationError(_(mark_safe('<li>该学生卡号已被占用</li>')), code='Duplicated Student Id')

class UserEditForm(forms.ModelForm):
    email = forms.CharField(disabled=True)

    class Meta:
        model = User
        fields = ('email','telNumber')

    def clean(self, *args, **kwargs):
        super().clean()
        email = self.cleaned_data.get('email')
        telNumber = self.cleaned_data.get('telNumber')

        duplicated_telNumber = User.objects.exclude(email=email).filter(telNumber=telNumber).first()
        if duplicated_telNumber:
            raise ValidationError(_(mark_safe('<li>该手机号已被他人注册</li>')), code='Duplicated tel number')

class AssignNewComitteeForm(forms.ModelForm):
    is_active = forms.BooleanField(initial=True, widget=forms.HiddenInput())
    class Meta:
        model = CSSACommitteProfile
        fields = ('member','Department','role','is_active',)
        widgets = {
            'member': forms.HiddenInput,
        }