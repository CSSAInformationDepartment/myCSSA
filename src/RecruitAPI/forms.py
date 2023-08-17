from django import forms

from .models import InterviewTimetable, JobList, Resume


class AddJobForm(forms.ModelForm):
    class Meta:
        model = JobList
        fields = '__all__'


class ResumeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('jobRelated', 'user', 'reason',
                  'hobby', 'inSchoolExp', 'attachment')


class AddInterviewForm(forms.ModelForm):
    class Meta:
        model = InterviewTimetable
        fields = '__all__'
