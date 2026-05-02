# -*- coding: utf-8 -*-
"""
================================================================================================================================================
文件：views.py
路径：/home/edo/cimf-v2/core/node/views.py
================================================================================================================================================

功能说明：
    Node 节点系统视图，包含节点类型管理、节点仪表盘等

版本：
    - 1.0: 从 modules/views.py 迁移

依赖：
    - core.node.models: NodeType
    - core.node.services: NodeTypeService, NodeService
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from core.decorators import admin_required
from core.node.models import NodeType, Node, Module
from core.node.services import NodeTypeService, NodeService, ModuleService
from core.fields import get_all_field_types_info

logger = logging.getLogger(__name__)


@login_required
def nodes_index(request):
    """节点首页 - 只显示 node 类型的节点类型"""
    node_type_ids = Module.objects.filter(
        module_type='node',
        is_active=True
    ).values_list('module_id', flat=True)
    node_types = NodeType.objects.filter(slug__in=node_type_ids, is_active=True)
    return render(request, 'node/node_dashboard.html', {
        'node_types': node_types,
        'active_section': 'dashboard',
    })


@login_required
def node_types(request):
    """节点类型列表（重定向到 node_types_list）"""
    return redirect('node:node_types_list')


@admin_required
def node_types_list(request):
    """可用节点类型列表页"""
    node_types = NodeTypeService.get_all_including_inactive()
    return render(request, 'node/node_types_list.html', {
        'node_types': node_types,
        'active_section': 'node_types',
    })


@admin_required
def node_type_create(request):
    """创建节点类型"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        icon = request.POST.get('icon', 'bi-folder').strip()
        
        try:
            NodeTypeService.create({
                'name': name,
                'slug': slug,
                'description': description,
                'icon': icon,
                'fields_config': [],
                'is_active': True,
            })
            messages.success(request, '节点类型创建成功')
            return redirect('node:index')
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'node/types/edit.html', {
        'node_type': None,
        'active_section': 'node_types',
    })


@admin_required
def node_type_edit(request, node_type_id: int):
    """编辑节点类型"""
    node_type = get_object_or_404(NodeType, id=node_type_id)
    
    if request.method == 'POST':
        node_type.name = request.POST.get('name', '').strip()
        node_type.slug = request.POST.get('slug', '').strip()
        node_type.description = request.POST.get('description', '').strip()
        node_type.icon = request.POST.get('icon', 'bi-folder').strip()
        node_type.save()
        
        messages.success(request, '节点类型更新成功')
        return redirect('node:node_types_list')
    
    return render(request, 'node/types/edit.html', {
        'node_type': node_type,
        'active_section': 'node_types',
    })


@admin_required
def node_type_delete(request, node_type_id: int):
    """删除节点类型"""
    NodeTypeService.delete(node_type_id)
    messages.success(request, '节点类型已删除')
    return redirect('node:node_types_list')


@admin_required
def node_type_toggle(request, node_type_id: int):
    """切换节点类型启用/禁用状态"""
    success = NodeTypeService.toggle_active(node_type_id)
    status = '启用' if success else '禁用'
    messages.success(request, f'节点类型已{status}')
    return redirect('node:node_types_list')


@login_required
def node_list(request, node_type_slug: str):
    """节点列表页"""
    node_type = get_object_or_404(NodeType, slug=node_type_slug)
    if not node_type.is_active:
        messages.error(request, '该节点类型未启用')
        return redirect('node:index')
    
    nodes = NodeService.get_nodes(node_type_slug)
    return render(request, 'node/node_list.html', {
        'node_type': node_type,
        'nodes': nodes,
    })


@login_required
def node_create(request, node_type_slug: str):
    """创建节点"""
    if not request.user.is_admin:
        messages.error(request, '需要管理员权限')
        return redirect('core:dashboard')
    
    node_type = get_object_or_404(NodeType, slug=node_type_slug)
    if not node_type.is_active:
        messages.error(request, '该节点类型未启用')
        return redirect('node:index')
    
    return render(request, 'node/node_edit.html', {
        'node_type': node_type,
        'node': None,
    })


@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """查看节点"""
    node = get_object_or_404(Node, id=node_id, node_type__slug=node_type_slug)
    return render(request, 'node/node_detail.html', {
        'node': node,
    })


