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

# pymysql 兼容性处理（使用 MySQL 时需要）
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

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
    'modules',
]

# 动态扫描 modules/ 下的模块及其模板目录
_node_modules = []
_module_template_dirs = []
_nodes_dir = os.path.join(BASE_DIR, 'modules')
if os.path.isdir(_nodes_dir):
    for item in os.listdir(_nodes_dir):
        module_path = os.path.join(_nodes_dir, item)
        if os.path.isdir(module_path) and os.path.exists(os.path.join(module_path, 'module.py')):
            _node_modules.append(f'modules.{item}')
            # 收集模块的 templates 目录
            template_dir = os.path.join(module_path, 'templates')
            if os.path.isdir(template_dir):
                _module_template_dirs.append(Path(template_dir))

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
# 动态收集所有模板目录
_template_dirs = [
    BASE_DIR / 'core' / 'templates',
    BASE_DIR / 'core' / 'node' / 'templates',
    BASE_DIR / 'core' / 'node' / 'templates' / 'types',
    BASE_DIR / 'core' / 'importexport' / 'templates',
] + _module_template_dirs

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': _template_dirs,
        'APP_DIRS': False,
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
                'jinja2.ext.debug',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': _template_dirs,
        'APP_DIRS': False,
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

# Database - 根据 config.env 配置选择 SQLite 或 MySQL
from cimf_django.database import get_database_config
DATABASES = {
    'default': get_database_config()
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
STATIC_ROOT = BASE_DIR / 'storage' / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'storage' / 'uploads'

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
