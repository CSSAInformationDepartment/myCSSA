from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.


class PublicAccessControl(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    uri = models.CharField(max_length=500)
    is_accessible = models.BooleanField(default=False)


class PageRegister(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp_create = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    uri = models.CharField(max_length=256)
    title = models.CharField(max_length=100)
    templates = models.CharField(max_length=200, default=None)

    def __str__(self):
        return self.title + '-' + self.uri


class HTMLFields(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    timestamp_create = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    PageId = models.ManyToManyField(PageRegister)
    elementType = (
        ('text', 'text'),
        ('html', 'html'),
        ('img', 'img'),
        ('video', 'video'),
        ('iFrame', 'iFrame')
    )
    fieldType = models.CharField(max_length=10, choices=elementType, null=True)
    fieldName = models.CharField(max_length=256)
    fieldClass = models.CharField(max_length=256)
    fieldInnerText = models.TextField(null=True, blank=True)
    fieldContentSrc = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.fieldName + '-' + str(self.id)


class ImgAttributes(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    timestamp_create = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    RelatedField = models.ForeignKey(HTMLFields, on_delete=models.DO_NOTHING)
    filePath = models.FileField(upload_to='uploads/usrImage/')
    styleAttr = models.TextField(null=True, blank=True)


class HomepageCarousels(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    url = models.URLField(verbose_name=_('页面链接'))
    filePath = models.FileField(verbose_name=_(
        '图片'), upload_to='site/homepage/carousel/')
    header = models.CharField(verbose_name=_('大标题'), max_length=35)
    description = models.CharField(verbose_name=_('大标题'), max_length=100)
