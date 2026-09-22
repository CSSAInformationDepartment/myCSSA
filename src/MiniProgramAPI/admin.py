from django.contrib import admin

from .models import (
    Course,
    CourseReview,
    CourseReviewLike,
    IdempotencyRecord,
    InteractionMessage,
    MiniProgramProfile,
    PostExtension,
    PostLike,
    UploadAsset,
)


admin.site.register(MiniProgramProfile)
admin.site.register(PostExtension)
admin.site.register(PostLike)
admin.site.register(Course)
admin.site.register(CourseReview)
admin.site.register(CourseReviewLike)
admin.site.register(InteractionMessage)
admin.site.register(UploadAsset)
admin.site.register(IdempotencyRecord)
