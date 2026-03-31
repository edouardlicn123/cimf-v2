# -*- coding: utf-8 -*-
"""
通用节点 URL 路由
"""

from django.urls import path
from . import views

app_name = 'node'

urlpatterns = [
    path('', views.nodes_index, name='index'),
    path('modules/', views.node_modules, name='modules'),
    path('modules/scan/', views.module_scan, name='module_scan'),
    path('modules/create/', views.module_create, name='module_create'),
    path('modules/create/action/', views.module_create_action, name='module_create_action'),
    path('modules/install/<str:module_id>/', views.module_install, name='module_install'),
    path('modules/enable/<str:module_id>/', views.module_enable, name='module_enable'),
    path('modules/disable/<str:module_id>/', views.module_disable, name='module_disable'),
    path('types/', views.node_types_list, name='node_types_list'),
    path('types/create/', views.node_type_create, name='node_type_create'),
    path('types/<int:node_type_id>/edit/', views.node_type_edit, name='node_type_edit'),
    path('types/<int:node_type_id>/toggle/', views.node_type_toggle, name='node_type_toggle'),
    path('types/<int:node_type_id>/delete/', views.node_type_delete, name='node_type_delete'),
    path('<slug:node_type_slug>/', views.node_list, name='node_list'),
    path('<slug:node_type_slug>/create/', views.node_create, name='node_create'),
    path('<slug:node_type_slug>/<int:node_id>/', views.node_view, name='node_view'),
    path('<slug:node_type_slug>/<int:node_id>/edit/', views.node_edit, name='node_edit'),
    path('<slug:node_type_slug>/<int:node_id>/delete/', views.node_delete, name='node_delete'),
]
