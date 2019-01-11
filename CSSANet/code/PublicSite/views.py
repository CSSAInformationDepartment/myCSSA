from django.shortcuts import render,reverse
from django.http import JsonResponse
from PublicSite import models
from UserAuthAPI import models as UserModels
from BlogAPI import models as BlogModels
# Static Files Path Reference
from CSSANet.settings import MEDIA_ROOT, MEDIA_URL
from Library.SiteManagement import LoadPagetoRegister
# CacheSettings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from django.views.decorators.cache import cache_page
# Create your views here.


################################# View Controller ########################################
#@cache_page(CACHE_TTL)
def index(request):

    return render(request, 'PublicSite/index.html')
            
#@cache_page(CACHE_TTL)
def News(request):
    return render(request, 'PublicSite/News.html')

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

def Blogs(request, page):
    # 找openToPublic为true的
    pass

def BlogContents(request, blogId):
    # 需要判断contentId
    # avatar没有的时候会报错！
    ViewBag = {}
    blogs = BlogModels.Blog.objects.filter()
    blogSingle = blogs[0]
    if not blogSingle.openToPublic:
        return page_not_found(request)
    ViewBag["blog"] = blogSingle
    users= BlogModels.BlogWrittenBy.objects.filter(blogId=blogSingle)
    ViewBag["users"] = []
    for user in users:
        ViewBag["users"].append({
            "user": user.userId,
            "userProfile": UserModels.UserProfile.objects.filter(user=user.userId)[0]
        })
    print(ViewBag)
    return render(request, 'PublicSite/blogs.html', ViewBag)

def editBlog(request, contentId):
    # 需要判断contentId
    # avatar没有的时候会报错
    ViewBag = {}
    blog = BlogModels.Blog.objects.filter()
    blogContentSingle = blogContent[0]
    return

#@cache_page(CACHE_TTL)
#def Events(requests):
#    return

################################# sponsor pages ########################################
def Sponsor(request):

    return render(request,'PublicSite/sponsor.html')

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
