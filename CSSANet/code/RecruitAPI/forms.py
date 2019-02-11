from django import forms
from .models import JobList, Resume

class AddJobForm(forms.ModelForm):
    class Meta:
        model = JobList
        fields = '__all___'