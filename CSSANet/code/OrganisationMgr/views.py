from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.core.paginator import Paginator

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta

from UserAuthAPI import models as UserModels
from PrizeAPI.models import Prize
from RecruitAPI.models import Resume
from FinanceAPI.apis import lodge_sys_gen_transaction

from .forms import *
import random


# Create your views here.

# ============================  Committee 管理 =============================


class DepartmentManagementView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'OrganisationMgr/dept_mgr.html'
    permission_required = ('UserAuthAPI.view_cssacommitteprofile')
    ViewBag = {}
    ViewBag['PageHeader'] = _("部门成员")

    # 请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        dept_member_qs = UserModels.CSSACommitteProfile.objects.filter(
            is_active=True)
        qs = dept_member_qs
        if not (request.user.is_superuser or request.user.is_council_member):
            profile = UserProfile.objects.get(user=request.user)
            try:
                qs = dept_member_qs.filter(
                    Department=profile.get_committee_profile().Department)
            except:
                return HttpResponseForbidden()
        self.ViewBag['member_count'] = qs.count()
        paginator = Paginator(qs, 15)
        page = request.GET.get('page')
        self.ViewBag['dept_members'] = paginator.get_page(page)

        return render(request, self.template_name, self.ViewBag)

    def post(self, request, *args, **kwargs):
        id = request.POST.get('lookUPId')
        return HttpResponseRedirect(reverse('myCSSAhub:OrganisationMgr:dept_add_committee', args=[str(id)]))


class AddNewCommitteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'OrganisationMgr/assign_new_committee.html'
    permission_required = ('UserAuthAPI.add_cssacommitteprofile')
    ViewBag = {}
    ViewBag['PageHeader'] = _("部员信息确认")
    ViewBag['lock_table'] = False
    ViewBag['add_successful'] = False

    time_interval = datetime.today() - timedelta(days=180)

    def get(self, request, *args, **kwargs):
        self.ViewBag['lock_table'] = False
        self.ViewBag['add_successful'] = False

        usr_id = self.kwargs.get('id')
        self.ViewBag['usr_id'] = usr_id
        self.ViewBag['user_profile'] = get_object_or_404(
            UserModels.UserProfile, user__pk=usr_id)
        self.ViewBag['recent_resume'] = Resume.objects.filter(
            Q(user__pk=usr_id) & Q(timeOfCreate__gte=self.time_interval))
        roles_data = UserModels.CSSACommitteProfile.objects.filter(
            Q(member__pk=usr_id) & Q(is_active=True))
        if roles_data:
            self.ViewBag['is_assgined_with_role'] = roles_data
        else:
            self.ViewBag['is_assgined_with_role'] = None

        if request.user.is_superuser:
            self.ViewBag['form'] = AssignNewComitteeForm(initial={
                'member': usr_id,
                'role': 3,
            })
        else:
            profile = UserProfile.objects.get(user=request.user)
            self.ViewBag['recent_resume']
            self.ViewBag['lock_table'] = True
            self.ViewBag['form'] = AssignNewComitteeForm(initial={
                'member': usr_id,
                'Department': profile.get_committee_profile().Department.deptId,
                'role': 3,
            })

        return render(request, self.template_name, self.ViewBag)

    def post(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        self.ViewBag['usr_id'] = usr_id
        submit_form = AssignNewComitteeForm(data=request.POST or None)
        if submit_form.is_valid():
            submit_form.save()
            new_committee = UserModels.User.objects.get(pk=usr_id)
            new_committee.is_staff = True
            new_committee.save()
            self.ViewBag['add_successful'] = True
        self.ViewBag['form'] = submit_form
        return render(request, self.template_name, self.ViewBag)


class GetCommitteeDetail(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'OrganisationMgr/user_mgr.html'
    permission_required = 'UserAuthAPI.add_cssa_committe_profile'

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass

# ============================  新会员激活    =============================


class MemberSearchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.activate_membership')
    template_name = 'OrganisationMgr/user_mgr.html'
    ViewBag = {}
    ViewBag['PageHeader'] = _("查找新会员")

    def get(self, request, *args, **kwargs):
        self.ViewBag['total_user_count'] = UserProfile.objects.all().count()
        self.ViewBag['activated_member_count'] = UserProfile.objects.exclude(
            membershipId=None).count()
        return render(request, self.template_name, self.ViewBag)

    def post(self, request, *args, **kwargs):
        id = request.POST.get('lookUPId')
        return HttpResponseRedirect(reverse('myCSSAhub:OrganisationMgr:new_member_activation', args=[str(id)]))


class MembershipActivationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.activate_membership')
    template_name = 'OrganisationMgr/activate_user_view.html'
    ViewBag = {}
    ViewBag['PageHeader'] = _("新会员身份信息核查")

    def get(self, request, *args, **kwargs):

        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(
            UserModels.UserProfile, user__pk=usr_id)
        form = BindingMembershipCardForm(initial={'user': usr_id})
        self.ViewBag['usr_id'] = usr_id
        self.ViewBag['user_profile'] = user_profile
        self.ViewBag['form'] = form
        return render(request, self.template_name, self.ViewBag)

    def post(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(
            UserModels.UserProfile, user__pk=usr_id)
        form = BindingMembershipCardForm(
            data=request.POST or None, instance=user_profile)
        self.ViewBag['usr_id'] = usr_id
        self.ViewBag['user_profile'] = user_profile
        self.ViewBag['form'] = form
        if form.is_valid():
            instance = form.save()
            lodge_sys_gen_transaction(user_profile, type='New Member Activation', amount=5.00,
                                      note='Card No.' + str(instance.membershipId))
            return HttpResponseRedirect(reverse('myCSSAhub:OrganisationMgr:confirm_activation', args=[str(usr_id)]))
        return render(request, self.template_name, self.ViewBag)

# ============================   会员管理   =============================


class MemberListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.change_indentity_data')
    template_name = 'OrganisationMgr/user_mgr.html'
    ViewBag = {}
    ViewBag['PageHeader'] = _("会员信息管理")

    def get(self, request, *args, **kwargs):
        self.ViewBag['total_user_count'] = UserProfile.objects.all().count()
        self.ViewBag['activated_member_count'] = UserProfile.objects.exclude(
            membershipId=None).count()
        return render(request, self.template_name, self.ViewBag)

    def post(self, request, *args, **kwargs):
        id = request.POST.get('lookUPId')
        return HttpResponseRedirect(reverse('myCSSAhub:OrganisationMgr:update_member', args=[str(id)]))


class UserProfileEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.change_indentity_data')
    template_name = 'OrganisationMgr/update_user_profile.html'
    ViewBag = {}
    ViewBag['PageHeader'] = _("修改会员信息")
    ViewBag['left_form_header'] = _("用户信息表")
    ViewBag['right_form_header'] = _("账户信息表")

    def get(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(
            UserModels.UserProfile, user__pk=usr_id)
        user = get_object_or_404(UserModels.User, pk=usr_id)
        self.ViewBag['usr_id'] = usr_id
        self.ViewBag['form_left'] = UserProfileEditForm(instance=user_profile)
        self.ViewBag['form_right'] = UserEditForm(instance=user)
        return render(request, self.template_name, self.ViewBag)

    def post(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(
            UserModels.UserProfile, user__pk=usr_id)
        user = get_object_or_404(UserModels.User, pk=usr_id)
        self.ViewBag['successful_message'] = {}
        self.ViewBag['usr_id'] = usr_id
        self.ViewBag['form_left'] = UserProfileEditForm(
            data=request.POST or None, instance=user_profile)
        self.ViewBag['form_right'] = UserEditForm(
            data=request.POST or None, instance=user)

        if self.ViewBag['form_left'].is_valid():
            self.ViewBag['form_left'].save()
            self.ViewBag['form_right'] = UserEditForm(instance=user)
            self.ViewBag['successful_message']['left'] = True

        if self.ViewBag['form_right'].is_valid():
            self.ViewBag['form_right'].save()
            self.ViewBag['form_left'] = UserProfileEditForm(
                instance=user_profile)
            self.ViewBag['successful_message']['right'] = True

        return render(request, self.template_name, self.ViewBag)

first_prize = []
second_prize = []
third_prize = []


class ConfirmActivationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/hub/login/'
    permission_required = ('UserAuthAPI.activate_membership')
    template_name = 'OrganisationMgr/operation_result_view.html'
    ViewBag = {}
    ViewBag['PrizeHeader'] = _("中奖情况")
    
    def get(self, request, *args, **kwargs):
        usr_id = self.kwargs.get('id')
        user_profile = get_object_or_404(UserModels.UserProfile, user__pk=usr_id)
        self.ViewBag['usr_name'] = user_profile.firstNameEN + " " + user_profile.lastNameEN
        self.ViewBag['membership_id']= user_profile.membershipId

        luckyDrawNumber = random.randint(0, 30)
        
        print(luckyDrawNumber)

        # 如果数组存满了，再存入到数据库中去
        # print('一等奖数组长度:',len(first_prize))
        # print('二等奖数组长度:',len(second_prize))
        # print('三等奖数组长度:',len(third_prize))
        

        if len(first_prize) == 1:
            for userID in first_prize:
                winPrizeUser= UserModels.User(id=userID)
                firstPrize=Prize(prize_name="一等奖", prize_userId=winPrizeUser)
                firstPrize.save()
            print('')
        if len(second_prize) == 1:
            for userID in second_prize:
                winPrizeUser= UserModels.User(id=userID)
                secondPrize=Prize(prize_name="二等奖", prize_userId=winPrizeUser)
                secondPrize.save()
            print('')
        if len(third_prize) == 1:
            for userID in third_prize:
                winPrizeUser= UserModels.User(id=userID)
                thirdPrize=Prize(prize_name="三等奖", prize_userId=winPrizeUser)
                thirdPrize.save()
            print('')   


        if luckyDrawNumber < 3:

            if len(first_prize) < 1:
                first_prize.append(usr_id)
                self.ViewBag['PrizeDetail']=("恭喜您，获得一等奖！")
                # print("恭喜您，获得一等奖！")
            # elif len(second_prize) < 10:
            #     second_prize.append(usr_id)
            #     print("恭喜您，获得二等奖！")
            # elif len(third_prize) < 15:
            #     third_prize.append(usr_id)
            #     print("恭喜您，获得三等奖！")
            else:
                self.ViewBag['PrizeDetail']=("很遗憾，您没有中奖。")
                # print("很遗憾，您没有中奖。")

        elif luckyDrawNumber > 2 and luckyDrawNumber < 13:

            if len(second_prize) < 1:
                second_prize.append(usr_id)
                self.ViewBag['PrizeDetail']=("恭喜您，获得二等奖！")
                # print("恭喜您，获得二等奖！")
            # elif len(third_prize) < 15:
            #     third_prize.append(usr_id)
            #     print("恭喜您，获得三等奖！")
            else:
                self.ViewBag['PrizeDetail']=("很遗憾，您没有中奖。")
                # print("很遗憾，您没有中奖。")

        elif luckyDrawNumber > 12 and luckyDrawNumber <= 30:

            if len(third_prize) < 1:
                third_prize.append(usr_id)
                # print("恭喜您，获得三等奖！")
                self.ViewBag['PrizeDetail']=_("恭喜您，获得三等奖！")
            else:
                self.ViewBag['PrizeDetail']=("很遗憾，您没有中奖。")
                # print("很遗憾，您没有中奖。")

        else:
            self.ViewBag['PrizeDetail']=("很遗憾，您没有中奖。")
            # print("很遗憾，您没有中奖。")

        return render(request, self.template_name, self.ViewBag)
