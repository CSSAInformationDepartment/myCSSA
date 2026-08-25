from rest_framework.renderers import JSONRenderer


HTTP_BUSINESS_CODE = {
    400: 10001,
    401: 10002,
    403: 10003,
    404: 10004,
    409: 10005,
    422: 10006,
    429: 10007,
    500: 20000,
    503: 20001,
}


def _message_from_error(data):
    if isinstance(data, dict):
        detail = data.get('detail')
        if detail:
            return str(detail)
        message = data.get('message')
        if message:
            return str(message)
    if isinstance(data, list) and data:
        return str(data[0])
    if data:
        return str(data)
    return 'Request failed'


def _business_data(data):
    """Restore typed business metadata flattened by DRF's ErrorDetail."""
    if not isinstance(data, dict):
        return data
    result = dict(data)
    retry_after = result.get('retryAfter')
    if retry_after is not None:
        try:
            result['retryAfter'] = int(retry_after)
        except (TypeError, ValueError):
            pass
    return result


class V1JSONRenderer(JSONRenderer):
    """Wrap only MiniProgramAPI responses without changing legacy APIs."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get('response')
        status_code = getattr(response, 'status_code', 200)

        if isinstance(data, dict) and set(('code', 'message', 'data')).issubset(data):
            payload = data
        elif status_code < 400:
            payload = {'code': 0, 'message': 'ok', 'data': data}
        elif isinstance(data, dict) and 'businessCode' in data:
            payload = {
                'code': int(data.get('businessCode')),
                'message': str(data.get('message') or 'Request failed'),
                'data': _business_data(data.get('data')),
            }
        else:
            payload = {
                'code': HTTP_BUSINESS_CODE.get(status_code, 20000),
                'message': _message_from_error(data),
                'data': {'errors': data} if data else None,
            }

        return super().render(payload, accepted_media_type, renderer_context)
