from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View

from UserAuthAPI import models
from . import forms
from django.contrib.auth.decorators import login_required
from UserAuthAPI.forms import BasicSiginInForm

# Create your views here.

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


###### 账号相关 ##########

#用户登陆CBV -- 范例
class LoginPage(View):
    #类属性
    model = models.User
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
            return JsonResponse(self.loginSuccessful)
        else:
            return JsonResponse(self.loginErrorMsg)


def register_guide(request):
    return render(request, 'myCSSAhub/register_guide.html')

class classname(object):
    pass

def register_form(request):

    ########注册验证##########
    if request.method == 'POST':
        form = ValidationForm(request.POST)
        if form.is_valid():
            # redirect to a new URL:
            return self.register_form_2(request)
    else:

        return render(request, 'myCSSAhub/registrationForm_step1.html')

# 跳转至注册界面的第二步
def register_form_2(request):

    return render(request, 'myCSSAhub/registrationForm_step2.html')


@login_required(login_url='/hub/login/')
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


################################# errors pages ########################################
from django.shortcuts import render
 
def bad_request(request):
 return render(request,'errors/page_400.html')

def permission_denied(request):
 return render(request,'errors/page_403.html')
 
def page_not_found(request):
 return render(request,'errors/page_404.html')
 
def server_error(request):
 return render(request,'errors/page_500.html')
################################# errors pages ########################################