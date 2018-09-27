from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from . import models

# Create your views here.

def home(request):

    return render(request, 'adminHub/home.html')

def userInfo(request):
    return render(request, 'adminHub/userInfo.html')

def message(request):
    return render(request, 'adminHub/message.html')

def notifications(request):
    return render(request, 'adminHub/notifications.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = models.UserProfile.objects.get(email = email).username
        password = request.POST['password']
        print(email,password,username)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/index')
        else:
            return JsonResponse(request, {'result':'Login Failed. Please Check your account inputs!'})
    else:
        return render(request, 'adminHub/login.html')

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/index')