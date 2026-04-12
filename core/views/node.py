# -*- coding: utf-8 -*-
"""
节点管理视图模块
"""

from django.shortcuts import render
from core.decorators import admin_required


@admin_required
def node_dashboard(request):
    """节点仪表盘"""
    return render(request, 'structure/structure_dashboard.html', {
        'active_section': 'dashboard',
    })


@admin_required
def structure_dashboard(request):
    """内容结构首页"""
    return render(request, 'structure/structure_dashboard.html', {
        'active_section': 'dashboard',
    })


@admin_required
def node_list(request):
    """节点列表"""
    return render(request, 'structure/node_list.html', {
        'active_section': 'nodes',
    })


@admin_required
def node_create(request):
    """创建节点"""
    return render(request, 'structure/node_edit.html', {
        'node': None,
        'is_create': True,
    })


@admin_required
def node_edit(request, node_id: int):
    """编辑节点"""
    return render(request, 'structure/node_edit.html', {
        'node_id': node_id,
        'is_create': False,
    })


@admin_required
def node_delete(request, node_id: int):
    """删除节点"""
    from django.shortcuts import redirect
    return redirect('core:node_list')