from django import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from rest_framework.generics import get_object_or_404

from CommunityAPI.models import Post
from .serializers import resolve_post_content


class ShowPostView(LoginRequiredMixin, TemplateView):
    login_url = '/hub/login/'
    template_name = 'CommunityAPI/show_post.html'
    permission_required = ('CommunityAPI.censor_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        post = Post.objects.filter(id=self.request.GET.get('id', 0)).first()

        if post:
            return {
                **context,
                "id": self.request.GET.get('id', 0),
                'post': post,
                'content': resolve_post_content(post),
            }
        else:
            print(context)
            return context