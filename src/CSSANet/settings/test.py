from .ci import *

import os


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('TEST_DATABASE_NAME', 'mycssa_test'),
        'USER': os.environ.get('TEST_DATABASE_USER', 'postgres'),
        'PASSWORD': os.environ.get('TEST_DATABASE_PASSWORD', 'test-only-password'),
        'HOST': os.environ.get('TEST_DATABASE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('TEST_DATABASE_PORT', '5432'),
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

MINIPROGRAM_CONTENT_AUDIT_REQUIRED = False
MINIPROGRAM_IMAGE_AUDIT_REQUIRED = False

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
