from django.contrib.auth.models import User
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and obj.createdBy_id == request.user.id