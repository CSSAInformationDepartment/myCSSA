from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import CreateView, UpdateView, FormView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.core.files import File
from django.contrib.auth.decorators import login_required


# Create your views here.
from .send_email import send_emails, queryEmailContent, queryEmailContent, queryEmailList
from .notification import insertDB, queryMessagesList, queryMessageContent
from .forms import NotificationForm
from .models import Notification_DB
from CSSANet.settings import MEDIA_ROOT, MEDIA_URL


###### 站内信 -- Start ##########

# 获取站内信列表
class NotificationsList(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'Communication/notification/notifications_list.html'
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
    template_name = 'Communication/notification/notifications_display.html'

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
    template_name = 'Communication/notification/notifications_form.html'

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
    template_name = 'Communication/email/email.html'

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
    template_name = 'Communication/email/email_history.html'

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

@login_required(login_url='/hub/login/')
def message(request):
    return render(request, 'Communication/message.html')

class Inbox(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'Communication/email/email_inbox.html'

    def get(self, request):
           
        return render(request, self.template_name, locals())
    
    def post(self, request):
        
        return render(request, self.template_name)

class Email_Message(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'Communication/email/email_message.html'

    def get(self, request):
           
        return render(request, self.template_name, locals())
    
    def post(self, request):
        
        return render(request, self.template_name)

class Email_Compose(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'Communication/email/email_compose.html' 

    def get(self, request):
           
        return render(request, self.template_name, locals())
    
    def post(self, request):
        
        return render(request, self.template_name)
