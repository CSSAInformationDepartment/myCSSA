def checkDuplicateResume(jobId, userId):
    from django.db.models import Q
    import RecruitAPI.models as JobModels

    prev_submission = JobModels.Resume.objects.filter(Q(disabled=False) & Q(user__id=userId) & Q(jobRelated__jobId=jobId)).first()
    if prev_submission:
        return True
    else:
        return False
