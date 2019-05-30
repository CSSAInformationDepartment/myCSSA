from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now as sys_now_time
from django.core.exceptions import ValidationError
from uuid import uuid4

from UserAuthAPI import models as UserModels
# Create your models here.
 

class MailDraft(models.Model):
    '''
    PostmanAPI Model - Store the Draft of a mail
    
    Le (Josh). Lu APR242019
    '''
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    disabled = models.BooleanField(default=False)
    author = models.ForeignKey(UserModels.UserProfile, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(verbose_name=_("创建时间"), auto_now_add=True)
    date_updated = models.DateTimeField(verbose_name=_("上次更新"), auto_now=True)
    title = models.CharField(verbose_name=_("标题"), max_length=100)
    html_body = models.TextField(verbose_name=_("正文"), default=None, null=True)
    is_pure_text = models.BooleanField(default=False)

    def _get_mail_attachments(self):
        return MailAttachments.objects.filter(id=self.id)

    def __str__(self):
        return self.title

class MailAttachments(models.Model):
    '''
    PostmanAPI Model - Store the Attachments of a mail draft
    
    Le (Josh). Lu APR242019
    '''
    FILE_TYPE = (
        ('CSS','CSS'),
        ('IMAGE','IMAGE'),
        ('VIDEO','VIDEO'),
        ('DOCUMENT','DOCUMENT'),
    )
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    related_mail = models.ForeignKey(MailDraft, verbose_name=_("关联邮件"), on_delete=models.CASCADE)
    date_created = models.DateTimeField(verbose_name=_("创建时间"), auto_now_add=True)
    file_name = models.CharField(verbose_name=_("文件名"), max_length=256)
    file_type = models.CharField(verbose_name=_("文件类型"), max_length=10, choices=FILE_TYPE)
    file = models.FileField(verbose_name=_("文件"), upload_to="public/email/attachments/%Y/%m/%d/")

    def __str__(self):
        return self.file_name


class MailQuene(models.Model):
    '''
    PostmanAPI Model - The mail quene that handle mail sending
    
    Le (Josh). Lu APR242019
    '''
    PRIORITY = (
        (0, _('LOW')),
        (1, _('NORMAL')),
        (2, _('HIGH')),
    )

    STATUS = (
        (-1, _('Failed')),
        (0, _('On Quene')),
        (1, _('Sending')),
        (2, _('Success')),
    )

    id = models.AutoField(primary_key=True, editable=False)
    date_created = models.DateTimeField(verbose_name=_("创建时间"), auto_now_add=True)
    date_scheduled = models.DateTimeField(verbose_name=_("设定发送时间"), default = sys_now_time)
    receiver = models.EmailField(verbose_name=_("收件人"))
    title = models.CharField(verbose_name=_("标题"), max_length=100)
    mail_text = models.TextField(verbose_name=_("邮件正文"), default=None, blank=True, null=True)
    mail_html = models.TextField(verbose_name=_("邮件HTML"), default=None, blank=True, null=True)
    priorty = models.IntegerField(verbose_name=_("优先级"), choices=PRIORITY, default=1)
    state = models.IntegerField(verbose_name=_("发送状态"), choices=STATUS, default=0)
    disabled = models.BooleanField(default=False)

    def _send_init(self):
        if not self.disabled and self.state in (0,-1):
            self.state = 1
            self.save()
        else:
            raise ValidationError(_("This mail quene has been disabled! Please contact system admin for more details"), 
                code="Disabled mail quene")

    def _send_failed(self):
        if self.state != 1:
            self.state = -1
            self.save()
    
    def _send_success(self):
        self.state = 2
        self.save()
