from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

# Create your views here.

class DepartmentManagementView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/hub/login/'
    template_name = 'OrganisationMgr/dept_mgr.html'
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            if self.request.user.get_committee_profile():
                return True
        return False

    #请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect("")



class GetCommitteeDetail(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'OrganisationMgr/dept_mgr.html'
    permission_required = 'UserAuthAPI.add_cssa_committe_profile'

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'success': False,
            'status': '400',
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            search = request.POST.get('search', "")
            print(search)
        else:
            return JsonResponse({
                'success': False,
                'status': '400',
            })