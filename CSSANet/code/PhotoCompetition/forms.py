from django import forms

from PhotoCompetition import models
class CandidateSubmissionForm(forms.ModelForm):
    '''
    PhotoCompetition ModelForm Class - Candidates Submission
    '''
    class Meta:
        model = models.Submission
        fields =('deviceType', 'categoryType', 'upload_photo', 'description')


    # def clean(self):
    #     super().clean()
    #     user_ id = 