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

import json, math
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
    BLOG_P = 2.0
    PAGE_SHW = 3 # must be odd!

    blogs = BlogModels.Blog.objects.filter(blogOpen=True, blogReviewed=True)
    if "tag" in request.GET:
        blogsTemp = []
        # filter tag
    numPage = int(math.ceil(len(blogs) / BLOG_P))
    # no blogs
    if page < 1 or page > numPage:
        return page_not_found(request)
    
    blogStarts = int((page - 1) * BLOG_P)
    blogEndAt = int((page) * BLOG_P)

    ViewBag = {}
    ViewBag["blogs"] = blogs[blogStarts: blogEndAt]

    pagesBottom = []
    if PAGE_SHW >= numPage:
        pagesBottom = [(x + 1) for x in range(numPage)]
    if page < PAGE_SHW:
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
    print(blogSingle.blogOpen)

    userAuthed = request.user.is_authenticated
    
    if not blogSingle.blogReviewed or not blogOpen:
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
    print(ViewBag)
    return render(request, 'PublicSite/blogs.html', ViewBag)
    


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
