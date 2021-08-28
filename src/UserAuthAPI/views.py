###############################################################################
#                    Desinged & Managed by Josh.Le.LU                         #
#                                                                             #
#                     █████╗ ██╗     ██╗ ██████╗███████╗                      #
#                    ██╔══██╗██║     ██║██╔════╝██╔════╝                      #
#                    ███████║██║     ██║██║     █████╗                        #
#                    ██╔══██║██║     ██║██║     ██╔══╝                        #
#                    ██║  ██║███████╗██║╚██████╗███████╗                      #
#                    ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝                      #
#        An agile web application platform bulit on top of Python/django      #
#                                                                             #
#                Proprietary version made for myCSSA project                  #
#                             Version: 0.6a(C)                                #
#                                                                             #
###############################################################################
from django.contrib.auth import get_user_model, authenticate

from rest_framework import authentication, permissions, status, response
from rest_framework.parsers import JSONParser
from rest_framework.response import Response, Serializer
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.generic import FormView
from mail_owl.utils import AutoMailSender

from UserAuthAPI import models, forms, serializers
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template import loader
from django.core.mail import send_mail
from django.contrib import messages
from django import forms

class UserListView(ListCreateAPIView):

    queryset = models.User.objects.all()
    serializer_class = serializers.LoginSerializer


class EditUserDetails(GenericAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        ## 获取object
        return self.request.user

    def post(self, request):
        ## 修改用户信息
        self.object = self.get_object()
        serializer = serializers.UserDetailSerializer(self.object, data=request.data)
        if serializer.is_valid():
            self.object.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([])
def user_easy_registry_api(request):
    ## 注册
    data = JSONParser().parse(request)
    serializer = serializers.UserEasyRegistrationSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        res = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(res, status=status.HTTP_201_CREATED)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_login_user_info(request):
    ## 获取已登录用户信息
    loginUser = request.user
    userProfile = models.UserProfile.objects.filter(user=loginUser)[0]

    return Response({
        'firstname': userProfile.firstNameEN,
        'lastname': userProfile.lastNameEN,
        'telNumber': loginUser.telNumber,
        'email_addr': loginUser.email,
        'studentId': userProfile.studentId,
        'membershipId': userProfile.membershipId,
        'avatarUrl': userProfile.avatar.url if userProfile.avatar else 'None'
    })


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Email"), max_length=254)
    
class ResetPasswordRequestView(FormView):
    ## FormView https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-editing/
    form_class = PasswordResetRequestForm
    success_url = '/login'
    template_name = "template/test_template.html"
 
    def form_valid(self, request,  *args, **kwargs):
        form = super(ResetPasswordRequestView, self).form_valid(*args, **kwargs)
        data= form.cleaned_data["email"]
        user= User.objects.filter(email=data)
        if user:
            c = {
                'email': user.email,
                'domain': self.request.META['HTTP_HOST'],
                'site_name': 'your site',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': self.request.scheme,
            }
            email_template_name='tamplate/reset_password.html'
            subject = "Reset Your Password"
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, 'yuntaol@student.unimelb.edu.au' , [user.email], fail_silently=False)
           
           
            messages.success(self.request, 'An email has been sent to ' + data +" if it is a valid user.")
        return 
        
                
         
           