from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField

from UserAuthAPI.models import User, UserProfile

# Create your models here.
class Tag(models.Model):
    title = models.CharField('标签标题', max_length=16)

class Post(models.Model):
    tagId = models.ForeignKey(Tag, on_delete=models.CASCADE)
    contentId = models.ForeignKey('Content', on_delete=models.CASCADE)

    '''
    以下的两个外键决定了这个Post到底是主贴还是回复
    Main post / 主贴 / 1楼: replyToID = null, replyToComment = null
    对主贴的回复 / 1级回复: replyToID = 主贴ID, replyToComment = null
    对回复的回复 /2级回复: replyToID = 1级回复ID, replyToComment = 1级回复ID
    3级回复（跟3级显示在一起）: replyToID = 1级回复ID, replyToComment = 回复的Post 的 ID
    '''
    # 这里只能用字符串 'Post'，因为程序执行到这里的时候这个类还没定义完毕
    replyToId = models.OneToOneField('Post', null=True, on_delete=models.SET_NULL,
        related_name='%(class)s_reply_to_id') 
    replyToComment = models.OneToOneField('Post', null=True, on_delete=models.SET_NULL,
        related_name='%(class)s_reply_to_comment') 

    viewableToGuest = models.BooleanField('未登录用户是否可见')

    deleted = models.BooleanField('是否被删除', default=False)
    deletedBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL, 
        related_name='%(class)s_deleted_by')

    censored = models.BooleanField('是否被审查', default=False)
    censoredBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL, 
        related_name='%(class)s_censored_by')

    createTime = models.DateTimeField('创建时间', auto_now_add=True)
    createdBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created_by')

    # last edit time: read from content

    viewCount = models.IntegerField('访问次数', default=0)

class Content(models.Model):
    # django 对复合主键的支持不大好，这里就不把它当成主键了。
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    # 其实这里不需要 previousContentID

    text = models.TextField('帖子正文', max_length=20000) # TODO: 决定一个长度

    imageUrls = ArrayField(models.URLField(), verbose_name='帖子中出现的url')

class Notification(models.Model):
    userId = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    targetId = models.ForeignKey(Post, null=True, on_delete=models.CASCADE)
    data = models.JSONField('使用JSON表示额外的数据， 其格式根据type来变化')
    read = models.BooleanField('用户是否已读该通知', default=False)

    notificationTypeChoices = [] # TODO: 决定类型
    type = CharField('通知类型', choices=notificationTypeChoices, max_length=100)

class FavouritePost(models.Model):
    userId = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together=(("userId","postId"),)

class Report(models.Model):
    createdBy = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    targetId = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.TextField('举报原因', max_length=1000) # TODO: 决定一个长度

    resolved = models.BooleanField('是否已处理', default=False)
    resolvedBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL)
    
    reportTypeChoices = [] # TODO: 决定类型
    type = CharField('举报类型', choices=reportTypeChoices, max_length=100)