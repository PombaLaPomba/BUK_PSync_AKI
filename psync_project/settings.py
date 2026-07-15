"""
Django settings for the PSync / AKI project.

Kept deliberately plain: no Celery, no Docker requirement, no third-party
auth. Swap the DATABASES block for PostGIS when you're ready to add
proper geo-search (see comment below).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---------------------------------------------------------
# Replace this before deploying anywhere public. Keep it out of version
# control in production (env var / secrets file).
SECRET_KEY = "django-insecure-CHANGE-ME-BEFORE-DEPLOYING"
DEBUG = True
ALLOWED_HOSTS: list[str] = []

# --- APPS ---------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "crispy_forms",
    "crispy_bootstrap5",
    "psnv",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "psync_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "psync_project.wsgi.application"

# --- DATABASE -------------------------------------------------------------
# Start here on SQLite. When you migrate to Postgres/PostGIS for real
# geo-search (Standort.latitude/longitude -> PointField + Distance
# queries), swap this block and add "django.contrib.gis" to INSTALLED_APPS.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# DATABASES = {
#     "default": {
#         "ENGINE": "django.contrib.gis.db.backends.postgis",
#         "NAME": "psync",
#         "USER": "psync",
#         "PASSWORD": "...",
#         "HOST": "localhost",
#         "PORT": "5432",
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- crispy-forms ---------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- auth redirects ---------------------------------------------------------
LOGIN_REDIRECT_URL = "psnv:suche"
LOGOUT_REDIRECT_URL = "psnv:suche"
LOGIN_URL = "login"
