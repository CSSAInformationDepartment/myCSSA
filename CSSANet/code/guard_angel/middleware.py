from .models import HttpAccessLogModel
from UserAuthAPI.models import User, UserProfile
import json

class HttpRequestLogMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
        
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        new_log = HttpAccessLogModel()
        new_log.request_path = request.path_info or request.path
        new_log.request_query_string = request.META.get('QUERY_STRING')
        new_log.request_method = request.method

        #new_log.request_META = json.dumps(request.META)

        
        ## Save IP
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            new_log.visitor_ipv4 = request.META.get('HTTP_X_FORWARDED_FOR')
        else:
            new_log.visitor_ipv4 = request.META.get('REMOTE_ADDR')
       
        ## Store User Info
        if request.user.is_authenticated:
            new_log.is_anonymous = False
            new_log.user = User.objects.get(pk=request.user.id)
        else:
            new_log.is_anonymous = True
        
        response = self.get_response(request)
        
        new_log.status_code = response.status_code

        new_log.save()
        # Code to be executed for each request/response after
        # the view is called.

        return response