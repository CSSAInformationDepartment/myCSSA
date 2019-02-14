from myCSSAhub.send_email import send_emails, queryEmailContent, queryEmailContent, queryEmailList
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .notification import insertDB, queryMessagesList, queryMessageContent
from .forms import NotificationForm, MerchantsForm
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm

from django.views import View
from django.views.generic import CreateView, UpdateView, FormView
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Notification_DB, AccountMigration, DiscountMerchant
from UserAuthAPI import models as UserModels
from BlogAPI import models as BlogModels
from UserAuthAPI.forms import BasicSiginInForm, UserInfoForm, MigrationForm, UserAcademicForm, UserProfileUpdateForm
from LegacyDataAPI import models as LegacyDataModels

from CSSANet.settings import MEDIA_ROOT, MEDIA_URL
from Library.Mixins import AjaxableResponseMixin
import json
import base64
import io
import hashlib

from urllib import parse

from django.core.files import File

import datetime

# Create your views here.


def register_guide(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/hub/home/")
    return render(request, 'myCSSAhub/register_guide.html')


@login_required(login_url='/hub/login/')
def home(request):
    return render(request, 'myCSSAhub/home.html')


@login_required(login_url='/hub/login/')
def message(request):
    return render(request, 'myCSSAhub/message.html')


###### 站内信 -- Start ##########

# 获取站内信列表
class NotificationsList(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/notification/notifications_list.html'
    paginate_by = 10
    context_object_name = 'infos'

    def get(self, request):
        if request.user.is_authenticated:
            # 获取当前用户id
            currentUserID = request.user.id

            # 将查询到的内容发送到前端
            infos = queryMessagesList(currentUserID)

            email_infos = queryEmailList(currentUserID)
            # 设置当前页面没有缓存
            # tmp.setdefault('Cache-Control', 'no-store')
            # tmp.setdefault('Expires', 0)
            # tmp.setdefault('Pragma', 'no-cache')

            return render(request, self.template_name, locals())

    def post(self, request):
        # if request.user.is_authenticated:
        #     # 先获取当前用户的id以便查询
        #     currentUserID=request.user.id
        return render(request, self.template_name)

# 展示站内信


class NotificationsDisplay(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/notification/notifications_display.html'

    def get(self, request, *args, **kwargs):
        contentId = self.kwargs.get('id')
        # print("usersfsdf", userId)
    #    将需要的id传入数据库已得到内容
        content, sender, receiver = queryMessageContent(contentId)

        return render(request, self.template_name, locals())

    def post(self, request):

        return render(request, self.template_name)

# 发送站内信


class NotificationForm(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/notification/notifications_form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        flag = False
        if request.user.is_authenticated:
            # 如果form通过POST方法发送数据
            # 发送的目标用户id
            targetUserId = request.POST.getlist('recID')
            # print("recID", targetUserId)
            # 当前用户id
            currentID = request.user.id

            form = NotificationForm(request.POST)

            flag, message = insertDB(form, targetUserId, currentID)

            # 测试返回结果
            if flag == False:
                print(message)

            return render(request, self.template_name, {'back_end_flag': flag})


################################# Email ########################################


class Email(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/email.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        flag = False
        if request.user.is_authenticated:
            targetUserId = request.POST.getlist('recID')
            title = request.POST['title']
            content = request.POST['content']
            # 当前用户id
            currentID = request.user.id

            print("title", title)
            print("targetUserId", targetUserId)
            print("content", content)

            if targetUserId is not None:
                flag = True

            # if targetUserId is not None:

            #   flag = send_emails(title, content, targetUserId, currentID)
            # else:
            #     raise Exception

        return render(request, self.template_name, {'back_end_flag': flag})


class EmailHistory(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/email_history.html'

    def get(self, request, *args, **kwargs):

        contentId = self.kwargs.get('id')
        # print("usersfsdf", userId)
        #    将需要的id传入数据库已得到内容
        content, sender, receiver = queryEmailContent(contentId)

        return render(request, self.template_name, locals())

    def post(self, request):

        # if request.user.is_authenticated:
        #     # 获取当前用户id
        #     currentUserID = request.user.id

        #     print("currentId")

        #     infos = queryEmailContent(currentUserID)

        return render(request, self.template_name, locals())

################################# merchants ########################################


class Merchants_list(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/merchants_list.html'

    def get(self, request):
        if request.user.is_authenticated:
            infos = DiscountMerchant.objects.all().order_by("merchant_add_date").values()

        return render(request, self.template_name, locals())

    def post(self, request):
        return render(request, self.template_name)


class Merchant_add(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/merchant_add.html'

    def get(self, request):

        return render(request, self.template_name)

    def post(self, request):
        have_update = False
        # 从表单获取图片并上传
        if request.user.is_authenticated:
            form = MerchantsForm(request.POST, request.FILES)
            if form.is_valid():

                m_name = form.cleaned_data['m_name']
                m_address = form.cleaned_data['m_address']
                m_phone = form.cleaned_data['m_phone']
                m_link = form.cleaned_data['m_link']
                m_description = form.cleaned_data['m_description']
                m_image = form.cleaned_data['m_image']

                # print("name", m_name)
                # print("address", m_address)
                # print("phone", m_phone)
                # print("link", m_link)
                # print("description", m_description)
                # print("image", m_image)

                new_merchant = DiscountMerchant(merchant_name=m_name, merchant_description=m_description,
                                                merchant_phone=m_phone, merchant_address=m_address, merchant_link=m_link, merchant_image=m_image)

                new_merchant.save()
                have_update = True

        return render(request, self.template_name, {'update': have_update})

# 这个页面主要是加载已经加入商家的信息，并更新


class Merchant_profile(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/merchant_profile.html'
    old_info = []

    def get(self, request,  *args, **kwargs):
        profileID = self.kwargs.get('id')
        # 获取id相关的信息
        infos = DiscountMerchant.objects.get(id=profileID)
        self.old_info = infos
        return render(request, self.template_name, locals())

    def post(self, request):
        have_update = False
        # 从表单获取更新信息
        if request.user.is_authenticated:
            form = MerchantsForm(request.POST, request.FILES)
            if form.is_valid():
                is_change = False
                m_name = form.cleaned_data['m_name']
                m_address = form.cleaned_data['m_address']
                m_phone = form.cleaned_data['m_phone']
                m_link = form.cleaned_data['m_link']
                m_description = form.cleaned_data['m_description']
                m_image = form.cleaned_data['m_image']

                if m_name != self.old_info.merchant_name:
                    self.old_info.merchant_name = m_name
                    is_change = True
                if m_address != self.old_info.merchant_address:
                    self.old_info.merchant_address = m_address
                    is_change = True
                if m_phone != self.old_info.merchant_phone:
                    self.old_info.merchant_phone = m_phone
                    is_change = True
                if m_link != self.old_info.merchant_link:
                    self.old_info.merchant_link = m_link
                    is_change = True
                if m_description != self.old_info.merchant_description:
                    self.old_info.merchant_description = m_description
                    is_change = True
                if m_image != self.old_info.merchant_image:
                    self.old_info.merchant_image = m_image
                    is_change = True
                
                if is_change:
                  self.old_info.save()
                  have_update = True

        return render(request, self.template_name, {'update': have_update})


###### logout page ##########

@login_required(login_url='/hub/login/')
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


###### 账号相关 ##########
# 用户登陆CBV -- 范例
class LoginPage(View):
    # 类属性
    model = UserModels.User
    template_name = 'myCSSAhub/login.html'
    loginErrorMsg = {"result": "Login Failed!"}
    loginSuccessful = {"result": "Login Successful!"}

    # 请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/hub/home/")
        return render(request, self.template_name)

    # 请求处理函数（post）
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        userQuery = self.model.objects.filter(email=email).first()
        if userQuery is None:
            return JsonResponse(self.loginErrorMsg)
        password = request.POST['password']
        # print(email,password,username)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            update_last_login(None, user)
            return JsonResponse(self.loginSuccessful)
        else:
            return JsonResponse(self.loginErrorMsg)


class NewUserSignUpView(View):
    template_name = 'myCSSAhub/registrationForm_step1.html'
    account_form = BasicSiginInForm
    profile_form = UserInfoForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/hub/home/")
        """Handle GET requests: instantiate a blank version of the form."""
        id = self.kwargs.get('id')
        legacy_data = None
        if id:
            try:
                migration_record = AccountMigration.objects.filter(
                    id=id).first()
                legacy_data = LegacyDataModels.LegacyUsers.objects.get(
                    Q(studentId=migration_record.studentId) & Q(
                        membershipId=migration_record.membershipId)
                )
            except ObjectDoesNotExist:
                print("Either the entry or blog doesn't exist.")

        return render(request, self.template_name, {'LegacyData': legacy_data})

    def post(self, request, *args, **kwargs):
        account_form = BasicSiginInForm(data=request.POST)
        profile_form = UserInfoForm(data=request.POST, files=request.FILES)
        academic_form = UserAcademicForm(data=request.POST)
        if account_form.is_valid() and profile_form.is_valid() and academic_form.is_valid():
            account_register = account_form.save(commit=False)
            account_form.save()
            profile = profile_form.save(commit=False)
            profile.user = account_register
            academic = academic_form.save(commit=False)
            academic.userProfile = account_register
            if profile.membershipId and profile.membershipId != '':
                profile.isValid = True
            profile.save()
            academic.save()

            # 完成信息保存以后，发送注册成功的邮件
            target_email = BasicSiginInForm.email
            send_emails('Register Successful','Howie Chen', 'shenhai0910@gmail.com', None)

        else:
            return JsonResponse({
                'success': False,
                'errors': [dict(account_form.errors.items()), dict(profile_form.errors.items()), dict(academic_form.errors.items())]
            })
        return JsonResponse({
            'success': True, })


class migrationView(View):
    template_name = 'myCSSAhub/migration.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        migration_request = MigrationForm(data=request.POST)
        if migration_request.is_valid():
            print(migration_request['studentId'].value())
            try:
                legacy_record = LegacyDataModels.LegacyUsers.objects.get(
                    Q(studentId=migration_request['studentId'].value()) & Q(
                        membershipId=migration_request['membershipId'].value())
                )
                if legacy_record.email == migration_request['email'].value() or legacy_record.telNumber == migration_request['telNumber'].value():
                    new_migration = AccountMigration(
                        studentId=migration_request['studentId'].value(),
                        membershipId=migration_request['membershipId'].value()
                    )
                    new_migration.save()
                    return JsonResponse({
                        'success': True,
                        'status': '200',
                        'migrationId': new_migration.id
                    })
            except ObjectDoesNotExist:
                return JsonResponse({
                    'success': False,
                    'status': '404',
                })


class UpdatePasswordView(LoginRequiredMixin, View):
    login_url = 'hub/login/'
    model = UserModels.User
    form_class = PasswordChangeForm
    template_name = 'myCSSAhub/update-password.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class(request.user)})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'New Password has been updated!')
            return HttpResponseRedirect('/hub/home')
        else:
            messages.error(request, 'Please double-check your input.')
        return render(request, self.template_name, {'form': form})


class UpdateUserProfileView(LoginRequiredMixin, View):
    login_url = 'hub/login/'
    model = UserModels.UserProfile
    form_class = UserProfileUpdateForm
    template_name = 'myCSSAhub/userInfo.html'

    def get(self, request, *args, **kwargs):
        current_data = self.model.objects.filter(user=request.user).first()
        return render(request, self.template_name, {'form': self.form_class, 'data': current_data})

    def post(self, request, *args, **kwargs):
        current_data = self.model.objects.get(user=request.user)
        form = self.form_class(request.POST or None, instance=current_data)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User Profile has been updated!')
            return HttpResponseRedirect('/hub/home')
        else:
            messages.error(request, 'Please double-check your input.')
            print(dict(form.errors))
        return render(request, self.template_name, {'form': form, 'data': current_data})


class MembershipCardView(LoginRequiredMixin, View):
    login_url = 'hub/login/'
    template_name = 'myCSSAhub/membership-home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

############################# blog ####################################################

def editBlog(request):
    # 需要判断contentId
    # avatar没有的时候会报错

    NEW_BLOG = -1

    CR_BLOG = "创建Blog"
    CH_BLOG = "更改Blog"
    blogId = request.GET["blogId"]
    try:
        blogId = int(blogId)
    except:
        return bad_request(request)

    print(blogId)
    ViewBag = {}

    userAuthed = request.user.is_authenticated

    if userAuthed:
        user = request.user
        ViewBag["user"] = {
            "user": request.user,
            "userProfile": UserModels.UserProfile.objects.filter(user=user)[0]
        }
    else:
        return bad_request(request)

    blogContentSingle = -1
    blogTitle = ""
    blogMainContent = ""


    if blogId != NEW_BLOG:
        blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blogId)
        wrote = False
        if blogWrittenBys:
            for blogWrittenBy in blogWrittenBys:
                if userAuthed and blogWrittenBy.userId == request.user:
                    wrote = True
                

            # user没有写blog
            if wrote == False:
                return permission_denied(request)
        blog = BlogModels.Blog.objects.filter(blogId=blogId)
        if not blog:
            return bad_request(request)
        blogContentSingle = blog[0]
        blogTitle = blogContentSingle.blogTitle
        blogMainContent = blogContentSingle.blogMainContent
        ViewBag["toolTitle"] = CH_BLOG
        curBlogTag = BlogModels.BlogInTag.objects.filter(blogId=blog[0])
        blogTag = json.dumps([x.tagId.tagName for x in curBlogTag]).replace("\\", "\\\\")

        ViewBag["blogTag"] = blogTag
    else:
        ViewBag["toolTitle"] = CR_BLOG

        ViewBag["blogTag"] = []
        pass

    ViewBag["blogId"] = blogId
    ViewBag["blogTitle"] = blogTitle
    ViewBag["blogMainContent"] = blogMainContent


    
    return render(request, 'myCSSAhub/blogeditpage.html', ViewBag)

############################# AJAX Page Resources #####################################


def GetUserAvatar(request):
    data = {}
    if request.user.is_authenticated:
        userQuery = UserModels.UserProfile.objects.filter(
            user=request.user).first()
        if userQuery is None:
            data['avatarPath'] = "Undefined"
        else:
            data['avatarPath'] = str(userQuery.avatar.url)
    else:
        data['errMsg'] = "Permission Denied"
    return JsonResponse(data)


def CheckEmailIntegrity(request):
    data = {}
    if request.method == 'POST':
        email = request.POST['value']
        print(email)
        userQuery = UserModels.User.objects.filter(email=email).first()
        if userQuery is None:
            data['result'] = 'Valid'
        else:
            data['result'] = 'Invalid'
    else:
        data = {
            'status': '400', 'reason': 'Bad Requests!'
        }
    print(data)
    return JsonResponse(data)


def CheckTelIntegrity(request):
    data = {}
    if request.method == 'POST':
        telNumber = request.POST['value']
        userQuery = UserModels.User.objects.filter(telNumber=telNumber).first()
        if userQuery is None:
            data['result'] = 'Valid'
        else:
            data['result'] = 'Invalid'
    else:
        data = {
            'status': '400', 'reason': 'Bad Requests!'
        }
    return JsonResponse(data)


def CheckStudentIdIntegrity(request):
    data = {}
    if request.method == 'POST':
        studentId = request.POST['value']
        userQuery = UserModels.UserProfile.objects.filter(
            studentId=studentId).first()
        if userQuery is None:
            data['result'] = 'Valid'
        else:
            data['result'] = 'Invalid'
    else:
        data = {
            'status': '400', 'reason': 'Bad Requests!'
        }
    return JsonResponse(data)


class UserLookup(LoginRequiredMixin, View):
    login_url = '/hub/login/'

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'success': False,
            'status': '400',
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            search = request.POST.get('search', "")
            print(search)
            db_lookup = UserModels.UserProfile.objects.filter(
                Q(firstNameEN__istartswith=search) | Q(lastNameEN__istartswith=search) |
                Q(firstNameCN__istartswith=search) | Q(lastNameCN__istartswith=search) |
                Q(studentId__istartswith=search) |
                Q(user__email__istartswith=search) |
                Q(user__telNumber__istartswith=search)
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

    


        


################################# errors pages ########################################


def bad_request(request):
    return render(request, 'errors/page_400.html')


def permission_denied(request):
    return render(request, 'errors/page_403.html')


def page_not_found(request):
    return render(request, 'errors/page_404.html')


def server_error(request):
    return render(request, 'errors/page_500.html')


def under_dev_notice(request):
    return render(request, 'myCSSAhub/under-dev-function.html')
