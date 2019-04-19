from django import forms
f
from PhotoCompetition import models
class CandidateSubmissionForm(forms.ModelForm):
    '''
    PhotoCompetition ModelForm Class - Candidates Submission
    '''
    class Meta:
        model = models.Submission
        fields =('submissionUserId', 'deviceType', 'categoryType', 'upload_photo', 'description')

    def clean(self):
        super().clean()
        user_id = self.get_cleaned_data('submissionUserId') 