from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm

from django.views import View
from django.views.generic import CreateView, UpdateView, FormView
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from UserAuthAPI import models as UserModels
from BlogAPI import models as BlogModels
from UserAuthAPI.forms import BasicSiginInForm, UserInfoForm, MigrationForm, UserAcademicForm, UserProfileUpdateForm
from LegacyDataAPI import models as LegacyDataModels

from CSSANet.settings import MEDIA_ROOT, MEDIA_URL
from Library.Mixins import AjaxableResponseMixin
import json
import base64
import io
import hashlib

from urllib import parse

from django.core.files import File

import datetime

# Create your views here.

class editBlog (LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.blog.add_blog", "BlogAPI.blog.change_blog", "BlogAPI.blog.delete_blog", 
    )

    def get(self, request, *args, **kwargs):
    # 需要判断contentId
    # avatar没有的时候会报错

        NEW_BLOG = -1

        CR_BLOG = "创建Blog"
        CH_BLOG = "更改Blog"
        blogId = request.GET["blogId"]
        try:
            blogId = int(blogId)
        except:
            return bad_request(request)

        print(blogId)
        ViewBag = {}

        userAuthed = request.user.is_authenticated


        print(request.user.email)
        if not userAuthed:
            return bad_request(request)

        blogContentSingle = -1
        blogTitle = ""
        blogMainContent = ""


        if blogId != NEW_BLOG:
            blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blogId)
            wrote = False
            if blogWrittenBys:
                for blogWrittenBy in blogWrittenBys:
                    if userAuthed and blogWrittenBy.userId == request.user:
                        wrote = True
                    

                # user没有写blog
                if wrote == False:
                    return permission_denied(request)
            blog = BlogModels.Blog.objects.filter(blogId=blogId)
            if not blog:
                return bad_request(request)
            blogContentSingle = blog[0]
            blogTitle = blogContentSingle.blogTitle
            blogMainContent = blogContentSingle.blogMainContent
            ViewBag["toolTitle"] = CH_BLOG
            curBlogTag = BlogModels.BlogInTag.objects.filter(blogId=blog[0])
            blogTag = json.dumps([x.tagId.tagName for x in curBlogTag]).replace("\\", "\\\\")

            ViewBag["blogTag"] = blogTag
        else:
            ViewBag["toolTitle"] = CR_BLOG

            ViewBag["blogTag"] = []
            pass

        ViewBag["blogId"] = blogId
        ViewBag["blogTitle"] = blogTitle
        ViewBag["blogMainContent"] = blogMainContent


        
        return render(request, 'myCSSAhub/blogeditpage.html', ViewBag)

    def post(self, request, *args, **kwargs):
        return page_not_found(request)


