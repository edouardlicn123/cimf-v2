# -*- coding: utf-8 -*-
"""
================================================================================
文件：context_processors.py
路径：/home/edo/cimf-v2/cimf_django/context_processors.py
================================================================================

功能说明：
    Django 模板上下文处理器，为所有模板提供公共变量

版本：
    - 1.0: 初始版本
"""

import time
from core.services import SettingsService


def system_settings(request):
    """
    为所有模板提供系统设置
    """
    try:
        settings = SettingsService.get_all_settings()
        return {
            'system_name': settings.get('system_name', 'CIMF'),
            'system_settings': settings,
            'timestamp': int(time.time()),
        }
    except:
        return {
            'system_name': 'CIMF',
            'system_settings': {},
            'timestamp': int(time.time()),
        }


def csrf_token(request):
    """
    为 Jinja2 模板提供 CSRF token
    """
    from django.middleware.csrf import get_token
    from django.utils.html import format_html
    
    token = get_token(request)
    csrf_html = format_html('<input type="hidden" name="csrfmiddlewaretoken" value="{}">', token)
    return {'csrf_token': csrf_html}


def user_permissions(request):
    """
    为所有模板提供用户权限信息
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {'user_permissions': []}
    
    from core.services.permission_service import PermissionService
    
    return {
        'user_permissions': PermissionService.get_user_effective_permissions(request.user)
    }
