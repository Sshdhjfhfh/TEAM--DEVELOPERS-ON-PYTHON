"""
Configuración de Django para el proyecto topico_project.

Generado con 'django-admin startproject' usando Django 5.1.

Documentación:
- https://docs.djangoproject.com/en/5.1/topics/settings/
- https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-sf1oqo-!k)0_f9d0$0f)5#=*anb771@iolf1a0&t2mmo!n21^h',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host] or ['127.0.0.1', 'localhost']
if DEBUG:
    # 'testserver' lo utiliza el cliente de pruebas de Django
    ALLOWED_HOSTS += ['testserver']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Librerías de terceros
    'rest_framework',
    'rest_framework.authtoken',
    # Aplicaciones del proyecto
    'accounts',
    'pacientes',
    'atenciones',
    'inventario',
    'reportes',
    'api_rest',
    'portal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'topico_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.permisos_roles',
            ],
        },
    },
]

WSGI_APPLICATION = 'topico_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# En desarrollo se usa SQLite (archivo db.sqlite3). Para producción (Vercel,
# Render, etc.) se usa PostgreSQL configurado por variables de entorno.
# Vercel inyecta DATABASE_URL / POSTGRES_* al conectar la integración de Neon.
def _parse_db_url(url):
    """Parsea una URL tipo postgresql://usuario:pass@host:puerto/dbname."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return {
        'NAME': (parsed.path or '').lstrip('/'),
        'USER': parsed.username,
        'PASSWORD': parsed.password,
        'HOST': parsed.hostname,
        'PORT': str(parsed.port or '5432'),
    }


_db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or ''
_use_postgres = os.environ.get('DB_ENGINE') == 'postgres' or bool(_db_url)

if _use_postgres:
    _from_url = _parse_db_url(_db_url) if _db_url else {}
    _db_host = (
        _from_url.get('HOST')
        or os.environ.get('DB_HOST')
        or os.environ.get('POSTGRES_HOST')
        or os.environ.get('PGHOST')
        or ''
    )
    _db_opts = {}
    if _db_host and _db_host not in ('localhost', '127.0.0.1'):
        _db_opts = {'sslmode': 'require'}
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': (
                _from_url.get('NAME')
                or os.environ.get('DB_NAME')
                or os.environ.get('POSTGRES_DATABASE')
                or os.environ.get('PGDATABASE')
                or ''
            ),
            'USER': (
                _from_url.get('USER')
                or os.environ.get('DB_USER')
                or os.environ.get('POSTGRES_USER')
                or os.environ.get('PGUSER')
                or ''
            ),
            'PASSWORD': (
                _from_url.get('PASSWORD')
                or os.environ.get('DB_PASSWORD')
                or os.environ.get('POSTGRES_PASSWORD')
                or os.environ.get('PGPASSWORD')
                or ''
            ),
            'HOST': _db_host,
            'PORT': (
                _from_url.get('PORT')
                or os.environ.get('DB_PORT')
                or os.environ.get('PGPORT')
                or '5432'
            ),
            'CONN_MAX_AGE': 60,
            'OPTIONS': _db_opts,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# WhiteNoise sirve los estáticos en producción (Vercel, Render, etc.)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Autenticación web ---
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'


# --- Correo electrónico (notificaciones del portal) ---
# En desarrollo los correos se imprimen en la consola. Configurar un
# servidor SMTP real en producción.
EMAIL_BACKEND = os.environ.get(
    'DJANGO_EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('DJANGO_EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('DJANGO_EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', 'Tópico UNH <topico@unh.edu.pe>')


# --- Django REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
