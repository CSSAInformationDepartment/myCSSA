from typing import Dict
from django.db import models
from django.db.models.deletion import SET_NULL
from django.db.models.fields import CharField
from django.utils.timezone import now
from sorl.thumbnail import ImageField as SorlImageField

from UserAuthAPI.models import UserProfile


POST_CONTENT_LENGTH_MAX = 20000  # TODO: 决定一个长度
POST_TITLE_LENGTH_MAX = 100

# Create your models here.


class Tag(models.Model):
    """
    主贴的标签
    """

    title = models.CharField('标签标题', max_length=16)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """
    表示一个帖子，可以是主贴或者回复
    """

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

    # last edit time: read from content

    viewCount = models.IntegerField('访问次数', default=0)

    class Meta:
        permissions = (
            ("censor_post", "Can censor post"),
        )

    # types
    MAIN_POST = 'MAIN_POST'
    COMMENT = 'COMMENT'
    SUBCOMMENT = 'SUBCOMMENT'

    @property
    def type(self):
        """
        获取post的类型
        """
        if not self.replyToId:
            assert not self.replyToComment
            return self.MAIN_POST
        elif not self.replyToComment:
            return self.COMMENT
        else:
            return self.SUBCOMMENT


class PostImage(models.Model):
    """
    帖子里的图片
    """

    id = models.UUIDField(primary_key=True)
    image = SorlImageField(verbose_name='用户上传的图片',
                           upload_to='uploads/community/post_image')
    uploader = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING,
                                 related_name='%(class)s_uploader')
    uploadTime = models.DateTimeField('本图片的上传时间', default=now)


class Content(models.Model):
    """
    帖子的内容。一个帖子可以有多个版本，每个版本都是一个 Content
    """

    # django 对复合主键的支持不大好，这里就不把它当成主键了。
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='contents')
    # 其实这里不需要 previousContentID

    title = models.CharField(
        '标题', max_length=POST_TITLE_LENGTH_MAX, null=True, default=None)
    text = models.TextField(
        '帖子正文', max_length=POST_CONTENT_LENGTH_MAX, default='')

    images = models.ManyToManyField(PostImage, verbose_name='帖子关联的图片')

    editedTime = models.DateTimeField('当前Content的创建时间（Post的修改时间）', default=now)
    editedBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL,
                                 related_name='%(class)s_edited_by')


class Notification(models.Model):
    """
    通知
    """

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    targetPost = models.ForeignKey(Post, null=True, on_delete=models.CASCADE)
    data = models.JSONField('使用JSON表示额外的数据， 其格式根据type来变化')
    read = models.BooleanField('用户是否已读该通知', default=False)
    sender = models.ForeignKey(UserProfile, on_delete=SET_NULL, null=True,
                               related_name='%(class)s_sender')

    # 列出所有类型，防止打错字
    REPLY = 'REPLY'
    CENSOR = 'CENSOR'
    DECENSOR = 'DECENSOR'
    FAVOURITE = 'FAVORITE'  # 这里确实拼错了，但它已经进数据库和接口了，没法改
    # End

    notificationTypeChoices = [
        (REPLY, '回复'),
        (CENSOR, '屏蔽'),
        (DECENSOR, '解除屏蔽'),
        (FAVOURITE, '收藏'),
    ]
    type = CharField('通知类型', choices=notificationTypeChoices, max_length=100)

    time = models.DateTimeField('通知的创建时间', default=now)


class FavouritePost(models.Model):
    """
    帖子收藏
    """

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['userId', 'postId'], name='userId_postId')
        ]


class Report(models.Model):
    """
    帖子举报
    """

    createdBy = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                                  related_name='%(class)s_created_by')

    targetPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.TextField('举报原因', max_length=1000)  # TODO: 决定一个长度

    resolved = models.BooleanField('是否已处理', default=False)
    resolvedBy = models.ForeignKey(UserProfile, null=True, on_delete=models.SET_NULL,
                                   related_name='%(class)s_resolved_by')

    # 列出所有类型，防止打错字
    SPAM = 'SPAM'
    FALSE_INFORMATION = 'FALSE_INFORMATION'
    PERSONAL_ATTACK = 'PERSONAL_ATTACK'
    PLAGIARISM = 'PLAGIARISM'
    HATRED = 'HATRED'
    ILLEGAL = 'ILLEGAL'

    reportTypeChoices = [
        (SPAM, r'垃圾/恶意营销'),
        (FALSE_INFORMATION, r'不实/有害消息'),
        (PERSONAL_ATTACK, r'人身攻击'),
        (PLAGIARISM, r'内容抄袭'),
        (HATRED, r'宣扬仇恨'),
        (ILLEGAL, r'违法内容'),
    ]
    type = CharField('举报类型', choices=reportTypeChoices, max_length=100)

    class Meta:
        permissions = (
            ("can_handle_report", "Can handle report"),
        )


class UserInformation(models.Model):
    """
    圈子API里专用的用户数据。

    比如下面的用户名和头像就是只在圈子里用的。
    """

    USERNAME_MAX_LENGTH = 30

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True,
                                verbose_name='用户的id')

    username = models.CharField('用户名', max_length=USERNAME_MAX_LENGTH)
    avatarUrl = models.URLField('用户头像的url')


class WxMiniProgramData(models.Model):
    """
    微信小程序的全局数据。比如 access_token。
    """

    class Type(models.IntegerChoices):
        ACCESS_TOKEN = 1

    # 用int当作主键，提升检索效率
    type = models.IntegerField(
        choices=Type.choices, primary_key=True, verbose_name="数据类型")

    data = models.JSONField(null=False, verbose_name="数据")

    @property
    def access_token(self) -> Dict:
        """
        Get access token.

        The type must be Type.ACCESS_TOKEN !
        """
        assert self.type == WxMiniProgramData.Type.ACCESS_TOKEN, 'Type must match'
        return self.data
