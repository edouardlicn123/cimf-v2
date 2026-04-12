# -*- coding: utf-8 -*-
"""
导入导出视图模块
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from core.services import PermissionService


@login_required
def importexport_dashboard(request):
    """数据导入导出首页"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')
    return render(request, 'importexport/importexport_dashboard.html', {
        'active_section': 'dashboard',
    })


@login_required
def import_list(request):
    """导入记录列表"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')
    return render(request, 'importexport/import_list.html', {
        'active_section': 'import',
    })


@login_required
def export_list(request):
    """导出记录列表"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')
    return render(request, 'importexport/export_list.html', {
        'active_section': 'export',
    })