@login_required
def node_edit(request, node_type_slug: str, node_id: int):
    """编辑节点"""
    if not request.user.is_admin:
        messages.error(request, '需要管理员权限')
        return redirect('core:dashboard')
    
    node = get_object_or_404(Node.objects.select_related('node_type'), id=node_id, node_type__slug=node_type_slug)
    return render(request, 'node/node_edit.html', {
        'node_type': node.node_type,
        'node': node,
    })


@login_required
def node_delete(request, node_type_slug: str, node_id: int):
    """删除节点"""
    if not request.user.is_admin:
        messages.error(request, '需要管理员权限')
        return redirect('core:dashboard')
    
    node = get_object_or_404(Node, id=node_id, node_type__slug=node_type_slug)
    try:
        node.delete()
        messages.success(request, '节点已删除')
    except Exception as e:
        messages.error(request, f'删除节点失败: {str(e)}')
        logger.error(f"删除节点失败: node_id={node_id}, error={e}", exc_info=True)
    return redirect('node:node_list', node_type_slug)


@admin_required
def field_types(request):
    """字段类型列表"""
    field_types_info = get_all_field_types_info()
    return render(request, 'node/field_types.html', {
        'field_types': field_types_info,
        'active_section': 'field_types',
    })


@login_required
def field_types_api(request):
    """字段类型 API"""
    field_types_info = get_all_field_types_info()
    return JsonResponse({'field_types': field_types_info})


@login_required
def taxonomy_items_api(request):
    """获取词汇表项 API"""
    from core.models import Taxonomy, TaxonomyItem
    taxonomy_slug = request.GET.get('taxonomy')
    if not taxonomy_slug:
        return JsonResponse({'error': '缺少 taxonomy 参数'}, status=400)
    
    taxonomy = Taxonomy.objects.filter(slug=taxonomy_slug).first()
    if not taxonomy:
        return JsonResponse({'error': '词汇表不存在'}, status=404)
    
    items = taxonomy.items.values('id', 'name')
    return JsonResponse({'items': list(items)})


@admin_required
def node_modules(request):
    """模块管理页面"""
    modules = Module.objects.all().order_by('-is_active', 'module_type', 'name')
    return render(request, 'node/modules.html', {
        'modules': modules,
        'active_section': 'modules',
    })


@admin_required
def module_scan(request):
    """扫描并注册模块"""
    result = ModuleService.scan_and_register_modules()
    messages.success(request, f"扫描完成: 发现 {result['new']} 个新模块")
    return redirect('core:modules_manage')


@admin_required
def module_install(request, module_id: str):
    """安装模块"""
    success, message = ModuleService.install_module(module_id)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('core:modules_manage')


@admin_required
def module_enable(request, module_id: str):
    """启用模块"""
    success = ModuleService.enable_module(module_id)
    status = '启用' if success else '启用失败'
    messages.success(request, f'模块已{status}')
    return redirect('core:modules_manage')


@admin_required
def module_disable(request, module_id: str):
    """禁用模块"""
    success = ModuleService.disable_module(module_id)
    status = '禁用' if success else '禁用失败'
    messages.success(request, f'模块已{status}')
    return redirect('core:modules_manage')


@login_required
def module_dispatch(request, node_type_slug: str, node_id: int = None):
    """模块分发视图 - 根据节点类型动态加载对应模块的视图"""
    from django.urls import reverse
    module_path = node_type_slug
    
    try:
        module_views = __import__(f'modules.{module_path}.views', fromlist=[''])
        if hasattr(module_views, 'module_view'):
            return module_views.module_view(request, node_id)
        elif hasattr(module_views, 'detail_view') and node_id:
            return module_views.detail_view(request, node_id)
        elif hasattr(module_views, 'list_view'):
            return module_views.list_view(request)
    except ImportError:
        pass
    
    return redirect('node:node_list', node_type_slug)


@admin_required
def module_create(request):
    """模块创建页面"""
    return render(request, 'node/module_create.html', {
        'active_section': 'modules',
    })


@admin_required
def module_create_action(request):
    """创建模块"""
    name = request.POST.get('name', '').strip()
    module_id = request.POST.get('module_id', '').strip()
    module_type = request.POST.get('module_type', 'node').strip()
    description = request.POST.get('description', '').strip()
    
    if not name or not module_id:
        messages.error(request, '名称和标识不能为空')
        return redirect('node:module_create')
    
    try:
        ModuleService.create_module({
            'name': name,
            'module_id': module_id,
            'module_type': module_type,
            'description': description,
        })
        messages.success(request, '模块创建成功')
        return redirect('core:modules_manage')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('node:module_create')
