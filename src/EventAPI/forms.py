from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from UserAuthAPI import models
from django.utils.safestring import mark_safe
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
            'DisplayArticleType': _("选择活动介绍所要显示的文章来源"),
            'relatedArticles': _("若文章来源选择为Blog，则此项必填"),
            'WechatArticleUrl': _("若文章来源选择为WeChat，则此项必填"),
            'WechatQRcode': _("若文章来源选择为WeChat，则必须提供文章对应的微信公众号"),

            'pastEventLink': _("可以为空"),
            'recentEventLink': _("可以为空"),
            'pastEventPoster': _("可以为空"),
            'recentEventPoster': _("可以为空"),
        }
        widgets = {
            'eventInfo': forms.Textarea(attrs={'rows': 3}),
            'eventSignUpTime': forms.TextInput(attrs={
                 'data-target': "#id_eventSignUpTime_picker",
            }),
            'eventActualStTime': forms.TextInput(attrs={
                 'data-target': "#id_eventActualStTime_picker",
            }),
        }

    def clean(self, *args, **kwargs):
        errors = []
        
        super().clean()
        wechat_article_url = self.cleaned_data.get('WechatArticleUrl')
        related_articles = self.cleaned_data.get('relatedArticles')
        display_article_type = self.cleaned_data.get('DisplayArticleType')
        wechat_qr_code = self.cleaned_data.get('WechatQRcode')

        if (display_article_type == 'WeChat' and (wechat_article_url == None or wechat_qr_code == None)) or (display_article_type == 'Blog' and related_articles == None):
            errors.append(ValidationError(_(mark_safe('<li>文章显示设置不正确，请检查相关设置项</li>')), code='invalid article display setting'))

        event_actualSt_time = self.cleaned_data.get("eventActualStTime")
        event_sign_up_time = self.cleaned_data.get("eventSignUpTime")
        if event_sign_up_time >= event_actualSt_time:
            errors.append(ValidationError(_(mark_safe('<li>报名开始时间不可晚于活动开始时间</li>')), code='late sign up time'))

        if errors:
            raise ValidationError(errors)


class AttendEventForm(forms.ModelForm):
    class Meta:
        model=AttendEvent
        fields = '__all__'
