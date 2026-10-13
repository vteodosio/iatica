from pathlib import Path
from decouple import config

import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-troque-em-producao')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'apps.accounts',
    'apps.groups',
    'apps.content',
    'apps.quiz',
    'apps.reports',
    'apps.chat',
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

ROOT_URLCONF = 'iatica_kids.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'iatica_kids.wsgi.application'

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/contas/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='iatica_kids'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# ── Chat IA (LLM) ─────────────────────────────────────────────────────────────
# Padrão 'mock': roda sem chave e sem custo (dev, testes e apresentação).
# Para usar um provedor real: LLM_PROVIDER=deepseek + LLM_API_KEY.
LLM_PROVIDER = config('LLM_PROVIDER', default='mock')
LLM_API_KEY = config('LLM_API_KEY', default='')
LLM_BASE_URL = config('LLM_BASE_URL', default='https://api.deepseek.com')
LLM_MODEL = config('LLM_MODEL', default='deepseek-flash')
LLM_MAX_TOKENS = config('LLM_MAX_TOKENS', default=400, cast=int)
LLM_TIMEOUT = config('LLM_TIMEOUT', default=30, cast=int)
CHAT_ATIVO = config('CHAT_ATIVO', default=True, cast=bool)
CHAT_RESPOSTA_MAX = config('CHAT_RESPOSTA_MAX', default=1200, cast=int)

