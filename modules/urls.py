# -*- coding: utf-8 -*-
"""
模块 URL 路由配置 - 动态加载

使用动态安全加载机制，当模块文件夹不存在时自动忽略，
确保系统可以在没有任何模块的情况下启动。
"""

from django.urls import path, include
from importlib import import_module
from core.node import views as node_views
from core.importexport import views as importexport_views

app_name = 'modules'


def try_include_module(module_slug):
    """尝试动态导入模块 URL，失败则返回空列表"""
    try:
        import_module(f'modules.{module_slug}.urls')
        return [path(f'{module_slug}/', include(f'modules.{module_slug}.urls'))]
    except (ImportError, ModuleNotFoundError, AttributeError):
        return []


_known_modules = ['clock', 'customer', 'customer_cn', 'resident_info']
_dynamic_routes = []
for _mod in _known_modules:
    _dynamic_routes.extend(try_include_module(_mod))


urlpatterns = [
    # 首页
    path('', node_views.nodes_index, name='index'),
] + _dynamic_routes + [
    # 字段类型 (must be before generic slug pattern)
    path('field-types/', node_views.field_types, name='field_types'),
    path('api/field-types/', node_views.field_types_api, name='field_types_api'),
    path('api/taxonomy-items/', node_views.taxonomy_items_api, name='taxonomy_items_api'),
    
    # 导出功能 (must be before generic slug pattern)
    path('export/', importexport_views.export_list, name='export_list'),
    path('export/<slug:node_type_slug>/', importexport_views.export_select_fields, name='export_select_fields'),
    path('export/<slug:node_type_slug>/confirm/', importexport_views.export_confirm, name='export_confirm'),
    path('export/<slug:node_type_slug>/exporting/', importexport_views.export_exporting, name='export_exporting'),
    path('export/<slug:node_type_slug>/do/', importexport_views.do_export, name='do_export'),
    
    # 导入功能 (must be before generic slug pattern)
    path('import/', importexport_views.import_list, name='import_list'),
    path('import/<slug:node_type_slug>/', importexport_views.import_page, name='import_page'),
    path('import/<slug:node_type_slug>/template/', importexport_views.download_template, name='download_template'),
    path('import/<slug:node_type_slug>/upload/', importexport_views.upload_preview, name='upload_preview'),
    path('import/<slug:node_type_slug>/do/', importexport_views.do_import, name='do_import'),
    path('import/<slug:node_type_slug>/errors/', importexport_views.download_errors, name='download_errors'),
    
    # 通用节点 (must be last)
    path('<slug:node_type_slug>/', node_views.node_list, name='node_list'),
    path('<slug:node_type_slug>/create/', node_views.node_create, name='node_create'),
    path('<slug:node_type_slug>/<int:node_id>/', node_views.node_view, name='node_view'),
    path('<slug:node_type_slug>/<int:node_id>/edit/', node_views.node_edit, name='node_edit'),
    path('<slug:node_type_slug>/<int:node_id>/delete/', node_views.node_delete, name='node_delete'),
]
