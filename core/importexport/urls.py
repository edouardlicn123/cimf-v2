# -*- coding: utf-8 -*-
"""
导入导出 URL 路由
"""

from django.urls import path
from . import views

app_name = 'importexport'

urlpatterns = [
    path('export/', views.export_list, name='export_list'),
    path('export/<slug:node_type_slug>/', views.export_select_fields, name='export_select_fields'),
    path('export/<slug:node_type_slug>/confirm/', views.export_confirm, name='export_confirm'),
    path('export/<slug:node_type_slug>/exporting/', views.export_exporting, name='export_exporting'),
    path('export/<slug:node_type_slug>/do/', views.do_export, name='do_export'),
]

urlpatterns_import = [
    path('import/', views.import_list, name='import_list'),
    path('import/<slug:node_type_slug>/', views.import_page, name='import_page'),
    path('import/<slug:node_type_slug>/template/', views.download_template, name='download_template'),
    path('import/<slug:node_type_slug>/upload/', views.upload_preview, name='upload_preview'),
    path('import/<slug:node_type_slug>/do/', views.do_import, name='do_import'),
    path('import/<slug:node_type_slug>/errors/', views.download_errors, name='download_errors'),
]
