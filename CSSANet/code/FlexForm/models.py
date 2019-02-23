from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from UserAuthAPI import models as userModels
import uuid
import django.utils.timezone as timezone

# Create your models here.


class FlexForm(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(verbose_name=_("表单标题"),max_length=100, unique=True)
    disabled = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('myCSSAhub:FlexForm:add_form_field', kwargs={"formid": self.pk})
    

class FlexFormField(models.Model):
    typeChoice = (
        ('text', 'text'),
        ('digit', 'digit'),
    )
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    form = models.ForeignKey(FlexForm, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_("字段名称"), max_length=100)
    field_type = models.CharField(verbose_name=_("字段类型"), max_length=10, choices=typeChoice)
    max_len = models.IntegerField(verbose_name=_("字数上限"), validators=[MaxValueValidator(2000),])
    disabled = models.BooleanField(default=False)
    

class FlexFormData(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(userModels.User, on_delete=models.CASCADE)
    field = models.ForeignKey(FlexFormField, on_delete=models.PROTECT)

    value = models.CharField(max_length=2000)