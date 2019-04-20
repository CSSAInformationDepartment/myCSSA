from django.shortcuts import render
from django.shortcuts import Http404, HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView

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
    model = models.Submission
    form_class = forms.CandidateSubmissionForm

    def get(self, request, *args, **kwargs):
        '''
        Proceed GET request for the submission page
        '''
        return render(request, self.template_name, {'form':self.form_class})

    def post(self, request, **args, *args, **kwargs):
        '''
        Proceed POST request for the submission page
        '''
        

        return render(self, request)