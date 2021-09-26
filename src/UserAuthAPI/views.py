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
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.core.mail import send_mail, BadHeaderError

from rest_framework import authentication, permissions, status, response
from rest_framework.parsers import JSONParser
from rest_framework.response import Response, Serializer
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

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
@permission_classes([])
def user_easy_registry_api(request):
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

# Password reset
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']

			# If the user exists in the database with matched email
			associated_users = models.User.objects.filter(Q(email=data))
			if associated_users.exists():

				# Send password reset email to the given address
				# === Currently only work locally ===
				for user in associated_users:
					subject = "CSSA Password Reset Requested"
					email_template_name = "password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'CSSA',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
						
					# If success, pop up a success message
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					# return redirect ("/hub/login/")
			# Otherwise let user to retype the email
			else:
				messages.error(request, 'An invalid email has been entered.')
	else:
		password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password_reset.html", context={"password_reset_form":password_reset_form})