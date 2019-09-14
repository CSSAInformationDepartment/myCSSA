from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Resume, JobList, InterviewTimetable
from .apis import GetResumesByDepartments, GetInterviewTimeByDepartments
from .forms import AddJobForm, AddInterviewForm

from myCSSAhub.apis import GetDocViewData
from UserAuthAPI.models import UserProfile
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.utils.formats import localize
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from django.utils.html import escape
from pytz import timezone
from CSSANet.settings import TIME_ZONE

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.exceptions import ValidationError

import django_filters
from . import models, forms, serializers
from UserAuthAPI.models import User, UserProfile
from mail_owl.utils import AutoMailSender


class JobListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.change_joblist',)
    model = JobList
    template_name='RecruitAPI/job_list.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class ResumeListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.view_resume',)
    model = Resume
    template_name='RecruitAPI/resume_list.html'

    def get(self, request, *args, **kwargs):
        resumes = GetResumesByDepartments(request.user)
        new_resume_count = resumes.filter(isOpened=False).count()

        return render(request, self.template_name, {'new_resume_count':new_resume_count})


class AddJobView(PermissionRequiredMixin, CreateView):
     form_class = AddJobForm
     permission_required = ('RecruitAPI.add_joblist',)
     model = JobList

     def form_valid(self, form):
         form.save()
         return super().form_valid(form)

class AddInterviewView(PermissionRequiredMixin, View):
    permission_required = ('RecruitAPI.add_interviewtimetable',)
    model = InterviewTimetable
    template_name='RecruitAPI/addto_interview.html'
    form_class = AddInterviewForm

    def get(self, request, *args, **kwargs):
        cv_id = self.kwargs.get('id')
        resume = get_object_or_404(Resume, CVId=cv_id)
        time_arrangement = self.model.objects.filter(resume=resume).first()
        if time_arrangement:
            return render(request, self.template_name, {'form':self.form_class,'current_arrangement':time_arrangement})
        return render(request, self.template_name, {'form':self.form_class, 'id':cv_id})
    
    def post(self, request, *args, **kwargs):
        cv_id = self.kwargs.get('id')
        resume = get_object_or_404(Resume, CVId=cv_id)
        form = self.form_class(data=request.POST)
        if form.is_valid():
            time_arrangement = form.save()
            resume.isEnrolled = True
            resume.save()
            mail_content = {'username': time_arrangement.resume.user.userprofile.lastNameEN + " " + time_arrangement.resume.user.userprofile.firstNameEN, 
                'date': time_arrangement.date,
                'time': time_arrangement.time, 
                'location': time_arrangement.location, 
                'note': time_arrangement.note, 
                'jobName': time_arrangement.resume.jobRelated.jobName}
                
            confirm_mail = AutoMailSender(
                title="Interview Scheduled. 您的面试时间已确认",
                mail_text="",
                template_path='myCSSAhub/email/interview_notice.html',
                fill_in_context=mail_content,
                to_address=resume.user.email,
            )
            confirm_mail.send_now()
            return render(request, self.template_name, {'form':self.form_class,'current_arrangement':time_arrangement})
        return render(request, self.template_name, {'form':self.form_class})


class ResumeDetailView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.view_resume',)
    model = Resume
    template_name='RecruitAPI/resume_detail.html'

    def get(self,request,*args, **kwargs):
        cv_id = self.kwargs.get('id')
        resume = get_object_or_404(Resume, CVId=cv_id)
        if request.user.is_staff and (not resume.isOpened):
            resume.isOpened = True
            resume.save()

        info_headers = [{'name':'提交时间', 'dbAttr': 'timeOfCreate'},{'name':'申请职位', 'dbAttr': 'jobRelated.jobName'},
            {'name':'主管部门', 'dbAttr': 'jobRelated.dept.deptTitle'},
            {'name':'申请原因', 'dbAttr': 'reason'},{'name':'兴趣爱好', 'dbAttr': 'hobby'}, 
            {'name':'校内经历', 'dbAttr': 'inSchoolExp'}, {'name':'其他信息/询问', 'dbAttr': 'additionMsg'}]

        return render(request, self.template_name, GetDocViewData(resume,info_headers, user_info_required=True, attachments=resume.attachment))

