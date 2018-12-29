from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.models import update_last_login
from django.db.models import Q

from django.contrib.auth.decorators import login_required

from UserAuthAPI import models as UserModels
from UserAuthAPI.forms import BasicSiginInForm, UserInfoForm

from CSSANet.settings import MEDIA_ROOT, MEDIA_URL
from Library.Mixins import AjaxableResponseMixin

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
@login_required(login_url='/hub/login/')
def notifications_list(request):
    return render(request, 'myCSSAhub/notification/notifications_list.html')

@login_required(login_url='/hub/login/')
def notifications_form(request):
    return render(request, 'myCSSAhub/notification/notifications_form.html')

@login_required(login_url='/hub/login/')
def notifications_display(request):
    return render(request, 'myCSSAhub/notification/notifications_display.html')

###### 站内信 ##########

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
        if request.user.is_authenticated:
            return HttpResponseRedirect("/hub/home/")
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


class BasicSignInView(FormView):
    template_name = 'myCSSAhub/registrationForm_step1.html'
    form_class = BasicSiginInForm
    JsonData = {}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/hub/home/")
        """Handle GET requests: instantiate a blank version of the form."""
        return self.render_to_response(self.get_context_data())

        
    def form_valid(self, form):
        form.save()
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            currentUser = UserModels.User.objects.filter(email=email).first()
            self.JsonData['step1'] = 'done'
            self.JsonData['user'] = currentUser.id
        else:
            self.JsonData['error'] = 'Authentication System Error'
        return JsonResponse(self.JsonData)

class UserProfileCreateView(View):
    model = UserModels.User
    form_class = UserInfoForm
    JsonData={}
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.JsonData['userID'] =  request.user.id
        else:
            self.JsonData['error'] = "Invalid Form Request"
        return JsonResponse(self.JsonData)

    def post(self, request, *args, **kwargs):
        form=UserInfoForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            currentUser = UserModels.User.objects.filter(id=form.cleaned_data['user']).first()
            if currentUser:
                form.save()
                self.JsonData['step2'] = 'done'
            else:
                self.JsonData['error'] = "Invalid Form Request"
        else:
            return JsonResponse({
               'success': False,
                'errors': dict(form.errors.items()),
            })
        return JsonResponse(self.JsonData)        

def register_form(request):
        return render(request, 'myCSSAhub/registrationForm_step1.html')




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
            data['result']='Valid'
        else:
            data['result']='Invalid'
    else:
        data = {
            'status': '400', 'reason': 'Bad Requests!'  
        }
    return JsonResponse(data)
    
def CheckStudentIdIntegrity(request):
    data = {}
    if request.method == 'POST':
        studentId = request.POST['value']
        userQuery = UserModels.UserProfile.objects.filter(studentId=studentId).first()
        if userQuery is None:
            data['result']='Valid'
        else:
            data['result']='Invalid'
    else:
        data = {
            'status': '400', 'reason': 'Bad Requests!'  
        }
    return JsonResponse(data)

class UserLookup(LoginRequiredMixin,View):
    login_url = '/hub/login/'
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({
               'success': False,
               'status': '400',
            })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            search = request.POST.get('search',"")
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
                        'FullNameEN': result.firstNameEN+" "+result.lastNameEN,
                        'FullNameCN': result.firstNameCN+" "+result.lastNameCN,
                        'email': result.user.email,
                    }
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
