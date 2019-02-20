from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from UserAuthAPI import models
import re

from .models import *

class AddEventForm(forms.ModelForm):
    eventInfo = forms.TextInput()
    class Meta:
        model = Event
        exclude = ('eventStartTime','disabled')
        help_texts = {
            'eventName': _("名称最大长度位50，不可重复"),
            'eventSignUpTime': _("活动开始接受报名的时间"),
            'eventActualStTime': _("活动实际开始的时间"),

        }
        widgets = {
            'eventInfo': forms.Textarea(attrs={'rows': 3}),
            'eventSignUpTime': forms.TextInput(attrs={
                 'data-target': "#id_eventSignUpTime_picker",
            }),
        }