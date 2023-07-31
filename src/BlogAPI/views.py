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
from UserAuthAPI.forms import BasicSiginInForm, UserInfoForm, MigrationForm, UserProfileUpdateForm
from LegacyDataAPI import models as LegacyDataModels

from Library.Mixins import AjaxableResponseMixin
import json
import base64
import io
import hashlib

import urllib.parse

from django.core.files import File

import datetime

# Create your views here.

def checkUserWrittenBlog(userAuthed, user, blog):
    blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blog)
    wrote = False
    if blogWrittenBys:
        for blogWrittenBy in blogWrittenBys:
            if userAuthed and blogWrittenBy.userId == user:
                wrote = True

    return wrote

# View for blog edit page
class editBlog (LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.add_blog", "BlogAPI.change_blog", "BlogAPI.delete_blog", 
    )

    def get(self, request, *args, **kwargs):

        NEW_BLOG = -1

        CR_BLOG = "创建Blog"
        CH_BLOG = "更改Blog"

        # check if blogId exists, and check if the blogId we got is a valid number
        blogId = request.GET["blogId"]
        try:
            blogId = int(blogId)
        except:
            return bad_request(request)

        ViewBag = {}

        userAuthed = request.user.is_authenticated

        # if user hasnt logged in
        if not userAuthed:
            return bad_request(request)


        blogContentSingle = -1
        blogTitle = ""
        blogMainContent = ""

        # history versions
        ViewBag["versions"] = []

        # if now editing existing blog
        if blogId != NEW_BLOG:

            '''# check if the logged in user is the one who created the original blog
            blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blogId)
            wrote = False
            if blogWrittenBys:
                for blogWrittenBy in blogWrittenBys:
                    if userAuthed and blogWrittenBy.userId == request.user:
                        wrote = True

                # user is not the writer
                if wrote == False:
                    return permission_denied(request)'''

            if not checkUserWrittenBlog(userAuthed, request.user, blogId):
                return permission_denied(request)


            # access version history
            oldBlogs = BlogModels.BlogOldContent.objects.filter(blogId = blogId).order_by("writtenDate")
            ViewBag["versions"] = [[i, oldBlogs[i]] for i in range(len(oldBlogs))]

            # find the list of blog that has id of blogId
            blog = BlogModels.Blog.objects.filter(blogId=blogId)
            
            # if user is requesting a history version
            if "version" in request.GET:
                try:
                    version = int(request.GET["version"])
                except:
                    return bad_request(request)

                # when version is not valid
                if version > len(oldBlogs) or version < 0:
                    return page_not_found(request)

                # change the title if now requesting history version
                ViewBag["toolTitle"] = CR_BLOG + " 版本: " + oldBlogs[version].writtenDate.ctime()

                # find current history version
                ViewBag["curVersion"] = oldBlogs[version]
                ViewBag["isHistory"] = True
                blogTitle = oldBlogs[version].blogOldTitle
                blogMainContent = oldBlogs[version].blogOldContent

            else:
                # requesting the latest one
                if not blog:
                    return bad_request(request)
                blogContentSingle = blog[0]

                blogTitle = blogContentSingle.blogTitle
                blogMainContent = blogContentSingle.blogMainContent
                ViewBag["toolTitle"] = CH_BLOG
                ViewBag["isHistory"] = False
            
            # returning tags
            curBlogTag = BlogModels.BlogInTag.objects.filter(blogId=blog[0])
            blogTag = json.dumps([x.tagId.tagName for x in curBlogTag]).replace("\\", "\\\\")

            ViewBag["blogTag"] = blogTag
        else:
            # creating new blog

            ViewBag["toolTitle"] = CR_BLOG
            ViewBag["blogTag"] = []
            pass

        ViewBag["blogId"] = blogId
        ViewBag["blogTitle"] = blogTitle
        ViewBag["blogMainContent"] = blogMainContent
        
        return render(request, 'myCSSAhub/blogeditpage.html', ViewBag)

    def post(self, request, *args, **kwargs):
        return page_not_found(request)