class saveBlog (LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.blog.add_blog", "BlogAPI.blog.change_blog", "BlogAPI.blog.delete_blog", 
    )

    def storeToBlogOldContent(self, oldBlog):
        MAX_HIST = 5
        oldBlogs = BlogModels.BlogOldContent.objects.filter(blogId = oldBlog).order_by("writtenDate")
        print(len(oldBlogs))
        if len(oldBlogs) >= MAX_HIST:
            oldBlogs[0].delete()

        newOldBlog = BlogModels.BlogOldContent(
            blogId = oldBlog,
            blogOldTitle = oldBlog.blogTitle,
            blogOldContent = oldBlog.blogMainContent,
            writtenDate = oldBlog.lastModifiedDate
        )

        newOldBlog.save()

    def addTagsToBlog(self, blog, tags):
        tags = [x[:18] for x in tags]
        curBlogTags = BlogModels.BlogInTag.objects.filter(blogId=blog)
        for tagInBlog in curBlogTags:
            if not (tagInBlog.tagId.tagName in tags):
                tagInBlog.delete()
            else:

                tags.remove(tagInBlog.tagId.tagName)
        
        for tag in tags:
            blogTagReal = ""
            blogTag = BlogModels.BlogTag.objects.filter(tagName=tag)
            if blogTag:
                blogTagReal = blogTag[0]
            else:
                blogTagReal = BlogModels.BlogTag(
                    tagName = tag
                )
                blogTagReal.save()
            
            newBlogInTag = BlogModels.BlogInTag(
                blogId = blog,
                tagId = blogTagReal
            )
            newBlogInTag.save()

    def getContent(self, blogMainContent):
        dicContent = json.loads(blogMainContent.replace("(ffffhhhhccccc)", ";").replace(" ", "+"))

        for content in range(len(dicContent["ops"])):
            print(dicContent["ops"][content])
            if type(dicContent["ops"][content]["insert"]) == dict:
                if ("image" in dicContent["ops"][content]["insert"]):
                    try:
                        imB64 = dicContent["ops"][content]["insert"]["image"]
                        imB64 = imB64.split(",")[1]
                        print(len(imB64))
                        imB64bs = base64.b64decode(imB64)
                        imB64Bytes = io.BytesIO(imB64bs)
                        hashmm = hashlib.md5()
                        hashmm.update(imB64bs)
                        hashedImage = hashmm.hexdigest()

                        extEndsIn = dicContent["ops"][content]["insert"]["image"].index(";")
                        ext = dicContent["ops"][content]["insert"]["image"][11: extEndsIn]

                        storedImage = BlogModels.BlogImage.objects.filter(hashValue=hashedImage)
                        if storedImage:
                            print("found duplicated picture")
                            dicContent["ops"][content]["insert"]["image"] = storedImage[0].imageFileB64.url
                        else:
                            newImage = BlogModels.BlogImage(
                                hashValue=hashedImage,
                            )
                            newImage.save()
                            newImage.imageFileB64.save(str(newImage.imageId) + "." + ext, imB64Bytes)
                            newImage.save()
                            dicContent["ops"][content]["insert"]["image"] = newImage.imageFileB64.url
                    except IndexError:
                        pass
        print(json.dumps(dicContent).replace("\\", "\\\\"))
        return json.dumps(dicContent).replace("\\", "\\\\")


    def get(self, request, *args, **kwargs):
        data = {
            'status': '400', 'reason': 'Bad Requests!'
        }
        return data
        
    def post(self, request, *args, **kwargs):
        # 检查是否是新content
        # 如果不是新content 检查是否 user对

        # post: blogId contentid blogtitle blogopentopublic

        NEW_BLOG = -1
        try:
            blogId = int(request.POST["blogId"])
        except:
            return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blog id"
                })

        print(blogId)
        blog = -1

        userAuthed = request.user.is_authenticated

        if blogId != NEW_BLOG:
            blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blogId)
            wrote = False
            if blogWrittenBys:
                for blogWrittenBy in blogWrittenBys:
                    if userAuthed and blogWrittenBy.userId == request.user:
                        wrote = True
                
                # user没有写blog
                if wrote == False:
                    return JsonResponse({
                        'success': False,
                        'status': '400',
                        'message': 'user is not the author'
                    })
                
                blog = BlogModels.Blog.objects.get(blogId=blogId)
                self.storeToBlogOldContent(blog)
                blogMainContent = self.getContent(request.POST["blogMainContent"])
                blogOpen = request.POST["openOrNot"]
                try:
                    blogOpen = {"true": True, "false": False}[blogOpen]
                    print(blogOpen)
                except:
                    return JsonResponse({
                        'success': False,
                        'status': '400',
                        'message': "wrong openOrNot"
                    })
                blog = BlogModels.Blog(
                    blogId=blogId,
                    blogTitle=request.POST["blogTitle"][:100],
                    createDate=blog.createDate,
                    lastModifiedDate=datetime.datetime.now(),
                    blogReviewed = False,
                    blogReads = blog.blogReads,
                    blogMainContent = blogMainContent,
                    blogOpen = blogOpen
                )
                blog.save()

                blogTags = json.loads(request.POST["tag"].replace("(ffffhhhhccccc)", ";"))
                self.addTagsToBlog(blog, blogTags)
                print(blogId)

                return JsonResponse({
                        'success': True,
                        'status': '200',
                        'message': 'modified'
                    })


            else:
                # blogId有问题
                return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blog id"
                })
        
        else:
            if userAuthed:

                print(request.POST["blogMainContent"])
                blogMainContent = self.getContent(request.POST["blogMainContent"])
                blogOpen = request.POST["openOrNot"]
                try:
                    blogOpen = {"true": True, "false": False}[blogOpen]
                    print(blogOpen)
                except:
                    return JsonResponse({
                        'success': False,
                        'status': '400',
                        'message': "wrong openOrNot"
                    })
                print(type(blogOpen) == bool)
                blog = BlogModels.Blog(
                    blogTitle=request.POST["blogTitle"][:100],
                    lastModifiedDate=datetime.datetime.now(),
                    createDate=datetime.datetime.now(),
                    blogReviewed = False,
                    blogReads = 0,
                    blogMainContent = blogMainContent,
                    blogOpen = blogOpen
                )
                blog.save()

                blogWrittenBy = BlogModels.BlogWrittenBy(
                    blogId = blog,
                    userId = request.user
                )
                blogWrittenBy.save()

                blogTags = json.loads(request.POST["tag"].replace("(ffffhhhhccccc)", ";"))
                self.addTagsToBlog(blog, blogTags)

                return JsonResponse({
                        'success': True,
                        'status': '200',
                        'message': 'created'
                    })
            else:
                # 游客禁止发blog
                return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': 'visitor is not permitted to create'
                })

class deleteBlog(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.can_add_blog", "BlogAPI.can_change_blog", "BlogAPI.can_delete_blog",)

    def get(self, request, *args, **kwargs):

        try:
            blogId = int(request.GET["blogId"])
        except:
            return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blog id"
                })

        print(blogId)
        blog = -1

        userAuthed = request.user.is_authenticated

        blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blogId)
        wrote = False
        if blogWrittenBys:
            for blogWrittenBy in blogWrittenBys:
                if userAuthed and blogWrittenBy.userId == request.user:
                    wrote = True
                
            # user没有写blog
            if wrote == False:
                return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': 'user is not the author'
                })
                
            blog = BlogModels.Blog.objects.get(blogId=blogId)
            blog.delete()

            return JsonResponse({
                    'success': True,
                    'status': '200',
                    'message': 'deleted'
                })


        else:
                # blogId有问题
            return JsonResponse({
                'success': False,
                'status': '400',
                'message': "wrong blog id"
            })

    def post(self, request, *args, **kwargs):
        # 检查是否是新content
        # 如果不是新content 检查是否 user对

        # post: blogId contentid blogtitle blogopentopublic


        data = {
            'status': '400', 'reason': 'Bad Requests!'
        }
        return data

def bad_request(request):
    return render(request, 'errors/page_400.html')


def permission_denied(request):
    return render(request, 'errors/page_403.html')


def page_not_found(request):
    return render(request, 'errors/page_404.html')


def server_error(request):
    return render(request, 'errors/page_500.html')

def under_dev_notice(request):
    return render(request, 'myCSSAhub/under-dev-function.html')