class ResumeListJsonView(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.view_resume',)
    model = Resume

    # define the columns that will be returned
    columns = ['CVId', 'user', 'jobRelated.dept.deptTitle',  'jobRelated.jobName', 'timeOfCreate', 'status']
    order_columns = ['CVId', 'user', 'jobRelated.dept.deptTitle',  'jobRelated.jobName', 'timeOfCreate','']

    max_display_length = 500

    def render_column(self, row, column):
        # Customer HTML column rendering
        if (column == 'timeOfCreate'):
            sys_tz = timezone(TIME_ZONE)
            return localize(row.timeOfCreate.astimezone(sys_tz))
        elif (column == 'user'):
            user_profile = UserProfile.objects.filter(user__id=row.user.id).first()
            if user_profile:
                return escape('%s %s' % (user_profile.lastNameEN, user_profile.firstNameEN))
            else:
                return escape(row.user.email)
        elif (column == 'status'):
            if row.isEnrolled:
                return '<span class="badge badge-warning">已计划面试</span>'
            elif row.isOfferd:
                return '<span class="badge badge-success">考核通过</span>'
            elif row.isReject:
                return '<span class="badge badge-danger">已拒绝</span>'
            elif row.isOpened:
                return '<span class="badge badge-primary">已读</span>'
            else:
                return '<span class="badge badge-secondary">未读</span>'


        else:
            return super(ResumeListJsonView, self).render_column(row, column)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return GetResumesByDepartments(self.request.user)

    def filter_queryset(self, qs):
        # DO NOT CHANGE THIS LINE
        search = self.request.GET.get('search[value]', None)

        if search:
            qs = qs.filter(Q(user__email__istartswith=search))
        return qs

class JobListJsonView(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.change_joblist',)
    model = JobList

    # define the columns that will be returned
    columns = ['jobName', 'dept.deptTitle','timeOfCreate',  'dueDate']
    order_columns = columns

    max_display_length = 500

    def render_column(self, row, column):
        # Customer HTML column rendering
        if (column == 'timeOfCreate'):
            sys_tz = timezone(TIME_ZONE)
            return localize(row.timeOfCreate.astimezone(sys_tz))
        elif (column == 'dueDate'):
            sys_tz = timezone(TIME_ZONE)
            return localize(row.dueDate.astimezone(sys_tz))
        else:
            return super(JobListJsonView, self).render_column(row, column)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(disabled=False).order_by('-timeOfCreate')

    def filter_queryset(self, qs):
        # DO NOT CHANGE THIS LINE
        search = self.request.GET.get('search[value]', None)

        if search:
            qs = qs.filter(Q(jobName__istartswith=search))
        return qs

class InterviewListJsonView(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.add_interviewtimetable',)
    model = InterviewTimetable

    # define the columns that will be returned
    columns = ['id', 'resume','date', 'time', 'location']
    order_columns = columns

    max_display_length = 500

    def render_column(self, row, column):
        # Customer HTML column rendering
        if (column == 'resume'):
            user_profile = UserProfile.objects.filter(user__id=row.resume.user.id).first()
            if user_profile:
                return escape('%s %s' % (user_profile.lastNameEN, user_profile.firstNameEN))
        else:
            return super(InterviewListJsonView, self).render_column(row, column)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return GetInterviewTimeByDepartments(self.request.user)

    def filter_queryset(self, qs):
        # DO NOT CHANGE THIS LINE
        search = self.request.GET.get('search[value]', None)

        if search:
            qs = qs.filter(Q(resume__user__email__istartswith=search))
        return qs
        
class JobListAPIViewSet(ReadOnlyModelViewSet):
   
    queryset = models.JobList.objects.all()
    serializer_class = (serializers.JobListSerializers)
    authentication_classes = (SessionAuthentication, TokenAuthentication)

class JobDetailView(View):
    model = JobList
    template_name='RecruitAPI/job_detail.html'

    def get(self,request,*args, **kwargs):
        job_id = self.kwargs.get('id')
        job = get_object_or_404(JobList, jobId=job_id)

        return render(request, self.template_name)