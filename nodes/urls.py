# -*- coding: utf-8 -*-
"""
节点应用 URL 路由配置 - 仅包含客户模块

注意：导入导出相关 URL 指向 core.importexport.views
"""

from django.urls import path, include
from core.node import views as node_views
from core.node import views as core_node_views
from core.importexport import views as importexport_views

app_name = 'nodes'

urlpatterns = [
    # 首页
    path('', node_views.nodes_index, name='index'),
    
    # 客户模块
    path('customer/', include('nodes.customer.urls')),
    path('customer_cn/', include('nodes.customer_cn.urls')),
    
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
