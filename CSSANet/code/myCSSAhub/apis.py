import os, operator

def GetDocViewData(instance, headers, user_info_required, attachments, **kwargs):
    '''
    用于生成DocView的数据
    可overload选项：
        - user_info_required
        - attachments
    '''
    view_bag = {'Data':[]}
    view_bag['id'] = instance.pk

    for item in headers:
        view_bag['Data'].append({
            'name':item['name'],
            'value':operator.attrgetter(item['dbAttr'])(instance)
       })
    
    if user_info_required:
        from UserAuthAPI.models import UserProfile
        userinfo = UserProfile.objects.filter(user__id=instance.user.id).first()
        if userinfo:
            view_bag['AccountInfo'] = instance.user
            view_bag['UserInfo'] = userinfo
        else:
            view_bag['UserInfo'] = None

    if attachments:
        view_bag['attachment'] = attachments
        print(attachments.name)
        name, extension = os.path.splitext(attachments.name)
        view_bag['file_name'] = os.path.basename(name)
        if extension[1:] == 'pdf':
            view_bag['file_ext'] = 'pdf'
        else:
            view_bag['file_ext'] = 'office'

    return {'DocView': view_bag}

    

