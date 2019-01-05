 from .models import EmailConfiguration 

# 获取存在数据库中的邮件设置
 def queryConfiguration():
    officialEmail = 'automail.cssa@cssaunimelb.com' 

    try:
       email = EmailConfiguration.objects.get(host_user=officialEmail)

    except email.model.DoesNotExist:
        raise Http404('No %s matches the given query.' %
                      email.model.object_name)    
    
    return email