from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from UserAuthAPI import models as userModels
import uuid
import django.utils.timezone as timezone

# Create your models here.
def _GetFormUploadsDir(instance, filename):
    return 'user_{0}/{1}/{2}'.format(instance.user.id, instance.field.form.name, filename)

class FlexForm(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(verbose_name=_("表单标题"),max_length=100, unique=True)
    disabled = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('myCSSAhub:FlexForm:add_form_field', kwargs={"formid": self.pk})
    

class FlexFormField(models.Model):
    typeChoice = (
        (_('文本'), 'text'),
        (_('数字'), 'digit'),
        (_('文件'), 'file'),
        (_('日期'), 'date'),
        (_('时间'), 'time'),
        
    )
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    form = models.ForeignKey(FlexForm, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_("字段名称"), max_length=100)
    field_type = models.CharField(verbose_name=_("字段类型"), max_length=10, choices=typeChoice)
    max_len = models.IntegerField(verbose_name=_("字数上限"), validators=[MaxValueValidator(2000),])
    is_required = models.BooleanField(verbose_name=_("是否为必填项？"), default=False)
    disabled = models.BooleanField(default=False)
    

class FlexFormData(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(userModels.UserProfile, on_delete=models.CASCADE)
    field = models.ForeignKey(FlexFormField, on_delete=models.PROTECT)

    ## 文本/数字 输入
    value = models.CharField(max_length=2000)

    ## 日期 输入
    date_value = models.DateField(default=None, blank=True, null=True)

    ## 时间 输入
    time_value = models.TimeField(default=None, blank=True, null=True)

    ## 文件 输入
    file_input = models.FileField(default=None, null=True, blank=True, upload_to=_GetFormUploadsDir)