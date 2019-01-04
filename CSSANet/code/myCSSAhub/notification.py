# 这个文件是用来处理关于站内信的所有相关业务逻辑，使得view.py不会过于冗长
# 这是发给全部用户的的特定ID: '3a4b499e-b49d-4e19-9c02-d0123dd196a4'，如果后台收到这个id,则说明用户要群发邮件
from UserAuthAPI import models as UserModels

from .models import Notification_DB

##### 插入数据库的操作#######


def insertDB(form, targetUsersId, currentUserId):

    allID = '3a4b499e-b49d-4e19-9c02-d0123dd196a4'
    if form.is_valid():

        title = form.cleaned_data['title']
        content = form.cleaned_data['content']
        # 先定义一个发送者instance，以免重复定义
        sender = UserModels.User(id=currentUserId)

        if allID not in targetUsersId:
            # 把每一位接收者的ID输入到数据库之中去
            for targetId in targetUsersId:

                receiver = UserModels.User(id=targetId)

                # 0表示消息未读
                notification_Db = Notification_DB(sendID=sender, recID=receiver, title=title, content=content,
                                                  status=0)
                notification_Db.save()

            return True, "发送成功"
        else:
            # 邮件群发
            allUsersID = UserModels.User.objects.values_list('id')

            for usersID in allUsersID:
                # 群发id不包含当前用户
                if currentUserId != usersID:
                    receiver = UserModels.User(id=usersID)
                    notification_Db = Notification_DB(sendID=sender, recID=receiver, title=title, content=content,
                                                      status=0)
                    notification_Db.save()

            return True, "群发成功"

        return False, "未能写入数据库"
    print(dict(form.errors))
    return False, "非法的表单"


##### 读取数据库的操作#######
def queryMessagesList(currentUserId):
    # 查询当前用户未读的信息, 在order_by 之前加负号，是为了以倒叙排列
    info_list = Notification_DB.objects.filter(
        recID=currentUserId).order_by('-add_date').values()

    # 返回给view.py
    return info_list


def queryMessageContent(id):

    try:
        # 查询当前用户未读的信息内容, 将信息更新为已读
        info_list = Notification_DB.objects.get(id=id)
        info_list.status = 1
        info_list.save()

        receiver = UserModels.UserProfile.objects.filter(user=info_list.recID).first()
        print(info_list.recID)
        sender = UserModels.UserProfile.objects.filter(user=info_list.sendID).first()

    except info_list.model.DoesNotExist:
        raise Http404('No %s matches the given query.' %
                      info_list.model.object_name)

    # print("sender", sender.firstNameEN)
    # print("receiver", receiver.firstNameEN)

    return info_list, sender, receiver
