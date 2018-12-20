from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from UserAuthAPI import models
from . import forms
from django.contrib.auth.decorators import login_required
from UserAuthAPI.forms import ValidationForm

# Create your views here.


@login_required(login_url='/adminhub/login/')
def home(request):

    return render(request, 'adminHub/home.html')


@login_required(login_url='/adminhub/login/')
def userInfo(request):
    return render(request, 'adminHub/userInfo.html')


@login_required(login_url='/adminhub/login/')
def message(request):
    return render(request, 'adminHub/message.html')


@login_required(login_url='/adminhub/login/')
def notifications(request):
    return render(request, 'adminHub/notifications.html')


###### 账号相关 ##########
def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        userQuery = models.User.objects.filter(email=email).first()
        if userQuery is None:
            return JsonResponse({'result': 'Login Failed. Please Check your account inputs!'})
        password = request.POST['password']
        # print(email,password,username)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return JsonResponse({'result': 'Login Failed. Please Check your account inputs!'})
    else:
        return render(request, 'adminHub/login.html')


def register_guide(request):
    return render(request, 'adminHub/register_guide.html')


def register_form(request):
    ########注册验证##########
    if request.method == 'POST':
        form = ValidationForm(request.POST)
        if form.is_valid(): 
            # redirect to a new URL:
            return self.register_form_2(request)
    else:

        return render(request, 'adminHub/registrationForm_step1.html')

# 跳转至注册界面的第二步
def register_form_2(request):
 
    return render(request, 'adminHub/registrationForm_step2.html') 

    
@login_required(login_url='/adminhub/login/')
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

    




