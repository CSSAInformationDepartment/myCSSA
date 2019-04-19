from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']
SECRET_KEY = env_dist.get('DJANGOKEYDEV')

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

# CACHES = {
#  'default': {
#   'BACKEND': 'django.core.cache.backends.dummy.DummyCache',  # 缓存后台使用的引擎
#   'TIMEOUT': 0,            # 缓存超时时间（默认300秒，None表示永不过期，0表示立即过期）
#   'OPTIONS':{
#    'MAX_ENTRIES': 300,          # 最大缓存记录的数量（默认300）
#    'CULL_FREQUENCY': 3,          # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3）
#   },
#  }
# }

# # Cache time to live is 1 minutes.
# CACHE_TTL = 1 * 1
# # Cache ENV Setup
# #SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# #SESSION_CACHE_ALIAS = "default"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '/static'),
]

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'


try:
    from .local import *
except:
    pass