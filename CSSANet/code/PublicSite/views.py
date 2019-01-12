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
    # 需要判断blogId
    # avatar没有的时候会报错！
    ViewBag = {}
    blogs = BlogModels.Blog.objects.filter(blogId=blogId)
    if not blogs:
        return page_not_found(request)
    blogSingle = blogs[0]
    blogOpen = blogSingle.blogOpen
    print(blogSingle.blogOpen)
    if not blogSingle.blogReviewed or not blogOpen:
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

def editBlog(request):
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
    blogContentSingle = -1
    blogTitle = ""
    blogMainContent = ""
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
                return permission_denied(request)
        blog = BlogModels.Blog.objects.filter(blogId=blogId)
        if not blog:
            return bad_request(request)
        blogContentSingle = blog[0]
        blogTitle = blogContentSingle.blogTitle
        blogMainContent = blogContentSingle.blogMainContent
        ViewBag["toolTitle"] = CH_BLOG
    else:
        ViewBag["toolTitle"] = CR_BLOG
        pass

    ViewBag["blogId"] = blogId
    ViewBag["blogTitle"] = blogTitle
    ViewBag["blogMainContent"] = blogMainContent


    
    return render(request, 'PublicSite/blogeditpage.html', ViewBag)


#@cache_page(CACHE_TTL)
#def Events(requests):
#    return

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
