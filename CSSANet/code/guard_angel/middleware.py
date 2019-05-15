from .models import HttpAccessLogModel
from UserAuthAPI.models import User, UserProfile
import json

def not_logging_whitelist(ip):
    WHITE_LIST = [
        '10.*.*.*',
        '192.168.*.*',
    ]
    if ip is None:
        return False

    return True


class HttpRequestLogMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
        
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        new_log = HttpAccessLogModel()
        new_log.request_path = request.path_info or request.path
        new_log.request_query_string = request.META.get('QUERY_STRING')
        new_log.request_method = request.method

        #new_log.request_META = json.dumps(request.META)
        
        ## Save IP
        USE_HTTP_X_FORWARD_FOR = True

        if USE_HTTP_X_FORWARD_FOR:
            new_log.visitor_ipv4 = request.META.get('HTTP_X_FORWARDED_FOR')
            if new_log.visitor_ipv4 is not None and ',' in new_log.visitor_ipv4:
                    proxy_parts = new_log.visitor_ipv4.split(',')
                    new_log.visitor_ipv4 = proxy_parts[-1].strip()
        else:
            new_log.visitor_ipv4 = request.META.get('REMOTE_ADDR')
       

        if not_logging_whitelist(new_log.visitor_ipv4):
            ## Store User Info
            if request.user.is_authenticated:
                new_log.is_anonymous = False
                new_log.user = User.objects.get(pk=request.user.id)
            else:
                new_log.is_anonymous = True
            
            new_log.status_code = response.status_code

            
            new_log.save()
            # Code to be executed for each request/response after
            # the view is called.

        return response