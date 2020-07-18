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


from rest_framework import authentication, permissions, status, response
from rest_framework.response import Response, Serializer
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate

from mail_owl.utils import AutoMailSender

from UserAuthAPI import models, forms, serializers

class UserListView(ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.LoginSerializer


class EditUserDetails(GenericAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request):
        self.object = self.get_object()
        serializer = serializers.UserDetailSerializer(self.object, data=request.data)
        if serializer.is_valid():
            self.object.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def user_easy_registry_api(request):
    account_form = forms.BasicSiginInForm(data=request.POST)
    profile_form = forms.EasyRegistrationForm(data=request.POST)
    academic_form = forms.UserAcademicForm(data=request.POST)
    if account_form.is_valid() and profile_form.is_valid() and academic_form.is_valid():
        account_register = account_form.save(commit=False)
        profile = profile_form.save(commit=False)
        profile.user = account_register
        academic = academic_form.save(commit=False)
        academic.userProfile = profile
        if profile.membershipId and profile.membershipId != '':
            profile.isValid = True
        account_form.save()
        profile.save()
        academic.save()

        # 完成信息保存以后，发送注册成功的邮件
        username = profile.get_full_EN_name()
        target_email = account_register.email
        mail_content = {'username':username}
        confirm_mail = AutoMailSender(
            title="注册成功！Registraion Successful",
            mail_text="",
            template_path="myCSSAhub/email/register_mail.html",
            fill_in_context=mail_content,
            to_address=target_email,
        )
        confirm_mail.send_now()

    else:
        return Response({
            'success': False,
            'errors': [dict(account_form.errors.items()), dict(profile_form.errors.items()), dict(academic_form.errors.items())]
        })

    return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_login_user_info(request):
    loginUser = request.user
    userProfile = models.UserProfile.objects.filter(user=loginUser)[0]

    return Response({
        'firstname': userProfile.firstNameEN,
        'lastname': userProfile.lastNameEN,
        'email_addr': loginUser.email,
        'avatarUrl': userProfile.avatar.url
    })