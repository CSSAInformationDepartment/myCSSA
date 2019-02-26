from UserAuthAPI.models import User, UserProfile
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