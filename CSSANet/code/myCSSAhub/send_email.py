# 发送email的逻辑类
from .models import EmailConfiguration
from django.core.mail import EmailMultiAlternatives
from UserAuthAPI import models as UserModels
# 关键设定：不能直接调用CSSAnet这个module进行设定
from django.conf import settings

officialEmail = 'automail.cssa@cssaunimelb.com'


def send_emails(title, content, targetID):
    
    targetEmail = []
    email = queryEmailConfiguration()

    # 设置settings里邮件的属性
    settings.EMAIL_HOST_USER = email.host_user
    settings.EMAIL_HOST_PASSWORD = email.host_password
    settings.EMAIL_PORT = email.port
     
    # 获得需要发送的email地址
    for userID in targetID:
        info_list = UserModels.User.objects.get(id=userID)
        targetEmail.append(info_list.email)
    # print("user", email.host_user)
    # print("pwd", email.host_password)
    # print("port", email.port)
    # print("title", title)
    # print("port", content)
    # print("targetID", targetID)

    # 获取需要发送的目标用户邮箱

    html_content = '<p>欢迎访问<a href="http://www.CSSA.com" target=blank>www.CSSA.com</a>'+content+'</p>'

    msg = EmailMultiAlternatives(title, content, officialEmail, targetEmail)

    msg.attach_alternative(html_content, "text/html")

    msg.send()


def queryEmailConfiguration():

    try:
        email = EmailConfiguration.objects.get(host_user=officialEmail)

    except email.model.DoesNotExist:
        raise Http404('No %s matches the given query.' %
                      email.model.object_name)

    return email
