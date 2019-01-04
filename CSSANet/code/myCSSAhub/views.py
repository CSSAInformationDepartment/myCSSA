
from .notification import insertDB, queryMessagesList
from .forms import NotificationForm as Notification_Form
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Notification_DB, AccountMigration
from UserAuthAPI import models as UserModels
from UserAuthAPI.forms import BasicSiginInForm, UserInfoForm, MigrationForm
from LegacyDataAPI import models as LegacyDataModels
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from CSSANet.settings import MEDIA_ROOT, MEDIA_URL
from Library.Mixins import AjaxableResponseMixin
import json

# Create your views here.


def register_guide(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/hub/home/")
    return render(request, 'myCSSAhub/register_guide.html')


@login_required(login_url='/hub/login/')
def home(request):
    return render(request, 'myCSSAhub/home.html')


@login_required(login_url='/hub/login/')
def userInfo(request):
    return render(request, 'myCSSAhub/userInfo.html')


@login_required(login_url='/hub/login/')
def message(request):
    return render(request, 'myCSSAhub/message.html')


###### 站内信 ##########

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# @login_required(login_url = '/hub/login/')
# def NotificationsList(request):
#     if request.user.is_authenticated:
#         currentUserID=request.user.id
     
#     # print(currentUserID) 
#     # 将查询到的内容发送到前端
#         title = queryMessagesList(currentUserID)
#         return render(request,'myCSSAhub/notification/notifications_list.html', locals())



# 获取站内信列表
class NotificationsList(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'myCSSAhub/notification/notifications_list.html'
    paginate_by = 10  
    context_object_name = 'infos' 

    def get(self, request):
        if request.user.is_authenticated:
            currentUserID=request.user.id
            
            # print(currentUserID) 
            # 将查询到的内容发送到前端
            infos = queryMessagesList(currentUserID)
            return render(request,self.template_name, locals())

    def post(self, request):
        if request.user.is_authenticated:
            # 先获取当前用户的id以便查询
            currentUserID=request.user.id


        return render(request, self.template_name)

# 展示站内信

class NotificationsDisplay(LoginRequiredMixin, View):
    login_url='/hub/login/'
    template_name='myCSSAhub/notification/notifications_display.html'

    def get(self, request, *args, **kwargs):
        userId = self.kwargs.get('id')
        print("usersfsdf", userId)

        return render(request, self.template_name)

    def post(self, request):

        return render(request, self.template_name)

# 发送站内信


class NotificationForm(LoginRequiredMixin, View):
    login_url='/hub/login/'
    template_name='myCSSAhub/notification/notifications_form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            # 如果form通过POST方法发送数据
            # 发送的目标用户id
            targetUserId=request.POST.getlist('recID')
            # print("recID", targetUserId)
            # 当前用户id
            currentID=request.user.id

            form=Notification_Form(request.POST)

            flag, message=insertDB(form, targetUserId, currentID)

            # 测试返回结果
            if flag == False:
                print(message)

            return render(request, self.template_name)


###### 站内信 ##########

@login_required(login_url = '/hub/login/')
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


###### 账号相关 ##########
# 用户登陆CBV -- 范例
class LoginPage(View):
    # 类属性
    model=UserModels.User
    template_name='myCSSAhub/login.html'
    loginErrorMsg={"result": "Login Failed!"}
    loginSuccessful={"result": "Login Successful!"}

    # 请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/hub/home/")
        return render(request, self.template_name)

    # 请求处理函数（post）
    def post(self, request, *args, **kwargs):
        email=request.POST['email']
        print(email)
        userQuery=self.model.objects.filter(email = email).first()
        if userQuery is None:
            return JsonResponse(self.loginErrorMsg)
        password=request.POST['password']
        # print(email,password,username)
        user=authenticate(request, email = email, password = password)
        if user is not None:
            login(request, user)
            update_last_login(None, user)
            return JsonResponse(self.loginSuccessful)
        else:
            return JsonResponse(self.loginErrorMsg)


class NewUserSignUpView(View):
    template_name='myCSSAhub/registrationForm_step1.html'
    account_form=BasicSiginInForm
    profile_form=UserInfoForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/hub/home/")
        """Handle GET requests: instantiate a blank version of the form."""
        id=self.kwargs.get('id')
        legacy_data=None
        if id:
            try:
                migration_record=AccountMigration.objects.filter(
                    id = id).first()
                legacy_data=LegacyDataModels.LegacyUsers.objects.get(
                    Q(studentId=migration_record.studentId) & Q(
                        membershipId=migration_record.membershipId)
                )
            except ObjectDoesNotExist:
                print("Either the entry or blog doesn't exist.")

        return render(request, self.template_name, {'LegacyData': legacy_data})

    def post(self, request, *args, **kwargs):
        account_form = BasicSiginInForm(data=request.POST)
        profile_form = UserInfoForm(data=request.POST, files=request.FILES)
        if account_form.is_valid() and profile_form.is_valid():
            account_register = account_form.save(commit=False)
            account_form.save()
            profile = profile_form.save(commit=False)
            profile.user = account_register
            if profile.membershipId and profile.membershipId != '':
                profile.isValid = True
            profile.save()
        else:
            print(dict(profile_form.errors.items()))
            return JsonResponse({
                'success': False,
                'errors': [dict(account_form.errors.items()), dict(profile_form.errors.items())]
            })
        return JsonResponse({
            'success': True, })


class migrationView(FormView):
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
