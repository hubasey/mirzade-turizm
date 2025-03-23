import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Proje dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# Güvenlik Ayarları
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Uygulamalar
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'main',
    'editor',
    'photologue',
    'django_ckeditor_5',
    'corsheaders',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'csp.middleware.CSPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mirzade.urls'

# Şablonlar
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'mirzade.wsgi.application'

# Veritabanı
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# Parola doğrulama
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Uluslararasılaştırma
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Statik ve Medya Dosyaları
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Whitenoise ile Statik Dosya Yönetimi - Geliştirme ve Canlı Ortam için farklı yapılandırmalar
if DEBUG:
    # Geliştirmede standart storage kullanarak önbellekleme sorunlarını engelle
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    # Canlı ortamda sıkıştırma ve önbellekleme kullan
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Varsayılan birincil anahtar alan türü
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID
SITE_ID = 1

# CKEditor 5 Ayarları
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Kırmızı"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pembe"},
    {"color": "hsl(291, 64%, 42%)", "label": "Mor"},
    {"color": "hsl(262, 52%, 47%)", "label": "Mor"},
    {"color": "hsl(231, 48%, 48%)", "label": "Mavi"},
    {"color": "hsl(207, 90%, 54%)", "label": "Mavi"},
    {"color": "hsl(187, 100%, 42%)", "label": "Turkuaz"},
    {"color": "hsl(152, 100%, 29%)", "label": "Yeşil"},
    {"color": "hsl(122, 39%, 49%)", "label": "Yeşil"},
    {"color": "hsl(45, 100%, 51%)", "label": "Sarı"},
    {"color": "hsl(36, 100%, 50%)", "label": "Turuncu"},
    {"color": "hsl(14, 91%, 54%)", "label": "Turuncu"},
    {"color": "hsl(0, 0%, 0%)", "label": "Siyah"},
    {"color": "hsl(0, 0%, 87%)", "label": "Gri"},
    {"color": "hsl(0, 0%, 100%)", "label": "Beyaz"},
]

# Yetkilendirme Ayarları
LOGIN_URL = '/editor/login/'
LOGIN_REDIRECT_URL = '/editor/'
LOGOUT_REDIRECT_URL = '/editor/login/'

# E-Posta Ayarları
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"Mirzade Turizm <{EMAIL_HOST_USER}>"
# E-posta ayarlarında debug modda hata ayıklama
if DEBUG:
    EMAIL_DEBUG = True  # Hata ayıklama etkin
else:
    EMAIL_DEBUG = False  # Canlı ortamda hata ayıklama kapalı

# Güvenlik Ayarları
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Sadece production ortamında SSL ayarlarını etkinleştir
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # HTTP isteklerini HTTPS'e yönlendirir
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Geliştirme ortamında SSL ayarlarını devre dışı bırak
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS Ayarları
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if not DEBUG:
    CORS_ALLOWED_ORIGINS += [
        "https://mirzadeturizm.com",
        "https://www.mirzadeturizm.com",
    ]

# CSP Ayarları (Content Security Policy)
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "fonts.googleapis.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com")
CSP_IMG_SRC = ("'self'", "data:", "*.mirzadeturizm.com")
CSP_FRAME_SRC = ("'self'", "www.google.com", "maps.google.com", "*.google.com")

# Redis Önbellek
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Önbellek anahtar öneki
CACHE_KEY_PREFIX = "mirzade"

# Oturum yönetiminde Redis kullanma
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Google Places API
GOOGLE_PLACE_ID = 'ChIJw6cPuX66yhQRrSY4T3IiFRo'
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'main': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
