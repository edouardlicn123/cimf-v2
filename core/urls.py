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

from django.urls import path, re_path, include
from . import views
from core.smtp import views as smtp_views
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
    
    # SMTP 邮件配置
    path('system/smtp/', smtp_views.smtp_config, name='smtp_config'),
    path('system/smtp/test/', smtp_views.smtp_test, name='smtp_test'),
    path('system/smtp/history/', smtp_views.smtp_history, name='smtp_history'),
    path('system/smtp/cleanup/', smtp_views.smtp_cleanup_logs, name='smtp_cleanup_logs'),
    
    # 日志管理
    path('system/logs/', views.logs_index, name='logs_index'),
    path('system/logs/<str:log_type>/', views.logs_view, name='logs_view'),
    
    # Cron API
    path('api/cron/status/', views.cron_status, name='cron_status'),
    path('api/cron/run/<str:task_name>/', views.cron_run_task, name='cron_run_task'),
    path('api/cron/toggle/<str:task_name>/', views.cron_toggle_task, name='cron_toggle_task'),
    
    # 内容结构
    path('structure/', views.structure_dashboard, name='structure_dashboard'),
    
    # 协作工具
    path('tools/', views.tools_index, name='tools_index'),
    re_path(r'^tools/(?P<tool_slug>[\w-]+)/$', views.tools_page, name='tools_page'),
    
    # 模块管理
    path('modules_manage/', node_views.node_modules, name='modules_manage'),
    
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
    path('profile/settings/homepage/', views.homepage_settings, name='homepage_settings'),
    
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
    
    # 功能卡片区域 API
    path('api/user/dashboard/cards/', views.api_dashboard_cards, name='api_dashboard_cards'),
    path('api/user/dashboard/cards/save/', views.api_dashboard_cards_save, name='api_dashboard_cards_save'),
    
    # 导航卡片
    path('user/nav-cards/', views.navigation_settings, name='navigation_settings'),
    path('api/user/nav-cards/', views.api_nav_cards, name='api_nav_cards'),
    path('api/user/nav-cards/save/', views.api_nav_cards_save, name='api_nav_cards_save'),
    
    # 健康检查
    path('health/', views.health_check, name='health_check'),
    path('health/detailed/', views.detailed_health_check, name='detailed_health_check'),
    path('api/version/', views.api_version, name='api_version'),
    
]