# ajax for saving blog after hitting the save button
class saveBlog (LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.add_blog", "BlogAPI.change_blog", "BlogAPI.delete_blog", 
    )

    # post request including char ';' '&' will be incurrectly analyzed
    # so in frontend we encoded these chars and need to decode here.
    def decodeSuckString(self, suckString):
        commaReplace = "(ffffhhhhccccc)"
        andReplace = "(andandand)"

        resultStr = suckString
        resultStr = resultStr.replace(commaReplace, ";")
        resultStr = resultStr.replace(andReplace, "&")
        resultStr = resultStr.replace(" ", "+")
        
        return resultStr

    # create history version of current blog
    def storeToBlogOldContent(self, oldBlog):

        # max history version size
        MAX_HIST = 5

        # delete the earliest history version
        oldBlogs = BlogModels.BlogOldContent.objects.filter(blogId = oldBlog).order_by("writtenDate")
        if len(oldBlogs) >= MAX_HIST:
            oldBlogs[0].delete()

        # create and save history version
        newOldBlog = BlogModels.BlogOldContent(
            blogId = oldBlog,
            blogOldTitle = oldBlog.blogTitle,
            blogOldContent = oldBlog.blogMainContent,
            writtenDate = oldBlog.lastModifiedDate
        )

        newOldBlog.save()

    def addTagsToBlog(self, blog, tags):

        # got new tags from request
        tags = [x[:18] for x in tags]
        curBlogTags = BlogModels.BlogInTag.objects.filter(blogId=blog)

        # if tag in old tags is not in new tags then remove
        # if tag in both new and old then delete it in new tags
        for tagInBlog in curBlogTags:
            if not (tagInBlog.tagId.tagName in tags):
                tagInBlog.delete()
            else:
                tags.remove(tagInBlog.tagId.tagName)
        
        # add new tags that dont exist in old tags
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

    # store images to the database and get the first
    def getContent(self, blogMainContent):

        # decode blogContent
        blogMainContent = urllib.parse.unquote(blogMainContent)
        blogMainContent = self.decodeSuckString(blogMainContent)
        dicContent = json.loads(blogMainContent)

        gotFirstPic = False
        picExt = ""
        stPic = ""

        for content in range(len(dicContent["ops"])):
            if type(dicContent["ops"][content]["insert"]) == dict:
                # got an image
                if ("image" in dicContent["ops"][content]["insert"]):
                    try:

                        # get base64 string of image
                        imB64 = dicContent["ops"][content]["insert"]["image"]
                        imB64 = imB64.split(",")[1]

                        # binary data of the image
                        imB64bs = base64.b64decode(imB64)
                        imB64Bytes = io.BytesIO(imB64bs)

                        # get the extension of the image (end index)
                        extEndsIn = dicContent["ops"][content]["insert"]["image"].index(";")

                        # hashing
                        hashmm = hashlib.md5()
                        hashmm.update(imB64bs)
                        hashedImage = hashmm.hexdigest()

                        # extension
                        ext = dicContent["ops"][content]["insert"]["image"][11: extEndsIn]

                        # see if the image is in database
                        storedImage = BlogModels.BlogImage.objects.filter(hashValue=hashedImage)

                        # store image if the image is new
                        if storedImage:
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
                    finally:

                        # always get the first image
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

        NEW_BLOG = -1

        # check if the blogId is valid
        try:
            blogId = int(request.POST["blogId"])
        except:
            return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blog id"
                })

        blog = -1

        userAuthed = request.user.is_authenticated

        if userAuthed:
            if blogId != NEW_BLOG:
                # check if user is the writter
                if not checkUserWrittenBlog(userAuthed, request.user, blogId):
                    return JsonResponse({
                                'success': False,
                                'status': '400',
                                'message': 'user is not the author or wrong blogId'
                            })
                
                # find blog and decode
                blog = BlogModels.Blog.objects.get(blogId=blogId)
                self.storeToBlogOldContent(blog)

            contented = self.getContent(request.POST["blogMainContent"])
            blogMainContent = contented[0]
            blogOpen = request.POST["openOrNot"]

            # see if blog opens to pub
            try:
                blogOpen = {"true": True, "false": False}[blogOpen]
            except:
                return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong openOrNot"
                })
            
            message = "you shouldnt see this message!"
            
            if blogId != NEW_BLOG:
                # modify
                blog = BlogModels.Blog(
                    blogId=blogId,
                    blogTitle=self.decodeSuckString(urllib.parse.unquote(request.POST["blogTitle"][:100])),
                    createDate=blog.createDate,
                    lastModifiedDate=datetime.datetime.now(),
                    blogReviewed = 0,
                    blogReads = blog.blogReads,
                    blogMainContent = blogMainContent,
                    blogOpen = blogOpen,
                    blogTopPic = contented[1]
                )
                blog.save()

                message = "blog modified"
            
            else:
                # create
                blog = BlogModels.Blog(
                    blogTitle=self.decodeSuckString(urllib.parse.unquote(request.POST["blogTitle"][:100])),
                    lastModifiedDate=datetime.datetime.now(),
                    createDate=datetime.datetime.now(),
                    blogReviewed = 0,
                    blogReads = 0,
                    blogMainContent = blogMainContent,
                    blogOpen = blogOpen,
                    blogTopPic = contented[1]
                )
                blog.save()

                blogWrittenBy = BlogModels.BlogWrittenBy(
                    blogId = blog,
                    userId = request.user
                )
                blogWrittenBy.save()

                message = "blog created"

            # decode tags and store them
            blogTags = json.loads(self.decodeSuckString(request.POST["tag"]))
            self.addTagsToBlog(blog, blogTags)

            return JsonResponse({
                    'success': True,
                    'status': '200',
                    'message': message
                })
            
        else:
            # visitors are not permitted
            return JsonResponse({
                'success': False,
                'status': '400',
                'message': 'visitor is not permitted to create'
            })

# get written blog list
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

# 
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


# ajax for reviewing blogs in reviewing page
class reviewBlogAjax(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.add_blogreviewed", "BlogAPI.delete_blogreviewed", 
    )

    def get(self, request, *args, **kwargs):

        # check if blog reviewing status is valid
        try:
            blogId = int(request.GET["blogId"])
            blogReviewStatus = int(request.GET["blogReviewStatus"])
        except:
            return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blog id"
                })

        if blogReviewStatus > 2 or blogReviewStatus < 0:
            return JsonResponse({
                    'success': False,
                    'status': '400',
                    'message': "wrong blogReviewStatus"
                })

        blog = -1

        userAuthed = request.user.is_authenticated

        if userAuthed: 
            # update blog review status
            blog = BlogModels.Blog.objects.filter(blogId=blogId)
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

                return JsonResponse({
                        'success': True,
                        'status': '200',
                        'message': 'reviewed'
                    })

            else:
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
        data = {
            'status': '400', 'reason': 'Bad Requests!'
        }
        return data

# delete blog
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
        blog = -1

        userAuthed = request.user.is_authenticated

        if checkUserWrittenBlog(userAuthed, request.user, blogId):
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
                'message': "wrong blog id or not the writter"
            })

    def post(self, request, *args, **kwargs):
        

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