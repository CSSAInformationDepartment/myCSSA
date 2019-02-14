from django.shortcuts import render,reverse
from django.http import JsonResponse
from PublicSite import models
from UserAuthAPI import models as UserModels
from BlogAPI import models as BlogModels
from RecruitAPI import models as JobModels
# Static Files Path Reference
from CSSANet.settings import MEDIA_ROOT, MEDIA_URL
from Library.SiteManagement import LoadPagetoRegister
# CacheSettings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from django.views.decorators.cache import cache_page

import json, math

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
from RecruitAPI.forms import ResumeSubmissionForm
from LegacyDataAPI import models as LegacyDataModels

from myCSSAhub import models as HubModels

# Create your views here.


################################# View Controller ########################################
#@cache_page(CACHE_TTL)
def index(request):

    return render(request, 'PublicSite/index.html')

#@cache_page(CACHE_TTL)
def News(request):
    return render(request, 'PublicSite/News.html')

def ContactUs(request):
    return render(request, 'PublicSite/contact_us.html')

#@cache_page(CACHE_TTL)
def Departments(request,dept):
    ViewBag = {}
    ViewBag['MEDIA_ROOT'] = MEDIA_ROOT
    ViewBag['MEDIA_URL'] = MEDIA_URL
    DeptInfo = UserModels.CSSADept.objects.filter(deptName=dept)
    if not DeptInfo:
        ViewBag['dept'] = None
    else:
        ViewBag['dept'] = DeptInfo[0]

    PageFields = models.HTMLFields.objects.filter(PageId__uri=request.get_full_path(Departments))

    for field in PageFields:
        if field.fieldType == 'text':
            ViewBag[field.fieldName.replace("-","")] = {'fieldInnerText':field.fieldInnerText}
        if field.fieldType == 'img':
            imgPath = models.ImgAttributes.objects.filter(RelatedField__id=field.id)[0].filePath
            ViewBag[field.fieldName.replace("-","")] = {
                'imgUri': imgPath.url
            }
    print(ViewBag)

    return render(request, 'PublicSite/dept.html', ViewBag)

def Recruitments(request):
    job_list = JobModels.JobList.objects.all()
    return render(request, 'PublicSite/recruit.html', {'job_list': job_list})

class ResumeSubmissionView(LoginRequiredMixin,View):
    login_url = "/hub/login/"
    redirect_field_name = 'redirect_to'

    json_data={}
    
    def get(self, request, *args, **kwargs):
        jobId = self.kwargs.get('jobId')
        job_data = JobModels.JobList.objects.get(jobId=jobId)
        return render(request, 'PublicSite/jobapplication.html', {'job_data': job_data})
    
    def post(self, request, *args, **kwargs):
        jobId = self.kwargs.get('jobId')
        job_data = JobModels.JobList.objects.get(jobId=jobId)
        if request.user.is_authenticated:
            form = ResumeSubmissionForm(data=request.POST, files=request.FILES)
            form.user = request.user
            if form.is_valid:
                form.save()
                self.json_data['result'] = True
         #       return JsonResponse(self.json_data)
            else:
                self.json_data['result'] = False
                self.json_data['error'] = form.error_class
        else:
            self.json_data['result'] = False
            self.json_data['error'] =  'You need to login first! '
        return JsonResponse(self.json_data)

class EventsListView(LoginRequiredMixin ,View):
    
    
    def get(self, request, *args, **kwargs):
        return render(request, 'PublicSite/event.html')

def Blogs(request):
    # 找openToPublic为true的
    BLOG_P = 5.0
    PAGE_SHW = 3 # must be odd!

    try:
        page = int(request.GET["page"])
    except:
        return page_not_found(request)

    ViewBag = {}

    ViewBag["tagTitle"] = ""

    blogs = BlogModels.Blog.objects.filter(blogOpen=True, blogReviewed=2).order_by("createDate")[::-1]
    if "tag" in request.GET:
        blogsTemp = []
        # filter tag
        tags = BlogModels.BlogTag.objects.filter(tagName=request.GET["tag"])
        ViewBag["tagTitle"] = "标签为 " + request.GET["tag"] + " 的"
        if tags:
            BlogInTags = BlogModels.BlogInTag.objects.filter(tagId=tags[0])
            blogs = [tag.blogId for tag in BlogInTags if tag.blogId.blogOpen==True and tag.blogId.blogReviewed==2]
        else:
            blogs = []


    numPage = int(math.ceil(len(blogs) / BLOG_P))
    # no blogs
    if numPage == 0:
        ViewBag["haveBlogs"] = False
    else:
        ViewBag["haveBlogs"] = True
    if numPage != 0 and (page < 1 or page > numPage):
        return page_not_found(request)

    blogStarts = int((page - 1) * BLOG_P)
    blogEndAt = int((page) * BLOG_P)
    ViewBag["blogs"] = [[y, [x.tagId.tagName for x in
        BlogModels.BlogInTag.objects.filter(blogId=y)]] for y in blogs[blogStarts: blogEndAt]]


    pagesBottom = []
    if PAGE_SHW >= numPage:
        pagesBottom = [(x + 1) for x in range(numPage)]
    elif page < PAGE_SHW:
        pagesBottom = [(x + 1) for x in range(PAGE_SHW)]
    elif page > numPage - PAGE_SHW + 1:
        pagesBottom = [x for x in range((numPage - PAGE_SHW + 1), (numPage + 1))]
    else:
        pageStart = page - (PAGE_SHW - 1) / 2
        pageEnd = page + (PAGE_SHW - 1) / 2 + 1
        pagesBottom = [x for x in range(pageStart, pageEnd)]

    ViewBag["pages"] = pagesBottom
    ViewBag["thisPage"] = page
    ViewBag["numPage"] = numPage


    nextPrev = {"pr": -1, "ne": -1}
    if page != 1:
        nextPrev["pr"] = page - 1
    if page != numPage:
        nextPrev["ne"] = page + 1
    ViewBag["hasNextPrev"] = nextPrev
    print("GET HERE !!")
    return render(request, "PublicSite/blogbref.html", ViewBag)

    pass

