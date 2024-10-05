from django.shortcuts import render
import itertools
import math
from typing import Dict, List

from BlogAPI import models as BlogModels
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

# CacheSettings
from django.db.models import Q
from django.http import (
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View
from EventAPI import models as eventModels
from mail_owl.utils import AutoMailSender
from myCSSAhub import models as HubModels
from RecruitAPI import models as JobModels
from RecruitAPI.forms import ResumeSubmissionForm
from RecruitAPI.resume_mgr import checkDuplicateResume
from UserAuthAPI import models as UserModels

from PublicSite import models

# Create your views here.


################################# View Controller ########################################
# @cache_page(CACHE_TTL)
def index(request):
    '''
    The Homepage view function for public site
    '''
    now_time = timezone.now()
    # Filter events for the past year
    past_year = now_time - timezone.timedelta(days=365)
    eventsPast = eventModels.Event.objects.filter(
        eventActualStTime__lt=now_time, eventActualStTime__gt=past_year).order_by("-eventActualStTime")
    eventsFuture = eventModels.Event.objects.filter(
        eventActualStTime__gt=now_time).order_by("eventActualStTime")
    header_caro = models.HomepageCarousels.objects.all()
    return render(request, 'PublicSite/index.html',
                  {'now_time': now_time, 'eventsPast': eventsPast, 'eventsFuture': eventsFuture,
                   'head_carousels': header_caro,
                   })


def ContactUs(request):
    '''
    The Contact Detail view function for public site
    '''
    return render(request, 'PublicSite/contact_us.html')


class DepartmentInfoView(View):
    '''
    The All-in-one view for presenting the department info for cssa departments
    '''
    templates_dict: Dict[str, str] = {
        'council': 'PublicSite/dept_council.html',
        'organisation': 'PublicSite/dept_organisation.html',
        'recruitment': 'PublicSite/dept_recruitment.html',
        'information': 'PublicSite/dept_Information.html',
        'liaison': 'PublicSite/dept_liaison.html',
        'publicity': 'PublicSite/dept_publicity.html',
    }
    members_model = UserModels.CSSACommitteProfile
    dept_model = UserModels.CSSADept

    def get(self, request, *args, **kwargs):
        view_bag: Dict = {}
        dept: str = self.kwargs.get('dept')
        dept_profiles = self.members_model.objects.filter(
            Q(Department__deptName=dept) & Q(is_active=True))
        view_bag['director'] = dept_profiles.filter(
            role__roleFlag='director').first()
        view_bag['management'] = dept_profiles.filter(Q(role__roleFlag='vice-director') | Q(
            role__roleFlag='lead_eng') | Q(role__roleFlag='secretary')).order_by('-role__roleFlag')
        view_bag['general'] = dept_profiles.filter(role__roleFlag='general')

        if dept == 'council':
            view_bag['accountant'] = dept_profiles.filter(
                role__roleFlag='accountant').first()
            view_bag['president'] = dept_profiles.filter(
                role__roleFlag='president').first()
            view_bag['vice_president'] = dept_profiles.filter(
                role__roleFlag='vice-president')
            view_bag['headOfSecretary'] = dept_profiles.filter(
                role__roleFlag='headOfSecretary').first()

        if dept == 'information':
            view_bag['lead_eng'] = dept_profiles.filter(
                role__roleFlag='lead_eng')

        # Metrics
        view_bag['number_of_member'] = dept_profiles.count()
        num_of_male = dept_profiles.filter(member__gender='Male').count()
        num_of_female = dept_profiles.filter(member__gender='Female').count()
        num_of_other = dept_profiles.filter(member__gender='Other').count() / 2
        factor: float = 0
        if num_of_male > num_of_female and num_of_female != 0:
            factor = (num_of_male + num_of_other) / \
                (num_of_female + num_of_other)
        elif num_of_male != 0:
            factor = (num_of_female + num_of_other) / \
                (num_of_male + num_of_other)
        view_bag['gender_div'] = round(factor, 2) or 0

        return render(request, template_name=self.templates_dict[dept], context={'view_bag': view_bag})


def Recruitments(request):
    job_list = JobModels.JobList.objects.filter(disabled=False)
    return render(request, 'PublicSite/recruit.html', {'job_list': job_list})


class ResumeSubmissionView(LoginRequiredMixin, View):
    login_url = "/hub/login/"
    redirect_field_name = 'redirect_to'

    json_data: Dict = {}

    def get(self, request, *args, **kwargs):
        prev_submission = None
        jobId = self.kwargs.get('jobId')
        job_data = JobModels.JobList.objects.get(jobId=jobId)
        if checkDuplicateResume(jobId, request.user.id):
            prev_submission = JobModels.Resume.objects.filter(Q(disabled=False) & Q(
                user__id=request.user.id) & Q(jobRelated__jobId=jobId)).first()
        return render(request, 'PublicSite/jobapplication.html', {'job_data': job_data, 'prev_submission': prev_submission})

    def post(self, request, *args, **kwargs):
        jobId = self.kwargs.get('jobId')
        if request.user.is_authenticated:
            if checkDuplicateResume(jobId, request.user.id):
                self.json_data['result'] = False
                self.json_data['error'] = "Duplicated Submission! 您已经提交过该岗位的申请"
            else:
                form = ResumeSubmissionForm(
                    data=request.POST, files=request.FILES)
                form.user = request.user
                if form.is_valid():
                    instance = form.save()
                    self.json_data['result'] = True
                    mail_content = {'username': instance.user.userprofile.lastNameEN + " " + instance.user.userprofile.firstNameEN,
                                    'dept': instance.jobRelated.dept.deptTitle,
                                    'jobName': instance.jobRelated.jobName}

                    confirm_mail = AutoMailSender(
                        title="CV Submitted. 我们已经收到您的简历",
                        mail_text="",
                        template_path='myCSSAhub/email/cv_mail.html',
                        fill_in_context=mail_content,
                        to_address=request.user.email,
                    )
                    confirm_mail.send_now()
                else:
                    self.json_data['result'] = False
                    self.json_data['error'] = "抱歉，您的表单填写有误，请重新检查。请注意，每项字数不可超过500字。"
        else:
            self.json_data['result'] = False
            self.json_data['error'] = 'You need to login first! 请先登录！ '
        return JsonResponse(self.json_data)


class EventsListView(View):
    template_name = 'PublicSite/event.html'
    events = eventModels.Event.objects.all().order_by("-eventActualStTime")

    def get(self, request, *args, **kwargs):
        timezone.activate('Australia/Melbourne')
        now_time = timezone.now()
        # Filter events for the past year
        past_year = now_time - timezone.timedelta(days=365)
        eventsFuture = eventModels.Event.objects.filter(
            eventActualStTime__gt=now_time).order_by("eventActualStTime")
        eventsPast = eventModels.Event.objects.filter(
            eventActualStTime__lt=now_time, eventActualStTime__gt=past_year).order_by("-eventActualStTime")
        return render(request, self.template_name, {'eventsFuture': eventsFuture, 'now_time': now_time, 'events': self.events, 'eventsPast': eventsPast})


def EventDetails(request, eventID):
    event = get_object_or_404(eventModels.Event, pk=eventID)
    timezone.activate('Australia/Melbourne')
    now_time = timezone.now()
    print(now_time)
    return render(request, 'PublicSite/eventDetails.html', {'events': event, 'now_time': now_time})


def Blogs(request):
    # 找openToPublic为true的
    BLOG_P = 5.0
    PAGE_SHW = 3  # must be odd!

    try:
        page = int(request.GET["page"])
    except:
        return page_not_found(request)

    ViewBag = {}

    ViewBag["tagTitle"] = ""

    blogs = BlogModels.Blog.objects.filter(
        blogOpen=True, blogReviewed=2).order_by("createDate")[::-1]
    if "tag" in request.GET:
        # filter tag
        tags = BlogModels.BlogTag.objects.filter(tagName=request.GET["tag"])
        ViewBag["tagTitle"] = "标签为 " + request.GET["tag"] + " 的"
        if tags:
            BlogInTags = BlogModels.BlogInTag.objects.filter(tagId=tags[0])
            blogs = [
                tag.blogId for tag in BlogInTags if tag.blogId.blogOpen is True and tag.blogId.blogReviewed == 2]
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
        pagesBottom = [x for x in range(
            (numPage - PAGE_SHW + 1), (numPage + 1))]
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

        if wrote is True:
            ViewBag["userIsAuthor"] = True

    ViewBag["blog"] = blogSingle
    users = BlogModels.BlogWrittenBy.objects.filter(blogId=blogSingle)
    ViewBag["users"] = []
    for user in users:
        userProfile = None
        try:
            userProfile = UserModels.UserProfile.objects.filter(user=user.userId)[
                0]
        except:
            pass
        ViewBag["users"].append({
            "user": user.userId,
            "userProfile": userProfile
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

        blogWrittenBys = BlogModels.BlogWrittenBy.objects.filter(
            blogId=blogSingle)
        ViewBag["userIsAuthor"] = False
        ViewBag["onlyForReview"] = "[审核中] "
        wrote = False
        if blogWrittenBys:
            for blogWrittenBy in blogWrittenBys:
                if userAuthed and blogWrittenBy.userId == request.user:
                    wrote = True

            if wrote is True:
                ViewBag["userIsAuthor"] = True

        ViewBag["blog"] = blogSingle
        users = BlogModels.BlogWrittenBy.objects.filter(blogId=blogSingle)
        ViewBag["users"] = []
        for user in users:
            userProfile = None
            try:
                userProfile = UserModels.UserProfile.objects.filter(user=user.userId)[
                    0]
            except:
                pass
            ViewBag["users"].append({
                "user": user.userId,
                "userProfile": userProfile
            })

        curBlogTags = BlogModels.BlogInTag.objects.filter(blogId=blogSingle)
        blogTag = [x.tagId.tagName for x in curBlogTags]

        ViewBag["blogTag"] = blogTag
        print(ViewBag)
        return render(request, 'PublicSite/blogs.html', ViewBag)


################################# sponsor pages ########################################
def Merchants(request):

    infos = HubModels.DiscountMerchant.objects.all().order_by("merchant_add_date")

    return render(request, 'PublicSite/merchant.html', {'infos': infos})


def SupportMerchants(request):

    merchants = HubModels.DiscountMerchant.objects.all() \
        .filter(merchant_type='赞助商家') \
        .order_by("merchant_level")

    infos: Dict[str, List[HubModels.DiscountMerchant]] = \
        {k: list(v) for k, v in itertools.groupby(
            merchants, lambda x: x.merchant_level)}

    return render(request, 'PublicSite/supportMerchant.html', {'categories': {
        # 不是所有的 category 都存在。如果某个类别不存在，infos里不会有这个key
        # 从python 3.6开始，dict里key的声明顺序决定了 for 里遍历的顺序
        '钻石商家': infos.get('钻石商家'),
        '金牌商家': infos.get('金牌商家'),
        '银牌商家': infos.get('银牌商家'),
    }})


################################# errors pages ########################################


def bad_request(request, exception):
    return render(request, 'errors/page_400.html', status=400)


def permission_denied(request, exception):
    return render(request, 'errors/page_403.html', status=403)


def page_not_found(request, exception):
    return render(request, 'errors/page_404.html', status=404)


def server_error(request):
    return render(request, 'errors/page_500.html', status=500)
################################# errors pages ########################################
