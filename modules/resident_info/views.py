# -*- coding: utf-8 -*-
"""
居民信息模块视图
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse

from core.node.services import NodeTypeService, NodeService
from core.services import TaxonomyService
from .services import ResidentInfoService


def safe_int(value: str, default=None):
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def check_resident_permission(user, node, permission_type: str):
    """检查居民节点操作权限"""
    if user.is_admin:
        return True, None
    
    is_creator = node.created_by_id == user.id
    if is_creator:
        return True, None
    
    perm_map = {
        'view': 'node.resident_info.view_others',
        'edit': 'node.resident_info.edit_others',
        'delete': 'node.resident_info.delete_others',
    }
    
    perm = perm_map.get(permission_type)
    if perm:
        from core.services import PermissionService
        if PermissionService.has_permission(user, perm):
            return True, None
    
    return False, f'您没有权限{permission_type}别人的居民信息'


def get_taxonomy_items(slug: str):
    tax = TaxonomyService.get_taxonomy_by_slug(slug)
    if tax:
        return list(TaxonomyService.get_items(tax.id))
    return []


@login_required
def node_list(request):
    node_type = NodeTypeService.get_by_slug('resident_info')
    if not node_type:
        from django.http import Http404
        raise Http404('节点类型不存在')
    
    search = request.GET.get('search', '')
    resident_type_filter = request.GET.get('resident_type', '')
    grid_filter = request.GET.get('grid', '')
    
    resident_type_id = safe_int(resident_type_filter)
    grid_id = safe_int(grid_filter)
    
    residents = ResidentInfoService.get_list(
        search if search else None,
        resident_type_id=resident_type_id,
        grid_id=grid_id,
        user=request.user
    )
    
    page_num = request.GET.get('page', 1)
    paginator = Paginator(residents, 10)
    page_obj = paginator.get_page(page_num)
    
    return render(request, 'resident_info/list.html', {
        'node_type': node_type,
        'node_types': NodeTypeService.get_all(),
        'residents': page_obj.object_list,
        'search': search,
        'active_section': 'resident_info',
        'filter_resident_type': resident_type_filter,
        'filter_grid': grid_filter,
        'resident_types': get_taxonomy_items('resident_type'),
        'grids': get_taxonomy_items('grid'),
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })


@login_required
def node_create(request):
    node_type = NodeTypeService.get_by_slug('resident_info')
    if not node_type:
        from django.http import Http404
        raise Http404('节点类型不存在')
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', '').strip(),
            'relation_id': request.POST.get('relation') or None,
            'id_card': request.POST.get('id_card', '').strip() or None,
            'gender_id': request.POST.get('gender') or None,
            'birth_date': request.POST.get('birth_date') or None,
            'phone': request.POST.get('phone', '').strip() or None,
            'current_community': request.POST.get('current_community', '').strip() or None,
            'current_door': request.POST.get('current_door', '').strip() or None,
            'grid_id': request.POST.get('grid') or None,
            'resident_type_id': request.POST.get('resident_type') or None,
            'is_key_person': request.POST.get('is_key_person') == 'on',
            'key_category_id': request.POST.get('key_category') or None,
            'registered_community': request.POST.get('registered_community', '').strip() or None,
            'registered_address': request.POST.get('registered_address', '').strip() or None,
            'registered_region': request.POST.get('registered_region') or None,
            'household_number': request.POST.get('household_number', '').strip() or None,
            'is_separated': request.POST.get('is_separated') == 'on',
            'actual_residence': request.POST.get('actual_residence', '').strip() or None,
            'is_moved_out': request.POST.get('is_moved_out') == 'on',
            'move_out_date': request.POST.get('move_out_date') or None,
            'move_to_place': request.POST.get('move_to_place', '').strip() or None,
            'is_deceased': request.POST.get('is_deceased') == 'on',
            'death_date': request.POST.get('death_date') or None,
            'nation_id': request.POST.get('nation') or None,
            'political_status_id': request.POST.get('political_status') or None,
            'marital_status_id': request.POST.get('marital_status') or None,
            'education_id': request.POST.get('education') or None,
            'work_status': request.POST.get('work_status', '').strip() or None,
            'health_status_id': request.POST.get('health_status') or None,
            'notes': request.POST.get('notes', '').strip() or None,
        }
        
        try:
            ResidentInfoService.create(request.user, data)
            messages.success(request, '居民信息创建成功')
            return redirect('modules:resident_info:list')
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'resident_info/edit.html', {
        'node_type': node_type,
        'node_types': NodeTypeService.get_all(),
        'resident': None,
        'active_section': 'resident_info',
        'relations': get_taxonomy_items('resident_relation'),
        'genders': get_taxonomy_items('gender'),
        'resident_types': get_taxonomy_items('resident_type'),
        'grids': get_taxonomy_items('grid'),
        'key_categories': get_taxonomy_items('key_category'),
        'nations': get_taxonomy_items('nation'),
        'political_statuses': get_taxonomy_items('political_status'),
        'marital_statuses': get_taxonomy_items('marital_status'),
        'educations': get_taxonomy_items('education'),
        'health_statuses': get_taxonomy_items('health_status'),
    })


@login_required
def node_view(request, node_id: int):
    node = NodeService.get_by_id(node_id)
    if not node:
        from django.http import Http404
        raise Http404('节点不存在')
    
    has_perm, error_msg = check_resident_permission(request.user, node, 'view')
    if not has_perm:
        messages.error(request, error_msg)
        return redirect('modules:resident_info:list')
    
    resident = ResidentInfoService.get_by_node_id(node_id)
    if not resident:
        messages.error(request, '居民信息不存在')
        return redirect('modules:resident_info:list')
    
    return render(request, 'resident_info/view.html', {
        'node_type': node.node_type,
        'node_types': NodeTypeService.get_all(),
        'node': node,
        'resident': resident,
        'active_section': 'resident_info',
    })


@login_required
def node_edit(request, node_id: int):
    node = NodeService.get_by_id(node_id)
    if not node:
        from django.http import Http404
        raise Http404('节点不存在')
    
    has_perm, error_msg = check_resident_permission(request.user, node, 'edit')
    if not has_perm:
        messages.error(request, error_msg)
        return redirect('modules:resident_info:view', node_id=node_id)
    
    resident = ResidentInfoService.get_by_node_id(node_id)
    if not resident:
        messages.error(request, '居民信息不存在')
        return redirect('modules:resident_info:list')
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', '').strip(),
            'relation_id': request.POST.get('relation') or None,
            'id_card': request.POST.get('id_card', '').strip() or None,
            'gender_id': request.POST.get('gender') or None,
            'birth_date': request.POST.get('birth_date') or None,
            'phone': request.POST.get('phone', '').strip() or None,
            'current_community': request.POST.get('current_community', '').strip() or None,
            'current_door': request.POST.get('current_door', '').strip() or None,
            'grid_id': request.POST.get('grid') or None,
            'resident_type_id': request.POST.get('resident_type') or None,
            'is_key_person': request.POST.get('is_key_person') == 'on',
            'key_category_id': request.POST.get('key_category') or None,
            'registered_community': request.POST.get('registered_community', '').strip() or None,
            'registered_address': request.POST.get('registered_address', '').strip() or None,
            'registered_region': request.POST.get('registered_region') or None,
            'household_number': request.POST.get('household_number', '').strip() or None,
            'is_separated': request.POST.get('is_separated') == 'on',
            'actual_residence': request.POST.get('actual_residence', '').strip() or None,
            'is_moved_out': request.POST.get('is_moved_out') == 'on',
            'move_out_date': request.POST.get('move_out_date') or None,
            'move_to_place': request.POST.get('move_to_place', '').strip() or None,
            'is_deceased': request.POST.get('is_deceased') == 'on',
            'death_date': request.POST.get('death_date') or None,
            'nation_id': request.POST.get('nation') or None,
            'political_status_id': request.POST.get('political_status') or None,
            'marital_status_id': request.POST.get('marital_status') or None,
            'education_id': request.POST.get('education') or None,
            'work_status': request.POST.get('work_status', '').strip() or None,
            'health_status_id': request.POST.get('health_status') or None,
            'notes': request.POST.get('notes', '').strip() or None,
        }
        
        try:
            ResidentInfoService.update(resident.id, request.user, data)
            messages.success(request, '居民信息更新成功')
            return redirect('modules:resident_info:view', node_id=node_id)
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'resident_info/edit.html', {
        'node_type': node.node_type,
        'node_types': NodeTypeService.get_all(),
        'node': node,
        'resident': resident,
        'active_section': 'resident_info',
        'relations': get_taxonomy_items('resident_relation'),
        'genders': get_taxonomy_items('gender'),
        'resident_types': get_taxonomy_items('resident_type'),
        'grids': get_taxonomy_items('grid'),
        'key_categories': get_taxonomy_items('key_category'),
        'nations': get_taxonomy_items('nation'),
        'political_statuses': get_taxonomy_items('political_status'),
        'marital_statuses': get_taxonomy_items('marital_status'),
        'educations': get_taxonomy_items('education'),
        'health_statuses': get_taxonomy_items('health_status'),
    })


@login_required
def node_delete(request, node_id: int):
    node = NodeService.get_by_id(node_id)
    if node:
        has_perm, error_msg = check_resident_permission(request.user, node, 'delete')
        if not has_perm:
            messages.error(request, error_msg)
        else:
            ResidentInfoService.delete(node_id)
            messages.success(request, '居民信息已删除')
    
    return redirect('modules:resident_info:list')


@login_required
def api_stats(request):
    total = ResidentInfoService.get_count()
    recent = ResidentInfoService.get_recent_count(days=7)
    
    return JsonResponse({
        'success': True,
        'data': {
            'total': total,
            'recent': recent,
        }
    })