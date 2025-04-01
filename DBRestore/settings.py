DATABASES = {
    "source": {
        "host": "localhost",
        "port": 5432,
        "db": "myCSSA_prod",
        "user": "postgres",
        "password": "postgres",
    },
    "destination": {
        "host": "localhost",
        "port": 5432,
        "db": "CSSARestoreA",
        "user": "postgres",
        "password": "postgres",
    },
}

EXCLUDED_TABLE = [
    "authtoken_token",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_session",
    "django_site",
    "socialaccount_socialtoken",
    "guard_angel_httpaccesslogmodel",
]

ANONYMOUS_MASKING_CONFIG = {}
