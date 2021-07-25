from django.db import models
from django.db.models.fields import CharField
from django.utils.timezone import now
from sorl.thumbnail import ImageField as SorlImageField

from UserAuthAPI.models import UserProfile


POST_CONTENT_LENGTH_MAX = 20000 # TODO: 决定一个长度
POST_TITLE_LENGTH_MAX = 100

# Create your models here.
class Tag(models.Model):
    title = models.CharField('标签标题', max_length=16)

    def __str__(self) -> str:
        return self.title

class Post(models.Model):
    # 标签。如果是回复，这里是null
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True)

    '''
    以下的两个外键决定了这个Post到底是主贴还是回复
    Main post / 主贴 / 1楼: replyToID = null, replyToComment = null
    对主贴的回复 / 1级回复: replyToID = 主贴ID, replyToComment = null
    对回复的回复 /2级回复: replyToID = 1级回复ID, replyToComment = 1级回复ID
    3级回复（跟3级显示在一起）: replyToID = 1级回复ID, replyToComment = 回复的Post 的 ID
    '''
    # 这里只能用字符串 'Post'，因为程序执行到这里的时候这个类还没定义完毕
    replyToId = models.ForeignKey('Post', null=True, on_delete=models.SET_NULL,
        related_name='%(class)s_reply_to_id') 
    replyToComment = models.ForeignKey('Post', null=True, on_delete=models.SET_NULL,
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

    class Meta:
        permissions = (
            ("censor_post", "Can censor post"),
        )

    # last edit time: read from content

    viewCount = models.IntegerField('访问次数', default=0)
        
class PostImage(models.Model):
    id = models.UUIDField(primary_key=True)
    image = SorlImageField(verbose_name='用户上传的图片', upload_to='uploads/community/post_image')
    uploader = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING,
        related_name='%(class)s_uploader')
    uploadTime = models.DateTimeField('本图片的上传时间', default=now)

class Content(models.Model):
    # django 对复合主键的支持不大好，这里就不把它当成主键了。
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # 其实这里不需要 previousContentID

    title = models.CharField('标题', max_length=POST_TITLE_LENGTH_MAX, null=True, default=None)
    text = models.TextField('帖子正文', max_length=POST_CONTENT_LENGTH_MAX, default='')

    images = models.ManyToManyField(PostImage, verbose_name='帖子关联的图片')

    editedTime = models.DateTimeField('当前Content的创建时间（Post的修改时间）', default=now)
    editedBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL,
        related_name='%(class)s_edited_by')

class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    targetPost = models.ForeignKey(Post, null=True, on_delete=models.CASCADE)
    data = models.JSONField('使用JSON表示额外的数据， 其格式根据type来变化')
    read = models.BooleanField('用户是否已读该通知', default=False)

    # 列出所有类型，防止打错字
    REPLY = 'REPLY'
    CENSOR = 'CENSOR'
    # End

    notificationTypeChoices = [
        (REPLY, '回复'),
        (CENSOR, '屏蔽')
    ]
    type = CharField('通知类型', choices=notificationTypeChoices, max_length=100)

class FavouritePost(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['userId', 'postId'], name='userId_postId')
        ]


class Report(models.Model):
    createdBy = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
        related_name='%(class)s_created_by')

    targetPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.TextField('举报原因', max_length=1000) # TODO: 决定一个长度

    resolved = models.BooleanField('是否已处理', default=False)
    resolvedBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL,
        related_name='%(class)s_resolved_by')
    
    reportTypeChoices = [] # TODO: 决定类型
    type = CharField('举报类型', choices=reportTypeChoices, max_length=100)

class UserInformation(models.Model):

    USERNAME_MAX_LENGTH = 30

    user_id = models.UUIDField('用户的id', primary_key=True, auto_created=False)

    username = models.CharField('用户名', max_length=USERNAME_MAX_LENGTH)
    avatarUrl = models.URLField('用户头像的url')