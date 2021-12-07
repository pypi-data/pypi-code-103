from tempfile import mkdtemp

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "yiv&ahwdi^^_(m63-%uok#9k6vp#6*p=@d+a=hk4vj62=me5&2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = []

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "titofisto.test_urls"

WSGI_APPLICATION = "titofisto_example.wsgi.application"

USE_TZ = True

MEDIA_ROOT = mkdtemp()
MEDIA_URL = "/media/"
