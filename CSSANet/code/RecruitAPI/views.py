from django.shortcuts import render
from django.db.models import Q

from .models import Resume, JobList
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView


from .forms import AddJobForm

# Create your views here.
class JobListJsonView(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.view_joblist',)
    model = JobList

    # define the columns that will be returned
    columns = ['timeOfCreate', 'jobName', 'dept', 'dueDate']
    order_columns = columns

    max_display_length = 500

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.all().order_by('-time')

    def filter_queryset(self, qs):
        # DO NOT CHANGE THIS LINE
        search = self.request.GET.get('search[value]', None)

        if search:
            qs = qs.filter(jobName__istartswith=search)
        return qs

class AddJobView(PermissionRequiredMixin, CreateView):
     form_class = AddJobForm
     permission_required = ('RecruitAPI.add_joblist',)
     model = JobList

     def form_valid(self, form):
         form.save()
         return super().form_valid(form)