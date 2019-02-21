from django.db import models
from django.core.validators import MaxValueValidator
from UserAuthAPI import models as userModels
import uuid
import django.utils.timezone as timezone

# Create your models here.


class FlexForm(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length=100, unique=True)
    disabled = models.BooleanField(default=False)

class FlexFormField(models.Model):
    typeChoice = (
        ('text', 'text'),
        ('digit', 'digit'),
    )
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    form = models.ForeignKey(FlexForm, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    field_type = models.CharField(max_length=10, choices=typeChoice)
    max_len = models.IntegerField(validators=[MaxValueValidator(2000),])
    disabled = models.BooleanField(default=False)
    

class FlexFormData(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(userModels.User, on_delete=models.CASCADE)
    field = models.ForeignKey(FlexFormField, on_delete=models.PROTECT)

    value = models.CharField(max_length=2000)