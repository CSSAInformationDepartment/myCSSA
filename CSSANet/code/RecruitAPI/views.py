from django.shortcuts import render
from django.db.models import Q

from .models import Resume, JobList
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from django.utils.html import escape



from .forms import AddJobForm
class JobListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('RecruitAPI.change_joblist',)
    model = JobList
    template_name='RecruitAPI/job_list.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


# Create your views here.
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
            return escape(row.timeOfCreate.strftime('%Y/%m/%d %H:%M:%S'))
        elif (column == 'dueDate'):
            return escape(row.dueDate.strftime('%Y/%m/%d %H:%M:%S'))
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

class AddJobView(PermissionRequiredMixin, CreateView):
     form_class = AddJobForm
     permission_required = ('RecruitAPI.add_joblist',)
     model = JobList

     def form_valid(self, form):
         form.save()
         return super().form_valid(form)