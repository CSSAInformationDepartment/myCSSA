from django import forms
from PhotoCompetition import models
class CandidateSubmissionForm(forms.ModelForm):
    '''
    PhotoCompetition ModelForm Class - Candidates Submission
    '''
    class Meta:
        model = models.Submission
        fields =('submissionUserId', 'deviceType', 'categoryType', 'upload_photo', 'description')