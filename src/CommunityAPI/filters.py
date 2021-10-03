from django.http.request import HttpRequest
from rest_framework.filters import BaseFilterBackend
from rest_framework.compat import coreapi, coreschema
from rest_framework.serializers import ValidationError

class IsOwnerFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request: HttpRequest, queryset, view):
        if not request.query_params.get('my'):
            return queryset

        if request.user.is_anonymous:
            raise ValidationError('必须登录才能查看我的帖子')

        return queryset.filter(createdBy_id=request.user.id)

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='my',
                required=False,
                location='query',
                schema=coreschema.Boolean(
                    title='只看我的',
                    description='如果设置为 true，只返回我的帖子。默认为 false',
                )
            )
        ]

class TagFilter(BaseFilterBackend):
    """
    Filter the posts belonged to assigned tags.
    """
    def filter_queryset(self, request: HttpRequest, queryset, view):
        if not request.query_params.get('tagid'):
            return queryset

        return queryset.filter(tag=request.query_params.get('tagid'))

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='tagid',
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Post标签id',
                    description='选择标签后，只返回对应标签的posts',
                )
            )
        ]

class NoImgFilter(BaseFilterBackend):
    def filter_queryset(self, request: HttpRequest, queryset, view):
        # we do noting here. because it will be read by ReadContentSerializer
        return queryset

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='noimg',
                required=False,
                location='query',
                schema=coreschema.Boolean(
                    title='不返回图片',
                    description='在返回的列表里不返回图片，这样设置可以提高查询速度。（默认为false）',
                )
            )
        ]
