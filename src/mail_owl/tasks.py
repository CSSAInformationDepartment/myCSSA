import datetime

from .celery import app
from celery.schedules import schedule
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.core.exceptions import ImproperlyConfigured
from .models import MailQuene
from django.utils import timezone as sys_time
from django.db.models import Q

TEN_MINUTES_INTERVAL = 600.0

from django.db import transaction

def exec_sendmail(quene_task:MailQuene) -> None:
    try:
        from django.conf import settings
        FROM_EMAIL = settings.EMAIL_HOST_USER
    except:
        raise ImproperlyConfigured("EMAIL_HOST_USER is a necessary setting for using MailOwl")

    mail_comp = EmailMultiAlternatives(subject=quene_task.title, 
        body=quene_task.mail_text, 
        from_email=FROM_EMAIL, 
        to=[quene_task.receiver])

    if quene_task.mail_html:
        mail_comp.attach_alternative(quene_task.mail_html, mimetype="text/html")
    
    mail_comp.send()


@app.task(name='send_async_mail')
def send_async_mail(quene_id:int) -> None:
    quene_task = MailQuene.objects.get(pk=quene_id)

    quene_task._send_init()
    try:
        exec_sendmail(quene_task)
        quene_task._send_success()
    except:
        quene_task._send_failed()


@app.task(name='mail_schedule_checker')
def scheduled_mail_sender():
    interval_start = sys_time.now() - datetime.timedelta(seconds=5.0)
    interval_end = sys_time.now() + datetime.timedelta(seconds=TEN_MINUTES_INTERVAL)
    quene = MailQuene.objects.select_for_update(skip_locked=True).filter(
        Q(date_scheduled__gte=interval_start) &
        Q(date_scheduled__lte=interval_end) & 
        Q(state=0)
    )
    with transaction.atomic():
        for quene_task in quene:
            quene_task._send_init()
            try:
                exec_sendmail(quene_task)
                quene_task._send_success()
            except:
                quene_task._send_failed()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
