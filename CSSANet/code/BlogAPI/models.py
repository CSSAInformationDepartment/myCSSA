from django.db import models
import sys
sys.path.append("..")

from UserAuthAPI.models import User

# Create your models here.

# 新闻本身
class BlogDescription (models.Model):
    blogId = models.AutoField(primary_key = True)
    blogTitle = models.CharField(max_length = 100)

    # 阅读量
    blogReads = models.IntegerField()

class BlogContent (models.Model):
    blogId = models.ForeignKey(BlogDescription, on_delete = models.CASCADE)
    blogContentId = models.AutoField(primary_key = True)
    blogMainContent = models.TextField()
    writtenDate = models.DateTimeField(auto_now_add=True)


class BlogWrittenBy(models.Model):
    blogCreatedId = models.AutoField(primary_key = True)
    blogContentId = models.ForeignKey(BlogContent, on_delete = models.CASCADE)
    userId = models.ForeignKey(User, on_delete = models.DO_NOTHING)

class BlogTag (models.Model):
    tagId = models.AutoField(primary_key = True)
    tagName = models.CharField(max_length = 18)
    tagCreateTime = models.DateTimeField(auto_now_add = True)

class BlogInTag (models.Model):
    blogId = models.ForeignKey(BlogDescription, on_delete = models.CASCADE)
    tagId = models.ForeignKey(BlogTag, on_delete = models.CASCADE)
    blogTagId = models.AutoField(primary_key = True)

