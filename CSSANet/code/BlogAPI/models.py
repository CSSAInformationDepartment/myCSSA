from django.db import models
import sys
sys.path.append("..")

from UserAuthAPI.models import User

# Create your models here.

# 新闻本身
class Blog (models.Model):
    blogId = models.AutoField(primary_key = True)
    blogTitle = models.CharField(max_length = 100)

    blogMainContent = models.TextField(default=None)
    createDate = models.DateTimeField(auto_now_add=True)
    lastModifiedDate = models.DateTimeField(auto_now=True)
    blogReviewed = models.BooleanField(default=False)

    # 阅读量
    blogReads = models.IntegerField(default=0)

class BlogOldContent (models.Model):
    blogId = models.ForeignKey(Blog, on_delete = models.CASCADE)
    blogOldContentId = models.AutoField(primary_key = True)
    blogOldTitle = models.CharField(max_length = 100)
    blogOldContent = models.TextField()
    writtenDate = models.DateTimeField(auto_now_add=True)
    # writeIn = models.CharField(max_length = 45)

class BlogWrittenBy(models.Model):
    blogCreatedId = models.AutoField(primary_key = True)
    blogId = models.ForeignKey(Blog, on_delete = models.CASCADE)
    userId = models.ForeignKey(User, on_delete = models.DO_NOTHING)

class BlogTag (models.Model):
    tagId = models.AutoField(primary_key = True)
    tagName = models.CharField(max_length = 18)
    tagCreateTime = models.DateTimeField(auto_now_add = True)

class BlogInTag (models.Model):
    blogId = models.ForeignKey(Blog, on_delete = models.CASCADE)
    tagId = models.ForeignKey(BlogTag, on_delete = models.CASCADE)
    blogTagId = models.AutoField(primary_key = True)

class BlogImage (models.Model):
    imageId = models.AutoField(primary_key = True)
    hashValue = models.CharField(max_length = 40)

    # 目前先存base64 在上传之后检查是否有重复
    # 改成imageField?
    imageFileB64 = models.TextField()