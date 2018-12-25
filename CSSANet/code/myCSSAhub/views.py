from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.models import update_last_login

from UserAuthAPI import models as UserModels
from django.contrib.auth.decorators import login_required
from UserAuthAPI.forms import BasicSiginInForm

from CSSANet.settings import MEDIA_ROOT, MEDIA_URL
from Library.Mixins import AjaxableResponseMixin

# Create your views here.
def register_guide(request):
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

@login_required(login_url='/hub/login/')
def notifications(request):
    return render(request, 'myCSSAhub/notifications.html')

@login_required(login_url='/hub/login/')
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


###### 账号相关 ##########
#用户登陆CBV -- 范例
class LoginPage(View):
    #类属性
    model = UserModels.User
    template_name = 'myCSSAhub/login.html'
    loginErrorMsg = {"result": "Login Failed!"}
    loginSuccessful = {"result": "Login Successful!"}

    #请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    #请求处理函数（post）    
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        print(email)
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



class BasicSignIn(FormView):
    template_name = 'myCSSAhub/registrationForm_step1.html'
    form_class = BasicSiginInForm

    def form_valid(self, form):
        form.save()
        return None

        

def register_form(request):
        return render(request, 'myCSSAhub/registrationForm_step1.html')

# 跳转至注册界面的第二步
def register_form_2(request):

    return render(request, 'myCSSAhub/registrationForm_step2.html')




############################# AJAX Page Resources #####################################

def GetUserAvatar(request):
    data = {}
    if request.user.is_authenticated:
        userQuery = UserModels.UserProfile.objects.filter(user=request.user).first()
        if userQuery is None:
            data['avatarPath'] = "Undefined"
        else:
            data['avatarPath'] = str(userQuery.avatar.url)
    else:
        data['errMsg'] = "Permission Denied"
    return JsonResponse(data)


def CheckEmailIntegrity(request):
    data = {}
    if request == 'POST':
        email = request.POST['email']
        userQuery = UserModels.User.objects.filter(email=email).first()
        if userQuery is None:
            data['result']='Valid'
        else:
            data['result']='Invalid'
    else:
        data = {
            'status': '400', 'reason': 'Bad Requests!'  
        }
    return JsonResponse(data)

def CheckTelIntegrity(request):
    data = {}
    if request == 'POST':
        telNumber = request.POST['telNumber']
        userQuery = UserModels.User.objects.filter(telNumber=telNumber).first()
        if userQuery is None:
            data['result']='Valid'
        else:
            data['result']='Invalid'
    else:
        data = {
            'status': '400', 'reason': 'Bad Requests!'  
        }
    return JsonResponse(data)

################################# errors pages ########################################
def bad_request(request):
 return render(request,'errors/page_400.html')

def permission_denied(request):
 return render(request,'errors/page_403.html')
 
def page_not_found(request):
 return render(request,'errors/page_404.html')
 
def server_error(request):
 return render(request,'errors/page_500.html')