def BlogContents(request, blogId):
    # 需要判断blogId
    # avatar没有的时候会报错！
    ViewBag = {}
    blogs = BlogModels.Blog.objects.filter(blogId=blogId)
    if not blogs:
        return page_not_found(request)
    blogSingle = blogs[0]
    blogOpen = blogSingle.blogOpen

    userAuthed = request.user.is_authenticated

    if blogSingle.blogReviewed != 2 or not blogOpen:
        return page_not_found(request)


    blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blogSingle)
    ViewBag["userIsAuthor"] = False
    wrote = False
    if blogWrittenBys:
        for blogWrittenBy in blogWrittenBys:
            if userAuthed and blogWrittenBy.userId == request.user:
                wrote = True

        if wrote == True:
            ViewBag["userIsAuthor"] = True

    ViewBag["blog"] = blogSingle
    users= BlogModels.BlogWrittenBy.objects.filter(blogId=blogSingle)
    ViewBag["users"] = []
    for user in users:
        ViewBag["users"].append({
            "user": user.userId,
            "userProfile": UserModels.UserProfile.objects.filter(user=user.userId)[0]
        })

    curBlogTags = BlogModels.BlogInTag.objects.filter(blogId=blogSingle)
    blogTag = [x.tagId.tagName for x in curBlogTags]

    ViewBag["blogTag"] = blogTag
    return render(request, 'PublicSite/blogs.html', ViewBag)


class reviewBlogPublic(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/hub/login/"
    permission_required = ("BlogAPI.add_blogreviewed", "BlogAPI.delete_blogreviewed",
    )

    def get(self, request, *args, **kwargs):
        ViewBag = {}

        try:
            blogId = int(request.GET["blogId"])
        except:
            return page_not_found(request)

        blogs = BlogModels.Blog.objects.filter(blogId=blogId)
        if not blogs:
            return page_not_found(request)
        blogSingle = blogs[0]
        blogOpen = blogSingle.blogOpen
        print(blogSingle.blogOpen)

        userAuthed = request.user.is_authenticated

        if not blogOpen:
            return page_not_found(request)


        blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(blogId=blogSingle)
        ViewBag["userIsAuthor"] = False
        ViewBag["onlyForReview"] = "[审核中] "
        wrote = False
        if blogWrittenBys:
            for blogWrittenBy in blogWrittenBys:
                if userAuthed and blogWrittenBy.userId == request.user:
                    wrote = True

            if wrote == True:
                ViewBag["userIsAuthor"] = True

        ViewBag["blog"] = blogSingle
        users= BlogModels.BlogWrittenBy.objects.filter(blogId=blogSingle)
        ViewBag["users"] = []
        for user in users:
            ViewBag["users"].append({
                "user": user.userId,
                "userProfile": UserModels.UserProfile.objects.filter(user=user.userId)[0]
            })

        curBlogTags = BlogModels.BlogInTag.objects.filter(blogId=blogSingle)
        blogTag = [x.tagId.tagName for x in curBlogTags]

        ViewBag["blogTag"] = blogTag
        print(ViewBag)
        return render(request, 'PublicSite/blogs.html', ViewBag)


#@cache_page(CACHE_TTL)
#def Events(requests):
#    return

################################# sponsor pages ########################################
def Merchants(request):

    infos = HubModels.DiscountMerchant.objects.all().order_by("merchant_add_date").values()

    return render(request,'PublicSite/merchant.html', locals())

################################# errors pages ########################################
from django.shortcuts import render

def bad_request(request):
 return render(request,'errors/page_400.html')

def permission_denied(request):
 return render(request,'errors/page_403.html')

def page_not_found(request):
 return render(request,'errors/page_404.html')

def server_error(request):
 return render(request,'errors/page_500.html')
################################# errors pages ########################################
