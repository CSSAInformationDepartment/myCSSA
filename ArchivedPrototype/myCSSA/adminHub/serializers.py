###############################################################################
#                    Desinged & Managed by JOSH.LE.LU                         #
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
#                             Version: 0.5a(C)                                #
#                                                                             #
#                               License: MIT                                  #
#                                                                             #
###############################################################################

from rest_framework import serializers
from adminHub import models as AdminModels

class MessageListSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('messageId', 'repliedId', 'messageTitle', 'timeOfSend',
        'isRead','isDraft','sender','receiver')
        read_only_fields = ('messageId', 'repliedId')


class  MessageBodySerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
