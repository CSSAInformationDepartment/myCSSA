# 发送email的逻辑类
from .models import EmailConfiguration, EmailDB
from django.core.mail import EmailMultiAlternatives
from UserAuthAPI import models as UserModels
# 关键设定：不能直接调用CSSAnet这个module进行设定
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

officialEmail = 'automail.cssa@cssaunimelb.com'


def send_emails(title, content, targetID, currentUserId):

    targetEmail = []
    email = queryEmailConfiguration()

    # 设置settings里邮件的属性
    settings.EMAIL_HOST_USER = email.host_user
    settings.EMAIL_HOST_PASSWORD = email.host_password
    settings.EMAIL_PORT = email.port

    if title == 'Register Successful':

        # print("email", targetID)
        # d = Context()

        html_content = get_template(
            'myCSSAhub/email/register_mail.html').render({'username': content})

        targetEmail.append(targetID)

        email_content(title+" 欢迎您来到myCSSA", content, html_content, targetEmail)

    elif title == 'CV Submitted':

        jobName = content.jobRelated.jobName
        dept = content.jobRelated.dept.deptTitle
        username = content.user.userprofile.lastNameEN + " " + content.user.userprofile.firstNameEN
        username = content.user.userprofile.lastNameEN + " " + content.user.userprofile.firstNameEN
        html_content = get_template('myCSSAhub/email/cv_mail.html').render({'username': username, 'dept': dept,
                                                                                  'jobName': jobName})

        targetEmail.append(targetID)

        email_content(title+" 我们已经收到您的简历", 'CV Submitted', html_content, targetEmail)
    
    elif title == "Interview Scheduled":

        date = content.date
        time = content.time
        location = content.location
        note = content.note
        username = content.resume.user.userprofile.lastNameEN + " " + content.resume.user.userprofile.firstNameEN
        jobName = content.resume.jobRelated.jobName

        html_content = get_template('myCSSAhub/email/interview_notice.html').render({'username': username, 'date': date,
                                                                                  'time': time, 'location': location, 'note':note, 'jobName':jobName})

        targetEmail.append(targetID)

        email_content(title+" 您的CSSA Committee面试即将开始", 'Interview Scheduled', html_content, targetEmail)
    else:

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

# 根据不同内容，发送email


def email_content(title, content, html_content, targetEmail):

    # html_content = '<p>欢迎访问<a href="http://www.CSSA.com" target=blank>www.CSSA.com</a>'+content+'</p>'

    email_msg = EmailMultiAlternatives(
        title, content, officialEmail, targetEmail)

    email_msg.attach_alternative(html_content, "text/html")

    email_msg.send()

    # flag, message = insertEmailDB(title,content,targetID, currentUserId)

    # return flag


def queryEmailConfiguration():

    try:
        email = EmailConfiguration.objects.get(host_user=officialEmail)

    except email.model.DoesNotExist:
        raise Http404('No %s matches the given query.' %
                      email.model.object_name)

    return email


def queryEmailList(currentUserId):
    # 查询当前用户未读的信息, 在order_by 之前加负号，是为了以倒叙排列
    info_list = EmailDB.objects.filter(
        recID=currentUserId).order_by('-add_date').values()

    # 返回给view.py
    return info_list


def queryEmailContent(id):

    try:
        # 查询当前用户未读的信息内容, 将信息更新为已读
        info_list = EmailDB.objects.get(id=id)

        receiver = UserModels.UserProfile.objects.filter(
            user=info_list.recID).first()
        print(info_list.recID)
        sender = UserModels.UserProfile.objects.filter(
            user=info_list.sendID).first()

    except info_list.model.DoesNotExist:
        raise Http404('No %s matches the given query.' %
                      info_list.model.object_name)

    # print("sender", sender.firstNameEN)
    # print("receiver", receiver.firstNameEN)

    return info_list, sender, receiver


def insertEmailDB(title, content, targetUsersId, currentUserId):

    allID = '3a4b499e-b49d-4e19-9c02-d0123dd196a4'
    if form.is_valid():

        # title = form.cleaned_data['title']
        # content = form.cleaned_data['content']
        # 先定义一个发送者instance，以免重复定义
        sender = UserModels.User(id=currentUserId)

        if allID not in targetUsersId:
            # 把每一位接收者的ID输入到数据库之中去
            for targetId in targetUsersId:

                receiver = UserModels.User(id=targetId)

                # 0表示消息未读
                email_Db = EmailDB(sendID=sender, recID=receiver,
                                   title=title, content=content)
                email_Db.save()

            return True, "发送成功"
        else:
            # 邮件群发
            allUsersID = UserModels.User.objects.values_list('id')

            for usersID in allUsersID:
                # 群发id不包含当前用户
                if currentUserId != usersID:
                    receiver = UserModels.User(id=usersID)
                    email_Db = EmailDB(
                        sendID=sender, recID=receiver, title=title, content=content)
                    email_Db.save()

            return True, "群发成功"

        return False, "未能写入数据库"
    print(dict(form.errors))
    return False, "非法的表单"
