from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from PhotoCompetition import models
class CandidateSubmissionForm(forms.ModelForm):
    '''
    PhotoCompetition ModelForm Class - Candidates Submission
    '''
    class Meta:
        model = models.Submission
        fields =('submissionUserId', 'deviceType', 'categoryType', 'upload_photo', 'description')
        widgets = {
            'submissionUserId': forms.HiddenInput,
            'description': forms.Textarea
        }


    def clean(self):
        super().clean()
        user_id = self.cleaned_data.get('submissionUserId')
        #device_type = self.cleaned_data.get('deviceType')
        category_type = self.cleaned_data.get('categoryType')

        check_duplication = models.Submission.objects.filter(Q(submissionUserId=user_id)
            & Q(categoryType=category_type)).first()

        if check_duplication:
            raise ValidationError(_(mark_safe('<li>您已在该类别有过提交记录</li>')), code='duplicated submission in the same category')
