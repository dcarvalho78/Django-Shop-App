from pathlib import Path
import os
import dj_database_url  # Render/12factor DB parsing

BASE_DIR = Path(__file__).resolve().parent.parent

# Geheimnis aus ENV (Render setzt SECRET_KEY), lokal fallback auf bisherigen Wert
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-+64kn9qjz4y-7u)+$j#w0gcwe-j8elkr74w=xvpqy3hz-r2q+^",
)

# DEBUG per ENV steuerbar (DEBUG=true), sonst False
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "t", "yes", "y")

# Hosts: lokal + Render
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# Für CSRF auf Render: https://<render-host>
CSRF_TRUSTED_ORIGINS = []
if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # eigene Apps
    "store",
    "cart",
    "checkout",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static Files in Prod
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Für korrektes HTTPS hinter Proxy (Render)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

ROOT_URLCONF = "shop.urls"

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
                "cart.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "shop.wsgi.application"  # passt für Gunicorn/Render

# Datenbank: Render via DATABASE_URL, lokal Fallback auf deine PG-Instanz
DATABASES = {
    "default": dj_database_url.config(
        default="postgresql://shop_user:NeuesSicheresPasswort@127.0.0.1:5432/shop_db",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static/Media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # deine Entwicklungs-Assets

if not DEBUG:
    STATIC_ROOT = BASE_DIR / "staticfiles"  # Render sammelt hier Datei-Assets
    # Django ≥4.2: STORAGES statt STATICFILES_STORAGE
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login/Logout Redirects
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django.contrib.auth": {"handlers": ["console"], "level": "DEBUG"}},
}
