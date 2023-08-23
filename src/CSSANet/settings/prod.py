#################################################
### CSSANet Production ENV Configuration File ###
###                                           ###
###        Composed by Le (Josh). Lu          ###
#################################################

# WARINING!: You should NEVER includes any real value of keys/credentials/passwords in this file
# To store a new sercret value for the production ENV, please disscuss with the director or lead
# developer of CSSA Information Technology Department first.

from .base import *

import os
env_dist = os.environ

DEBUG = False

SECRET_KEY = env_dist.get('DJANGOKEYPD')
ALLOWED_HOSTS = ['cssanet', '.cssaunimelb.com',
                 'cloud.digitalocean.com', '.digitalocean.com', '165.227.240.43']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True  # <- Activate in HTTPS envrioment only
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = False
X_FRAME_OPTIONS = 'DENY'


# S3 Elastic Storage Configuration

AWS_DEFAULT_ACL = None
AWS_ACCESS_KEY_ID = env_dist.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env_dist.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env_dist.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT = env_dist.get('AWS_S3_ENDPOINT')
AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_ENDPOINT}'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_QUERYSTRING_AUTH = True

AWS_STATIC_LOCATION = 'static'
AWS_MEDIA_LOCATION = 'media'

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT}'

# S3 static settings
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
STATICFILES_STORAGE = 'Library.backends.storages.StaticStorage'
# S3 public media settings
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'Library.backends.storages.PublicMediaStorage'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'myCSSA',
        'USER': 'cssaweb',
        'PASSWORD': env_dist.get('DATABASE_PASSWD'),
        'HOST': env_dist.get('DATABASE_HOST'),
        'PORT': env_dist.get('DATABASE_PORT'),
    }
}

# Redis Message Cache Serivce
# REDIS_ADDRESS = 'redis://redis:6379/6'

CELERY_BROKER_URL = 'redis://redis-service:6379'
CELERY_RESULT_BACKEND = 'redis://redis-service:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Mail Owl Config
MAILOWL_MULTI_NODES = False
MAILOWL_MASTER_NODE = ''
MAILOWL_PORT = 44300


ADMINS = [('Master Inbox', 'information@cssaunimelb.com'),
          ('Lead Engineer', 'joshlubox@gmail.com')]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
SERVER_EMAIL = env_dist.get('SERVER_EMAIL')
EMAIL_HOST_USER = env_dist.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env_dist.get('EMAIL_HOST_PASSWORD')

MINIPROGRAM_APPID = env_dist.get('MINIPROGRAM_APPID')
MINIPROGRAM_SECRET = env_dist.get('MINIPROGRAM_SECRET')

try:
    from .local import *
except:
    pass
