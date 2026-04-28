# -*- coding: utf-8 -*-
"""
日志管理视图
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from core.decorators import admin_required
from core.services.log_service import LogService


@login_required
@admin_required
def logs_index(request):
    """日志管理首页 - 显示日志文件列表和统计"""
    log_files = LogService.get_log_files()
    
    stats = {}
    for log_file in log_files:
        if log_file['exists']:
            stats[log_file['key']] = LogService.get_log_stats(log_file['key'])
    
    return render(request, 'admin/logs.html', {
        'log_files': log_files,
        'stats': stats,
        'active_section': 'logs',
    })


@login_required
@admin_required
def logs_view(request, log_type):
    """查看指定日志 - 分页显示日志内容"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 100))
    level = request.GET.get('level', 'all')
    
    if log_type not in ['cimf', 'error', 'security']:
        log_type = 'cimf'
    
    log_data = LogService.read_log(log_type, page, page_size, level)
    log_files = LogService.get_log_files()
    stats = LogService.get_log_stats(log_type)
    
    return render(request, 'admin/logs.html', {
        'log_type': log_type,
        'log_files': log_files,
        'log_data': log_data,
        'stats': stats,
        'current_level': level,
        'active_section': 'logs',
    })


@login_required
@admin_required
def logs_api(request, log_type):
    """日志 API - JSON 接口"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 100))
    level = request.GET.get('level', 'all')
    
    if log_type not in ['cimf', 'error', 'security']:
        return JsonResponse({'error': 'Invalid log type'}, status=400)
    
    log_data = LogService.read_log(log_type, page, page_size, level)
    return JsonResponse(log_data)