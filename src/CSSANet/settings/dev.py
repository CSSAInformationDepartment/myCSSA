from .base import *

DEBUG = True

ALLOWED_HOSTS = ['10.0.2.2','*']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'myCSSA',
#         'USER': 'postgres',
#         'PASSWORD': 'aiuh489ieu19vc*4',
#         'HOST': 'db',
#         'PORT': '5432'
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cssadev',
        'USER': 'dev_general',
        'PASSWORD': 'cwGlU8j1DS',
        'HOST': 'dev.cssaunimelb.com',
        'PORT': '43961'
    }
}

## S3 Elastic Storage Configuration

AWS_DEFAULT_ACL = None
AWS_ACCESS_KEY_ID = 's3dev'
AWS_SECRET_ACCESS_KEY = 'kdj3iqkU6UumYchEKx4OJpQzzcj0vrWx'
AWS_STORAGE_BUCKET_NAME = 's3dev'
AWS_S3_ENDPOINT = 'devcdn.cssaunimelb.com'
AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_ENDPOINT}'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_QUERYSTRING_AUTH = True

AWS_STATIC_LOCATION = 'static'
AWS_MEDIA_LOCATION = 'media'

AWS_S3_CUSTOM_DOMAIN = f'{AWS_S3_ENDPOINT}/{AWS_STORAGE_BUCKET_NAME}'

# S3 static settings
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
STATICFILES_STORAGE = 'Library.backends.storages.PublicStaticStorage'
# S3 public media settings
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'Library.backends.storages.PublicMediaStorage'

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Mail Owl Config
MAILOWL_MULTI_NODES = True
MAILOWL_MASTER_NODE = ''
MAILOWL_PORT = 44300


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

# STATICFILES_DIRS = [
#     os.path.join(PROJECT_DIR, 'static'),
# ]

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_URL = '/static/'

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'

### Email Configuration

# To test the mail sending related features, adding your personal email accounts credentials here. 
# Remember !!! You must REMOVE your credentails when you push this to the public repo, otherwise your 
# credentials will be at risk.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

try:
    from .local import *
except:
    pass