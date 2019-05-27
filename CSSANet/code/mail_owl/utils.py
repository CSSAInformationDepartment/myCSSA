from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from PostmanAPI.models import *



class MailDirectSender(EmailMultiAlternatives):

    def __init__(self, mail_config:MailDraft) -> None:
       subject: str = mail_config.title
       body: str = mail_config.html_body
       from_email=None
       to=None
       bcc=None 
       connection=None 
       attachments=None 
       headers=None
       alternatives=None 
       cc=None
       reply_to=None
       return super().__init__(subject=subject, body=body, from_email=from_email, to=to, bcc=bcc, connection=connection, attachments=attachments, headers=headers, alternatives=alternatives, cc=cc, reply_to=reply_to)


