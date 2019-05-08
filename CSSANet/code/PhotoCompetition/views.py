from django.shortcuts import render
from django.shortcuts import Http404, HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, DetailView
from django.urls import reverse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from . import models, forms, serializers, filters, app_permission
from UserAuthAPI.models import User, UserProfile

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


class SubmissionListAPIViewSet(ReadOnlyModelViewSet):
    '''
    PhotoCompetition App - Admin - Submission List API 
    Read Only

    Written by Le (Josh). Lu
    '''
    queryset = models.Submission.objects.all()
    serializer_class = (serializers.SubmissionListSerializers)
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)


class SubmissionListView(LoginRequiredMixin,PermissionRequiredMixin,ListView):
    template_name = 'PhotoCompetition/submission_list.html'
    queryset = models.Submission.objects.all()
    context_object_name = 'submissions'
    paginate_by = 25
    login_url = '/hub/login/'
    permission_required = ('PhotoCompetition.view_submission')




class SubmissionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    PhotoCompetition App - Admin - Submission Detail View 
    Read Only

    Written by Le (Josh). Lu
    '''
    template_name = 'PhotoCompetition/inspect_photo.html'
    model = models.Submission
    login_url = '/hub/login/'
    permission_required = ('PhotoCompetition.view_submission')
    def get_context_data(self, **kwargs):
        context = super(SubmissionDetailView, self).get_context_data(**kwargs)
        context['UserInfo'] = UserProfile.objects.filter(pk=self.object.submissionUserId.pk).first()
        context['AccountInfo'] = User.objects.get(pk=self.object.submissionUserId.pk)
        return context

    

class SubmissionSelectionControlAPI(APIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = models.ApprovedSubmission.objects.none()  # Required for DjangoModelPermissions

    def get_object(self, key):
        try:
            return models.ApprovedSubmission.objects.get(submission=key)
        except models.ApprovedSubmission.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        pk = request.GET.get('pk')
        if pk is None:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)
        approved_submission = models.ApprovedSubmission.objects.filter(submission__pk = pk).first()   
        res = serializers.SubmissionSelectionControlSerializers()
        if approved_submission:
            res = serializers.SubmissionSelectionControlSerializers(approved_submission)
        return Response(res.data)
    
    def post(self, request, format=None):
        serializer = serializers.SubmissionSelectionControlSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        pk = request.GET.get('pk')
        record = self.get_object(pk)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)