import sys

from django.db import models
from UserAuthAPI.models import UserProfile

sys.path.append("..")


# Create your models here.

# 新闻本身

class Blog (models.Model):
    blogId = models.AutoField(primary_key=True)
    blogTitle = models.CharField(max_length=100)

    blogMainContent = models.TextField(default=None)
    createDate = models.DateTimeField()
    lastModifiedDate = models.DateTimeField(auto_now=True)

    blogReviewed = models.SmallIntegerField(default=0)
    # blogReviewed 取值说明
    # 0 ->  未审核
    # 1 ->  审核不通过
    # 2 ->  审核通过

    blogOpen = models.BooleanField(default=True)

    blogTopPic = models.CharField(max_length=95)

    # 阅读量
    blogReads = models.IntegerField(default=0)

    def __str__(self):
        return self.blogTitle


class BlogOldContent (models.Model):
    blogId = models.ForeignKey(Blog, on_delete=models.CASCADE)
    blogOldContentId = models.AutoField(primary_key=True)
    blogOldTitle = models.CharField(max_length=100)
    blogOldContent = models.TextField()
    writtenDate = models.DateTimeField(default=None)
    # writeIn = models.CharField(max_length = 45)


class BlogWrittenBy(models.Model):
    blogCreatedId = models.AutoField(primary_key=True)
    blogId = models.ForeignKey(Blog, on_delete=models.CASCADE)
    userId = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)


class BlogTag (models.Model):
    tagId = models.AutoField(primary_key=True)
    tagName = models.CharField(max_length=18)
    tagCreateTime = models.DateTimeField(auto_now_add=True)


class BlogInTag (models.Model):
    blogId = models.ForeignKey(Blog, on_delete=models.CASCADE)
    tagId = models.ForeignKey(BlogTag, on_delete=models.CASCADE)
    blogTagId = models.AutoField(primary_key=True)


class BlogImage (models.Model):
    imageId = models.AutoField(primary_key=True)
    hashValue = models.CharField(max_length=40)

    # 目前先存base64 在上传之后检查是否有重复
    # 改成imageField?
    imageFileB64 = models.ImageField(upload_to='blog/blogpics', height_field=None, width_field=None,
                                     blank=True, null=True)


class BlogReviewed (models.Model):

    reviewedId = models.AutoField(primary_key=True)
    blogId = models.ForeignKey(Blog, on_delete=models.CASCADE)
    userId = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
