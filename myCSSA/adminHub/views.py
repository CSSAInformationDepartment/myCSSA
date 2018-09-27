from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def home(request):

    return render(request, 'adminHub/home.html')

def userInfo(request):
    return render(request, 'adminHub/userInfo.html')

def message(request):
    return render(request, 'adminHub/message.html')

def notifications(request):
    return render(request, 'adminHub/notifications.html')

def login(request):
    return render(request, 'adminHub/login.html')