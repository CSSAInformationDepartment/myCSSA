
#              ,' ``',
#             '  (o)(o)
#            `       > ;
#            ',     . ...-'"""""`'.
#          .'`',`''''`________:   ":___________________________________
#        (`'. '.;  |           ;/\;\;                                  |
#       (`',.',.;  |                                                   |
#      (,'` .`.,'  |    Mail Owl -> RESTful email service interface    |
#      (,.',.','   |              ~ Universal Component of openALICE   |
#     (,.',.-`_____|                                                   |
#         __\_ _\_ |              Designer: Le Lu (2019)               |
#                  |               Ver: 0.0.2 (Ricecake)               |
#                  |                 M.I.T. Licensed                   |
#                  |___________________________________________________|
#


from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings.dev')

app = Celery('mail_owl')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {

    'check-schedule-every-ten-minutes': {
        'task': 'mail_schedule_checker',
        'schedule': crontab(minute='0,10,14,15,20,30,40,50'),
    },
}
