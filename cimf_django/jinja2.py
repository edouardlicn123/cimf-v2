# -*- coding: utf-8 -*-
"""
================================================================================
文件：jinja2.py
路径：/home/edo/cimf-v2/cimf_django/jinja2.py
================================================================================

功能说明：
    Django Jinja2 自定义配置，添加 Django 特有的模板函数和过滤器

版本：
    - 1.0: 初始版本
    - 1.1: 添加 date 过滤器
    - 1.2: 修复 url() 函数支持位置参数
"""

from functools import partial
from django.templatetags.static import static
from django.urls import reverse
from django.utils.dateformat import format as date_format
from jinja2 import Environment


def jinja2_date_filter(value, format_string='Y-m-d H:i'):
    """Date filter for Jinja2 templates"""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    try:
        return date_format(value, format_string)
    except:
        return str(value)


def url_with_args(viewname, *args, **kwargs):
    """
    包装 reverse 函数，支持位置参数
    用法：{{ url('core:user_edit', u.id) }}
          {{ url('core:user_edit', user_id=u.id) }}
    """
    return reverse(viewname, args=args, kwargs=kwargs)


def environment(**options):
    """创建自定义 Jinja2 环境"""
    env = Environment(**options)
    
    def media(path):
        """生成媒体文件 URL"""
        from django.conf import settings
        return f"{settings.MEDIA_URL}{path}"
    
    # 添加 static 函数
    env.globals.update({
        'static': static,
        'url': url_with_args,
        'range': range,
        'media': media,
    })
    
    # 添加 date 过滤器
    env.filters['date'] = jinja2_date_filter
    
    return env
