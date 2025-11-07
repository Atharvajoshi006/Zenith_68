from pathlib import Path

# ---------------------------------------------
# BASE SETUP
# ---------------------------------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key'

# -----------------------------
# Debug and Allowed Hosts
# -----------------------------
DEBUG = True

ALLOWED_HOSTS = ["*", "127.0.0.1", "localhost"]

# -----------------------------
# CSRF and Session Settings
# -----------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    # add your LAN or tunnel origin if you use them:
    # "http://192.168.1.10:8000",
    # "https://<your-ngrok>.ngrok-free.app",
]

CSRF_COOKIE_SECURE = False   # safe for local development
SESSION_COOKIE_SECURE = False


# ---------------------------------------------
# INSTALLED APPS
# ---------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # <- must be here
    'core',
]



# ---------------------------------------------
# MIDDLEWARE
# ---------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ---------------------------------------------
# URLS / WSGI
# ---------------------------------------------
ROOT_URLCONF = 'adhyeta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Your HTML files live here
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

WSGI_APPLICATION = 'adhyeta.wsgi.application'


# ---------------------------------------------
# DATABASE
# ---------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------
# PASSWORDS
# ---------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ---------------------------------------------
# LANGUAGE / TIMEZONE
# ---------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# -----------------------
# ----------------------------------------
# ✅ Static files configuration (ready-to-paste)
# ----------------------------------------

# URL for static files (used in templates and HTML)
STATIC_URL = '/static/'

# Directory where your static files (like JS, CSS, images) are stored in development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Directory where all static files will be collected when running 'collectstatic'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media (if you ever add file uploads later)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

