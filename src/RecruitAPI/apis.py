from .models import *
from UserAuthAPI.models import CSSACommitteProfile, CSSADept
from django.db.models import Q


def GetResumesByDepartments(request_user):
    if request_user.is_authenticated and request_user.is_staff:
        if request_user.is_superuser or request_user.has_perm('RecruitAPI.view_all_resumes'):
            return Resume.objects.filter(disabled=False).order_by('-timeOfCreate')
        else:
            committe_profile = CSSACommitteProfile.objects.filter(Q(is_active=True) & Q(member__user=request_user)).first()
            if committe_profile:
                return Resume.objects.filter(Q(disabled=False) & Q(jobRelated__dept=committe_profile.Department)).order_by('-timeOfCreate')
            else:
                return None
    else:
        return None

def GetInterviewTimeByDepartments(request_user):
    if request_user.is_authenticated and request_user.is_staff:
        if request_user.is_superuser or request_user.has_perm('RecruitAPI.view_all_resumes'):
            return InterviewTimetable.objects.filter(disabled=False).order_by('-date', '-time')
        else:
            committe_profile = CSSACommitteProfile.objects.filter(Q(is_active=True) & Q(member__user=request_user)).first()
            if committe_profile:
                return InterviewTimetable.objects.filter(Q(disabled=False) & 
                    Q(resume__jobRelated__dept=committe_profile.Department)).order_by('-date', '-time')
            else:
                return None
    else:
        return None