from celery import app
from celery.schedules import schedule
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.core.exceptions import ImproperlyConfigured
from .models import MailQuene


@app.task(name='send_async_mail')
def send_async_mail(quene_task:MailQuene) -> None:

    try:
        from django.conf import settings
        FROM_EMAIL = settings.EMAIL_HOST_USER
    except:
        raise ImproperlyConfigured("EMAIL_HOST_USER is a necessary setting for using MailOwl")

    mail_comp = EmailMultiAlternatives(subject=quene_task.title, body=quene_task.mail_text, from_email=FROM_EMAIL, to=quene_task.receiver)
    
    if quene_task.mail_html:
        mail_comp.attach_alternative(quene_task.mail_html, mimetype="text/html")
    mail_comp.send()





