"""
================================================================================
文件：settings.py
路径：/home/edo/cimf-v2/cimf_django/settings.py
================================================================================

功能说明：
    Django 项目配置文件，包含应用设置、数据库、模板引擎等配置。
    
版本：
    - 1.0: 初始版本

依赖：
    - django: 6.0+
    - djangorestframework: 用于 REST API
    - jinja2: 模板引擎（兼容现有模板）
"""

from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
import os

# 尝试加载 config.env 文件
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, 'config.env'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9dtjvn^e5l-o7k12i*0_2ez**pbtje4ik=v*)a42t+r=n2rt#l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

# 基础应用（必须保留）
_base_apps = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'nodes',
]

# 动态扫描 nodes/ 下的模块
_node_modules = []
_nodes_dir = os.path.join(BASE_DIR, 'nodes')
if os.path.isdir(_nodes_dir):
    for item in os.listdir(_nodes_dir):
        module_path = os.path.join(_nodes_dir, item)
        if os.path.isdir(module_path) and os.path.exists(os.path.join(module_path, 'module.py')):
            _node_modules.append(f'nodes.{item}')

INSTALLED_APPS = _base_apps + _node_modules

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cimf_django.urls'

# Jinja2 模板引擎配置（兼容现有 Flask 模板）
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            BASE_DIR / 'core' / 'templates',
            BASE_DIR / 'nodes' / 'customer' / 'templates',
            BASE_DIR / 'nodes' / 'customer_cn' / 'templates',
            BASE_DIR / 'core' / 'node' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'cimf_django.jinja2.environment',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cimf_django.context_processors.system_settings',
                'cimf_django.context_processors.csrf_token',
                'cimf_django.context_processors.user_permissions',
            ],
            'extensions': [
                'jinja2.ext.loopcontrols',
                'jinja2.ext.do',
                'jinja2.ext.i18n',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cimf_django.context_processors.system_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'cimf_django.wsgi.application'

# Database - 使用 SQLite，Django 专用数据库（与 Flask 分离）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'instance' / 'django.db',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Auth 配置
AUTH_USER_MODEL = 'core.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Django REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# Flash/Toast 消息配置
MESSAGE_TAGS = {
    'debug': 'alert-info',
    'info': 'alert-info',
    'success': 'alert-success',
    'warning': 'alert-warning',
    'error': 'alert-danger',
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging Configuration
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
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 自定义错误页面处理（跟随主题）
handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
