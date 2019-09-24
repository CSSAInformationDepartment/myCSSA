from .base import *

DEBUG = True

ALLOWED_HOSTS = ['10.0.2.2','*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'myCSSA',
        'USER': 'postgres',
        'PASSWORD': 'aiuh489ieu19vc*4',
        'HOST': 'db',
        'PORT': '5432'
    }
}

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

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

### Email Configuration

# To test the mail sending related features, adding your personal email accounts credentials here. 
# Remember !!! You must REMOVE your credentails when you push this to the public repo, otherwise your 
# credentials will be at risk.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

try:
    from .local import *
except:
    pass