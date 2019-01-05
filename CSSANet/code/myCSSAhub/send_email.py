# 发送email的逻辑类
from CSSANet import settings
from .models import EmailConfiguration

officialEmail = 'automail.cssa@cssaunimelb.com'

def send_single_email(form, targetID):
   

    title = form.cleaned_data['title']
    content = form.cleaned_data['content']

    email = queryEmailConfiguration()

    settings.EMAIL_HOST = email.host
    settings.EMAIL_HOST_USER = email.host_user
    settings.EMAIL_HOST_PASSWORD = email.host_password
    settings.EMAIL_PORT = email.port
    settings.EMAIL_USE_TLS = True

    
   






def queryEmailConfiguration():

    try:
        email = EmailConfiguration.objects.get(host_user=officialEmail)

    except email.model.DoesNotExist:
        raise Http404('No %s matches the given query.' %
                      email.model.object_name)

    return email
