from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from UserAuthAPI import models
from . import forms
from django.contrib.auth.decorators import login_required
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
def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        userQuery = models.User.objects.filter(email = email).first()
        if userQuery is None:
            return JsonResponse({'result':'Login Failed. Please Check your account inputs!'})
        password = request.POST['password']
        #print(email,password,username)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return JsonResponse({'result':'Login Failed. Please Check your account inputs!'})
    else:
        return render(request, 'myCSSAhub/login.html')

def register_guide(request):
    return render(request, 'myCSSAhub/register_guide.html')

def register_form(request):

    return render(request, 'myCSSAhub/registrationForm_step1.html')


@login_required(login_url='/hub/login/')
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
