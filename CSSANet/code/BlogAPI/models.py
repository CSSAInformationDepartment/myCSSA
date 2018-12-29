from django.db import models
import sys
sys.path.append("..")

from UserAuthAPI.models import User

# Create your models here.

# 新闻本身
class Blog (models.Model):
    blogId = models.AutoField(primary_key = True)
    blogTitle = models.CharField(max_length = 100)
    blogMainContent = models.TextField()

    # 阅读量
    blogReads = models.IntegerField()

class BlogWrittenBy(models.Model):
    blogCreatedId = models.AutoField(primary_key = True)
    blogId = models.ForeignKey(Blog, on_delete = models.CASCADE)
    userId = models.ForeignKey(User, on_delete = models.DO_NOTHING)
    writtenDate = models.DateTimeField(auto_now_add=True)

