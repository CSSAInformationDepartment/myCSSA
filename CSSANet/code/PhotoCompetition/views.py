from django.shortcuts import render
from django.shortcuts import Http404, HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView

from django.urls import reverse

from . import models
from . import forms
# Create your views here.

class CandidateSubmissionView(LoginRequiredMixin, View):
    '''
    PhotoCompetition App - CandidateSubmissionView
    Written by Le (Josh). Lu & Mengyu (Caitlin). Jiang - 2019

    This view is for presenting the submission form and retriving candidate's submission data
    '''
    login_url = '/hub/login/'
    template_name = 'PhotoCompetition/photoSubmit.html' 
    form_class = forms.CandidateSubmissionForm

    def get(self, request, *args, **kwargs):
        '''
        Proceed GET request for the submission page
        '''
        prev_submission = models.Submission.objects.filter(submissionUserId=request.user.id)
        print(prev_submission.__dict__)
        submit_form = self.form_class(initial={
            'submissionUserId': request.user.id
        })
        return render(request, self.template_name, {'form':submit_form, 'prev_submission':prev_submission})

    def post(self, request, *args, **kwargs):
        '''
        Proceed POST request for the submission page
        '''
        submission = self.form_class(data=request.POST or None, files=request.FILES)

        if submission.is_valid():
            submission.save()
            return HttpResponseRedirect(reverse('PublicSite:PhotoCompetition:submit-photo'))
        
        return render(request, self.template_name, {'form':submission})