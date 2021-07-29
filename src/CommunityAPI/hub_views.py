from django import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from rest_framework.generics import get_object_or_404

from CommunityAPI.models import Post
from .serializers import resolve_post_content

def pk(instance):
    if not instance:
        return ''
    else:
        return instance.pk

class ShowPostView(LoginRequiredMixin, TemplateView):
    login_url = '/hub/login/'
    template_name = 'CommunityAPI/show_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        id = self.request.GET.get('id', 0)
        post: Post = Post.objects.filter(id=id).first()
        if post:
            return {
                **context,
                'post': post,
                'content': resolve_post_content(post),
                'post_fields': [
                    ('创建时间', post.createTime),
                    ('创建者', post.createdBy.pk),
                    ('Tag', post.tag.title if post.tag else ''),
                    ('未登录用户是否可见', post.viewableToGuest),
                    ('被删除', post.deleted),
                    ('被谁删除', pk(post.deletedBy)),
                    ('被屏蔽', post.censored),
                    ('被谁屏蔽', pk(post.censoredBy)),
                ]
            }
        else:
            return {
                **context,
                'id': id,
            }