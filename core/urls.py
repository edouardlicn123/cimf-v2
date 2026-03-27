# -*- coding: utf-8 -*-
"""
================================================================================
文件：urls.py
路径：/home/edo/cimf-v2/core/urls.py
================================================================================

功能说明：
    核心应用 URL 路由配置，包括认证、管理后台、词汇表等路由
    
版本：
    - 1.0: 从 Flask 迁移

依赖：
    - core.views: 视图模块
"""

from django.urls import path
from . import views
from core.node import views as node_views

app_name = 'core'

urlpatterns = [
    # 认证
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    
    # 管理后台 (使用 /system/ 避免与 Django admin 冲突)
    path('system/', views.admin_dashboard, name='admin_dashboard'),
    path('system/users/', views.system_users, name='system_users'),
    path('system/user/create/', views.user_create, name='user_create'),
    path('system/user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('system/user/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('system/settings/', views.system_settings, name='system_settings'),
    path('system/permissions/', views.system_permissions, name='system_permissions'),
    path('system/cron/', views.cron_manager, name='cron_manager'),
    path('system/permission-check/', views.permission_check, name='permission_check'),
    
    # Cron API
    path('api/cron/status/', views.cron_status, name='cron_status'),
    path('api/cron/run/<str:task_name>/', views.cron_run_task, name='cron_run_task'),
    path('api/cron/toggle/<str:task_name>/', views.cron_toggle_task, name='cron_toggle_task'),
    
    # 内容结构
    path('structure/', views.structure_dashboard, name='structure_dashboard'),
    
    # 数据导入导出
    path('importexport/', views.importexport_dashboard, name='importexport_dashboard'),
    
    # 词汇表
    path('taxonomies/', views.taxonomies, name='taxonomies'),
    path('taxonomy/<int:taxonomy_id>/', views.taxonomy_view, name='taxonomy_view'),
    path('taxonomy/<int:taxonomy_id>/edit/', views.taxonomy_edit, name='taxonomy_edit'),
    path('taxonomy/create/', views.taxonomy_create, name='taxonomy_create'),
    path('taxonomy/<int:taxonomy_id>/delete/', views.taxonomy_delete, name='taxonomy_delete'),
    
    # 词汇项
    path('taxonomy/<int:taxonomy_id>/item/create/', views.taxonomy_item_create, name='taxonomy_item_create'),
    path('taxonomy/<int:taxonomy_id>/item/<int:item_id>/edit/', views.taxonomy_item_update, name='taxonomy_item_update'),
    path('taxonomy/<int:taxonomy_id>/item/<int:item_id>/delete/', views.taxonomy_item_delete, name='taxonomy_item_delete'),
    
    # Node 节点系统 - 已合并到 /node/modules/
    # 模块管理和节点类型管理现在都在 node_modules 页面
    
    # 仪表盘
    path('', views.dashboard, name='dashboard'),
    
    # 个人中心
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    
    # 时间 API
    path('api/time/current/', views.api_time_current, name='api_time_current'),
    path('api/time/test/', views.api_time_test, name='api_time_test'),
    path('api/time/status/', views.api_time_status, name='api_time_status'),
    
    # 地区 API
    path('api/regions/provinces/', views.api_regions_provinces, name='api_regions_provinces'),
    path('api/regions/cities/', views.api_regions_cities, name='api_regions_cities'),
    path('api/regions/districts/', views.api_regions_districts, name='api_regions_districts'),
    path('api/regions/search/', views.api_regions_search, name='api_regions_search'),
    path('api/regions/path/', views.api_regions_path, name='api_regions_path'),
    path('api/regions/stats/', views.api_regions_stats, name='api_regions_stats'),
    
]
