# 这个文件是用来处理关于站内信的所有相关业务逻辑，使得view.py不会过于冗长
# 这是发给全部用户的ID: '3a4b499e-b49d-4e19-9c02-d0123dd196a4'
from .forms import NotificationForm as Notification_Form
from .models import Notification_DB
from UserAuthAPI import models as UserModels


def processDB(targetUserId, currentUserId):
    form = Notification_Form(request.POST)

    allID = '3a4b499e-b49d-4e19-9c02-d0123dd196a4'

    if form.is_valid():

        title = form.cleaned_data['title']
        content = form.cleaned_data['content']

        if allID not in targetUserId:
            # 把接收者的ID输入到数据库之中去
            for targetId in targetUserId:

                receiver = UserModels.User(id=targetId)
                sender = UserModels.User(id=currentUserId)
                # 0表示消息未读
                notification_Db = Notification_DB(sendID=sender, recID=receiver, title=title, content=content,
                                                  status=0)
                notification_Db.save()
             # user1 = UserModels.User(id="27ebd0e9-5cce-4cc9-8ae9-c7398b54f4ec",
            #                         email="ff@gmail.com", telNumber="123456789")
            # user2 = UserModels.User(id="e06d1184-de29-4c95-aa72-5180c42d5cf3",
            #                         email="gg@gmail.com", telNumber="123456799")

        # form = Notification_Form(request.POST)

        # user1 = UserModels.User(id="27ebd0e9-5cce-4cc9-8ae9-c7398b54f4ec",
        #                         email="ff@gmail.com", telNumber="123456789")
        # user2 = UserModels.User(id="e06d1184-de29-4c95-aa72-5180c42d5cf3",
        #                         email="gg@gmail.com", telNumber="123456799")

        # user1.save()
        # user2.save()

        # 验证数据是否合法

        # if form.is_valid():
        #     recID = form.cleaned_data['recID']
        #     title = form.cleaned_data['title']
        #     content = form.cleaned_data['content']

        #print("recID", recID)
        # print("title", title)
        # print("content", content)

        # notification_Db = Notification_DB(sendID=user1, recID=user2, title=title, content=content,
        #                                   status=0)

        # notification_Db.save()

        # aa = Notification_DB.objects.all().values()

        # print(aa)
