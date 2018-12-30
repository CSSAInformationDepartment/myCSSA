from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

# Create your views here.

class DepartmentManagementView(LoginRequiredMixin,View):
    login_url = '/hub/login/'
    template_name = 'OrganisationMgr/dept_mgr.html'

    #请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)