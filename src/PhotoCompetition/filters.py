from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, filters

from . import models


class SubmissionFilter(FilterSet):
    SHORTLIST = (
        ('not-shortlisted', _("未入选")),
        ('shortlisted', _("已入选")),
    )
    first_name = filters.CharFilter(
        field_name='submissionUserId__firstNameEN', lookup_expr='istartswith', label=_("英文名"))
    last_name = filters.CharFilter(
        field_name='submissionUserId__lastNameEN', lookup_expr='istartswith', label=_("英文姓"))
    device_type = filters.ChoiceFilter(
        field_name='deviceType', choices=models.Submission.DEVICE_CHOICE, label=_("使用设备"))
    category_type = filters.ChoiceFilter(
        field_name='categoryType', choices=models.Submission.CATEGORY_CHOICE, label=_("题材类型"))
    theme_type = filters.ChoiceFilter(
        field_name='themeType', choices=models.Submission.THEME_CHOICE, label=('主题类型'))
    shortlist_status = filters.ChoiceFilter(
        field_name='shortlistType', choices=SHORTLIST, label=_("是否入选"), method="pesudo_filter")

    def pesudo_filter(self, queryset, name, value):
        return queryset


class DisplaySubmissionFilter(FilterSet):
    device_type = filters.ChoiceFilter(
        field_name='deviceType', choices=models.Submission.DEVICE_CHOICE, label=_("使用设备"))
    category_type = filters.ChoiceFilter(
        field_name='categoryType', choices=models.Submission.CATEGORY_CHOICE, label=_("题材类型"))
    theme_type = filters.ChoiceFilter(
        field_name='themeType', choices=models.Submission.THEME_CHOICE, label=('主题类型'))
