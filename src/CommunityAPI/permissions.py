from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and obj.createdBy_id == request.user.id


class CanHandleReport(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('CommunityAPI.can_handle_report')


class CanCensorPost(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('CommunityAPI.censor_post')
