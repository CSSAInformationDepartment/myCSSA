from django.contrib.postgres.fields import JSONField
from django.db import models
from UserAuthAPI.models import User

# Create your models here.


class HttpAccessLogModel(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    time_stamp = models.DateTimeField(auto_now_add=True)
    visitor_ipv4 = models.GenericIPAddressField()
    is_anonymous = models.BooleanField(default=True)
    user = models.ForeignKey(
        User, default=None, blank=True, null=True, on_delete=models.CASCADE)

    request_path = models.TextField()
    request_query_string = models.TextField(default=None, null=True)
    request_method = models.CharField(max_length=10)
    status_code = models.CharField(max_length=3, default='200')
    request_META = JSONField(default=dict)
    # response_host_ipv4 = models.GenericIPAddressField()
