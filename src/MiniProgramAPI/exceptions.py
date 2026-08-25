from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    business_code = 10001
    default_detail = 'Request failed'

    def __init__(self, message=None, data=None):
        super().__init__({
            'businessCode': self.business_code,
            'message': message or self.default_detail,
            'data': data,
        })


class DuplicateOperation(BusinessAPIException):
    status_code = status.HTTP_409_CONFLICT
    business_code = 10005
    default_detail = 'Duplicate operation'


class AuditRejected(BusinessAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    business_code = 10006
    default_detail = 'Content audit rejected'


class OperationTooFrequent(BusinessAPIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    business_code = 10007
    default_detail = 'Operation too frequent'

    def __init__(self, retry_after):
        super().__init__(
            message='发布过于频繁，请稍后再试',
            data={'retryAfter': max(1, int(retry_after))},
        )


class DependencyUnavailable(BusinessAPIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    business_code = 20001
    default_detail = 'Dependency service unavailable'
