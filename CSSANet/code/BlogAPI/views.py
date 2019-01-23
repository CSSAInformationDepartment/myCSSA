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
    permission_required = ("BlogAPI.add_blog", "BlogAPI.change_blog", "BlogAPI.delete_blog", 
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

        ViewBag["versions"] = []


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
            # access version history
            oldBlogs = BlogModels.BlogOldContent.objects.filter(blogId = blogId).order_by("writtenDate")
            ViewBag["versions"] = [[i, oldBlogs[i]] for i in range(len(oldBlogs))]
            blog = BlogModels.Blog.objects.filter(blogId=blogId)
            if "version" in request.GET:
                
                try:
                    version = int(request.GET["version"])
                except:
                    return bad_request(request)



                if version > len(oldBlogs) or version < 0:
                    return page_not_found(request)

                ViewBag["toolTitle"] = CR_BLOG + " 版本: " + oldBlogs[version].writtenDate.ctime()

                ViewBag["curVersion"] = oldBlogs[version]
                ViewBag["isHistory"] = True
                blogTitle = oldBlogs[version].blogOldTitle
                blogMainContent = oldBlogs[version].blogOldContent


            else:
                if not blog:
                    return bad_request(request)
                blogContentSingle = blog[0]
                blogTitle = blogContentSingle.blogTitle
                blogMainContent = blogContentSingle.blogMainContent
                ViewBag["toolTitle"] = CH_BLOG
                ViewBag["isHistory"] = False
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
    permission_required = ("BlogAPI.add_blog", "BlogAPI.change_blog", "BlogAPI.delete_blog", 
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
        gotFirstPic = False
        picExt = ""
        
        stPic = ""

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
                        extEndsIn = dicContent["ops"][content]["insert"]["image"].index(";")
                        hashmm = hashlib.md5()
                        hashmm.update(imB64bs)
                        hashedImage = hashmm.hexdigest()

                        ext = dicContent["ops"][content]["insert"]["image"][11: extEndsIn]

                        storedImage = BlogModels.BlogImage.objects.filter(hashValue=hashedImage)
                        if storedImage:
                            print("found duplicated picture")
                            dicContent["ops"][content]["insert"]["image"] = storedImage[0].imageFileB64.url
                            if not gotFirstPic:
                                stPic = storedImage[0].imageFileB64.url

                                gotFirstPic = True
                        else:
                            newImage = BlogModels.BlogImage(
                                hashValue=hashedImage,
                            )
                            newImage.save()
                            newImage.imageFileB64.save(str(newImage.imageId) + "." + ext, imB64Bytes)
                            newImage.save()
                            if not gotFirstPic:
                                stPic = newImage.imageFileB64.url

                                gotFirstPic = True
                            dicContent["ops"][content]["insert"]["image"] = newImage.imageFileB64.url
                    except IndexError:
                        if not gotFirstPic:
                            stPic = dicContent["ops"][content]["insert"]["image"]


                            gotFirstPic = True
                        pass
        return json.dumps(dicContent).replace("\\", "\\\\"), stPic


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
                contented = self.getContent(request.POST["blogMainContent"])
                blogMainContent = contented[0]
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
                    blogReviewed = 0,
                    blogReads = blog.blogReads,
                    blogMainContent = blogMainContent,
                    blogOpen = blogOpen,
                    blogTopPic = contented[1]
                )
                blog.save()
                print(contented[1])

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
                contented = self.getContent(request.POST["blogMainContent"])
                blogMainContent = contented[0]
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
                    blogReviewed = 0,
                    blogReads = 0,
                    blogMainContent = blogMainContent,
                    blogOpen = blogOpen,
                    blogTopPic = contented[1]
                )
                blog.save()
                print(contented[1])

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

class writtenBlogs(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.add_blog", "BlogAPI.change_blog", "BlogAPI.delete_blog")

    def get(self, request):
        ViewBag = {}
        userAuthed = request.user.is_authenticated

        if userAuthed:

            ViewBag["writtenOrReview"] = True
            blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(userId=request.user)
            ViewBag["blogs"] = [blogWritten.blogId for blogWritten in blogWrittenBys][::-1]



            return render(request, "myCSSAhub/blogLess.html", ViewBag)
        else:
            return page_not_found(request)

class reviewBlogs(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"

    # review permission
    permission_required = ("BlogAPI.add_blogreviewed", "BlogAPI.delete_blogreviewed",)

     
    def get(self, request):
        ViewBag = {}
        userAuthed = request.user.is_authenticated

        if userAuthed:


            ViewBag["writtenOrReview"] = False
            blog = BlogModels.Blog.objects.filter(blogReviewed=0, blogOpen=True)
            ViewBag["blogs"] = blog[::-1]


            return render(request, "myCSSAhub/blogLess.html", ViewBag)
        else:
            return page_not_found(request)

        



class reviewBlogAjax(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.add_blogreviewed", "BlogAPI.delete_blogreviewed", 
    )

    def get(self, request, *args, **kwargs):

        try:
            blogId = int(request.GET["blogId"])
            blogReviewStatus = int(request.GET["blogReviewStatus"])
        except:

            return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blog id"
                })

        

        if blogReviewStatus > 2:
            return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blogReviewStatus"
                })

        print(blogId)
        blog = -1

        userAuthed = request.user.is_authenticated


        print(blogId)

        if userAuthed: 
            # create reviewed
            blog = BlogModels.Blog.objects.filter(blogId=blogId)
            print(blogId)
            if blog:
                blogTmp = BlogModels.Blog(
                    blogId=blog[0].blogId,
                    blogTitle=blog[0].blogTitle,
                    lastModifiedDate=blog[0].lastModifiedDate,
                    createDate=blog[0].createDate,
                    blogReviewed = blogReviewStatus,
                    blogReads = 0,
                    blogMainContent = blog[0].blogMainContent,
                    blogOpen = blog[0].blogOpen,
                    blogTopPic = blog[0].blogTopPic
                )
                blogTmp.save()
                print(blog[0])

                return JsonResponse({
                        'success': True,
                        'status': '200',
                        'message': 'reviewed'
                    })

            else:
                    # blogId有问题
                return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blog id"
                })
        else:
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


class deleteBlog(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.add_blog", "BlogAPI.change_blog", "BlogAPI.delete_blog",)

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