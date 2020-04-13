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

############################  WARNING !!! #####################################
#                                                                             #
#    This part of code relates to the proprietary security features of        #
#                        myCSSA Account System                                #
#                                                                             #
#                                                                             #
#                          DO NOT DISCLOSE!                                   #
###############################################################################

from rest_framework import serializers
from LegacyDataAPI import models

class LegacyUserSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('firstNameEN', 'lastNameEN', 'gender', 'dateOfBirth', 'studentId', 'membershipId', 'telNumber', 'email') 
        model = models.LegacyUsers
        read_only_fields = ('firstNameEN', 'lastNameEN', 'gender', 'dateOfBirth', 'studentId', 'membershipId', 'telNumber', 'email')

class LegitCheck(serializers.Serializer):
    #A类记录字段
    membershipId = serializers.CharField(required=False, write_only=True)
    studentId = serializers.CharField(required=False, write_only=True)
    firstNameEN = serializers.CharField(required=False, write_only=True)
    lastNameEN =  serializers.CharField(required=False, write_only=True)
    dateOfBirth =  serializers.DateField(required=False, write_only=True)

    #B类记录
    telNumber = serializers.CharField(required=False, write_only=True)
    email = serializers.CharField(required=False, write_only=True)

    #结果
    outcome = serializers.CharField(required=False, write_only=True)


    class Meta:
        fields = '__all__'