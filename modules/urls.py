# -*- coding: utf-8 -*-
"""
模块 URL 路由配置 - 动态加载

使用动态安全加载机制，当模块文件夹不存在时自动忽略，
确保系统可以在没有任何模块的情况下启动。
"""

from django.urls import path, include
from importlib import import_module
from core.node import views as node_views

app_name = 'modules'


def try_include_module(module_slug):
    """尝试动态导入模块 URL，失败则返回空列表"""
    try:
        import_module(f'modules.{module_slug}.urls')
        return [path(f'{module_slug}/', include(f'modules.{module_slug}.urls'))]
    except (ImportError, ModuleNotFoundError, AttributeError):
        return []


def get_installed_module_slugs():
    """动态获取所有已安装模块的 slug"""
    try:
        from core.module.models import Module
        modules = Module.objects.filter(is_installed=True, is_active=True)
        return [m.module_id for m in modules]
    except Exception:
        return []


def get_dynamic_routes():
    """动态获取模块路由，每次调用时重新查询数据库"""
    slugs = get_installed_module_slugs()
    routes = []
    for _mod in slugs:
        routes.extend(try_include_module(_mod))
    return routes


urlpatterns = get_dynamic_routes() + [
    path('api/taxonomy-items/', node_views.taxonomy_items_api, name='taxonomy_items_api'),
]
