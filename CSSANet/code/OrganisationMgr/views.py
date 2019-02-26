from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.urls import reverse
from django.utils.html import escape

from UserAuthAPI import models as UserModels
from FinanceAPI.apis import lodge_sys_gen_transaction

from .forms import *

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

class MemberSearchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.activate_membership')
    template_name = 'OrganisationMgr/dept_mgr.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        id = request.POST.get('lookUPId')
        return HttpResponseRedirect(reverse('myCSSAhub:OrganisationMgr:new_member_activation', args=[str(id)]))

class MembershipActivationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.activate_membership')
    template_name = 'OrganisationMgr/activate_user_view.html'

    def get(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(UserModels.UserProfile, user__pk=usr_id)
        form = BindingMembershipCardForm(initial={'user': usr_id})
        return render(request, self.template_name, {'user_profile':user_profile, 'form':form})

    def post(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(UserModels.UserProfile, user__pk=usr_id)
        form = BindingMembershipCardForm(data = request.POST or None, instance=user_profile)
        if form.is_valid():
            print("FORM VALID")
            instance = form.save()
            lodge_sys_gen_transaction(user_profile.user,type='New Member Activation', amount=5.00, 
                note='Card No.' + str(instance.membershipId))
            return HttpResponseRedirect(reverse('myCSSAhub:OrganisationMgr:confirm_activation', args=[str(usr_id)]))
        return render(request, self.template_name, {'user_profile':user_profile, 'form':form})

class ConfirmActivationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.activate_membership')
    template_name = 'OrganisationMgr/operation_result_view.html'

    def get(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(UserModels.UserProfile, user__pk=usr_id)
        return render(request, self.template_name, {'user_profile':user_profile})




class UserAuthLookup(LoginRequiredMixin, PermissionRequiredMixin ,View):
    login_url = '/hub/login/'
    permission_required = ()


    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'success': False,
            'status': '400',
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            search = request.POST.get('search', "")
            db_lookup = UserModels.UserProfile.objects.filter(
                Q(studentId__istartswith=search) |
                Q(user__email__istartswith=search) |
                Q(user__telNumber__icontains=search)
            )
            if db_lookup:
                result_set = []
                for result in db_lookup:
                    lookupResult = {
                        'id': result.user.id,
                        'full_name': str(result.firstNameEN) + " " + str(result.lastNameEN),
                        'full_name_cn': str(result.firstNameCN) + " " + str(result.lastNameCN),
                        'email': str(result.user.email),
                        'text': str(result.user.email)
                    }
                    if result.avatar:
                        lookupResult['avatar'] = str(result.avatar.url)
                    result_set.append(lookupResult)

                return JsonResponse({
                    'success': True,
                    'status': '200',
                    'result': result_set,
                })
            else:
                return JsonResponse({
                    'success': False,
                    'status': '404',
                    'result': None,
                })
        else:
            return JsonResponse({
                'success': False,
                'status': '400',
            })