import uuid

from django.db import IntegrityError, transaction
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from UserAuthAPI.models import UserProfile

from .models import IdempotencyRecord
from .renderers import V1JSONRenderer


class PublicV1APIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (V1JSONRenderer,)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        supplied = request.META.get('HTTP_X_REQUEST_ID', '')
        try:
            request_id = str(uuid.UUID(supplied))
        except (TypeError, ValueError, AttributeError):
            request_id = str(uuid.uuid4())
        response['X-Request-Id'] = request_id
        return response

    def get_profile(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return None
        return UserProfile.objects.select_related('user').get(pk=self.request.user.pk)


class AuthenticatedV1APIView(PublicV1APIView):
    permission_classes = (permissions.IsAuthenticated,)


class IdempotentCreateMixin:
    idempotency_header = 'HTTP_IDEMPOTENCY_KEY'

    def replay_idempotent_response(self, profile):
        key = self.request.META.get(self.idempotency_header)
        if not key:
            return None
        if len(key) > 128:
            raise serializers.ValidationError({
                'Idempotency-Key': '长度不能超过 128 个字符',
            })
        # All current callers run inside transaction.atomic(). Serialising on
        # the profile closes the check-then-create race for concurrent retries.
        profile.__class__.objects.select_for_update().get(pk=profile.pk)
        record = IdempotencyRecord.objects.filter(
            user=profile,
            key=key,
            method=self.request.method,
            path=self.request.path,
        ).first()
        if not record:
            return None
        return Response(record.response_data, status=record.response_status)

    def store_idempotent_response(self, profile, data, status_code=200):
        key = self.request.META.get(self.idempotency_header)
        if not key:
            return
        try:
            with transaction.atomic():
                IdempotencyRecord.objects.create(
                    user=profile,
                    key=key,
                    method=self.request.method,
                    path=self.request.path,
                    response_status=status_code,
                    response_data=data,
                )
        except IntegrityError:
            # Another identical request committed first. Its response can be
            # returned by a subsequent retry.
            return
