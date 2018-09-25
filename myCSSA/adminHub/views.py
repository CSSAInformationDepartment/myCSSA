from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def userInfo(request):
    return render(request, 'userInfo.html')

def message(request):
    return render(request, 'message.html')

def notifications(request):
    return render(request, 'notifications.html')