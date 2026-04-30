# -*- coding: utf-8 -*-
"""
================================================================================
文件：views.py
路径：/home/edo/cimf-v2/core/node/views.py
================================================================================

功能说明：
    Node 节点系统视图，包含节点类型管理、节点仪表盘等

版本：
    - 1.0: 从 modules/views.py 迁移

依赖：
    - core.node.models: NodeType
    - core.node.services: NodeTypeService, NodeService
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from core.decorators import admin_required
from core.node.models import NodeType, Module
from core.node.services import NodeTypeService, NodeService, ModuleService
from core.services import PermissionService
from core.fields import get_all_field_types_info


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
    return redirect('core:modules_manage')
    
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
    
    node = get_object_or_404(Node, id=node_id, node_type__slug=node_type_slug)
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
    node.delete()
    messages.success(request, '节点已删除')
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
    taxonomy_slug = request.GET.get('taxonomy')
    if not taxonomy_slug:
        return JsonResponse({'error': '缺少 taxonomy 参数'}, status=400)
    
    from core.models import Taxonomy, TaxonomyItem
    taxonomy = Taxonomy.objects.filter(slug=taxonomy_slug).first()
    if not taxonomy:
        return JsonResponse({'error': '词汇表不存在'}, status=404)
    
    items = taxonomy.items.values('id', 'name')
    return JsonResponse({'items': list(items)})


@admin_required
def node_modules(request):
    """模块管理页面"""
    from core.node.models import Module
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


@login_required
def node_types_list(request):
    """可用节点类型列表页"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    node_types = NodeTypeService.get_all_including_inactive()
    return render(request, 'node/node_types_list.html', {
        'node_types': node_types,
        'active_section': 'node_types',
    })


@login_required
def node_type_create(request):
    """创建节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
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


@login_required
def node_type_edit(request, node_type_id: int):
    """编辑节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    node_type = get_object_or_404(NodeType, id=node_type_id)
    
    if request.method == 'POST':
        node_type.name = request.POST.get('name', '').strip()
        node_type.slug = request.POST.get('slug', '').strip()
        node_type.description = request.POST.get('description', '').strip()
        node_type.icon = request.POST.get('icon', 'bi-folder').strip()
        node_type.save()
        
        messages.success(request, '节点类型更新成功')
    return redirect('core:modules_manage')
    
    return render(request, 'node/types/edit.html', {
        'node_type': node_type,
        'active_section': 'node_types',
    })


@login_required
def node_type_delete(request, node_type_id: int):
    """删除节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    NodeTypeService.delete(node_type_id)
    messages.success(request, '节点类型已删除')
    return redirect('node:node_types_list')


@login_required
def node_type_toggle(request, node_type_id: int):
    """切换节点类型启用/禁用状态"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要管理员权限访问该页面')
        return redirect('core:dashboard')
    
    node_type = NodeTypeService.get_by_id(node_type_id)
    if node_type:
        node_type.is_active = not node_type.is_active
        node_type.save()
        status = '启用' if node_type.is_active else '禁用'
        messages.success(request, f'节点类型已{status}')
    
    return redirect('node:node_types_list')


# ===== 通用节点 CRUD =====

def _check_module_installed(node_type_slug: str):
    """检查节点模块是否已安装并启用（防止循环重定向），未安装或非node类型则抛出 404"""
    from core.node.models import Module
    from django.http import Http404
    
    module = Module.objects.filter(
        module_id=node_type_slug,
        is_installed=True,
        is_active=True,
        module_type='node'
    ).first()
    
    if not module:
        raise Http404(f'节点模块 "{node_type_slug}" 未安装、未启用或不是节点类型')
    
    return module


@login_required
def node_list(request, node_type_slug: str):
    """通用节点列表（用于未来扩展的节点类型）"""
    _check_module_installed(node_type_slug)
    return redirect('modules:node_list', node_type_slug=node_type_slug)


@login_required
def node_create(request, node_type_slug: str):
    """通用节点创建（用于未来扩展的节点类型）"""
    _check_module_installed(node_type_slug)
    return redirect('modules:node_create', node_type_slug=node_type_slug)


@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """通用节点查看"""
    _check_module_installed(node_type_slug)
    return redirect('modules:node_view', node_type_slug=node_type_slug, node_id=node_id)


@login_required
def node_edit(request, node_type_slug: str, node_id: int):
    """通用节点编辑"""
    _check_module_installed(node_type_slug)
    return redirect('modules:node_edit', node_type_slug=node_type_slug, node_id=node_id)


@login_required
def node_delete(request, node_type_slug: str, node_id: int):
    """通用节点删除"""
    _check_module_installed(node_type_slug)
    node = NodeService.get_by_id(node_id)
    if node:
        NodeService.delete_node(node_id)
        messages.success(request, '节点已删除')
    return redirect('modules:node_list', node_type_slug=node_type_slug)


@login_required
def field_types(request):
    """字段类型列表页面"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    field_types_list = get_all_field_types_info()
    return render(request, 'structure/field_types/field_types.html', {
        'field_types': field_types_list,
        'active_section': 'field_types',
    })


@login_required
def field_types_api(request):
    """字段类型 API（JSON）"""
    field_types_list = get_all_field_types_info()
    return JsonResponse({'field_types': field_types_list})


@login_required
def taxonomy_items_api(request):
    """词汇表项 autocomplete API"""
    from core.models import TaxonomyItem
    taxonomy_slug = request.GET.get('taxonomy', '')
    search = request.GET.get('q', '')
    
    queryset = TaxonomyItem.objects.filter(taxonomy__slug=taxonomy_slug)
    if search:
        queryset = queryset.filter(name__icontains=search)
    
    items = [{'id': item.id, 'name': item.name} for item in queryset[:20]]
    return JsonResponse({'items': items})


@login_required
def node_modules(request):
    """Node 模块管理页 - 合并模块管理和节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    all_modules = ModuleService.scan_modules()
    registered = ModuleService.get_all()
    
    registered_ids = {m.module_id for m in registered}
    unregistered = [m for m in all_modules if m['id'] not in registered_ids]
    
    # 为每个已安装模块添加依赖信息
    for module in registered:
        if module.path:
            module_info = ModuleService._load_module_info(module.path)
            if module_info:
                module.dependencies = module_info.get('require', [])
            else:
                module.dependencies = None  # 解析失败
        else:
            module.dependencies = []
    
    node_types = NodeTypeService.get_all_including_inactive()
    
    return render(request, 'node/index.html', {
        'modules': registered,
        'unregistered_modules': unregistered,
        'node_types': node_types,
        'active_section': 'node_modules',
    })


@login_required
def module_scan(request):
    """扫描模块并同步节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    # 使用通用函数扫描、注册、安装
    result = ModuleService.scan_register_install(do_install=True, dry_run=False)
    
    # 显示结果消息
    msg = f"扫描完成: 注册 {result.get('registered', 0)} 个，安装 {result.get('installed', 0)} 个"
    messages.success(request, msg)
    
    if result.get('failed'):
        failed_msg = "失败列表: " + "; ".join(result['failed'])
        messages.error(request, failed_msg)
    
    return redirect('core:modules_manage')


@login_required
def module_install(request, module_id: str):
    """安装模块"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    module_info = ModuleService._load_module_info(module_id)
    if not module_info:
        messages.error(request, f'模块 {module_id} 不存在')
        return redirect('node:node_types_list')
    
    ok, err = ModuleService.verify_dependencies(module_id)
    if not ok:
        messages.error(request, f'无法安装模块：{err}')
        return redirect('core:modules_manage')
    
    module = ModuleService.register_module(module_info)
    ModuleService.install_module(module_id)
    
    messages.success(request, f'模块 {module_info["name"]} 已安装')
    return redirect('core:modules_manage')


@login_required
def module_enable(request, module_id: str):
    """启用模块"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')

    ok, err = ModuleService.verify_dependencies(module_id)
    if not ok:
        messages.error(request, f'无法启用模块：{err}')
        return redirect('core:modules_manage')

    if not ModuleService._check_tables_exist(module_id):
        ok, msg = ModuleService.install_module(module_id)
        if not ok:
            messages.error(request, f'安装失败：{msg}')
            return redirect('core:modules_manage')

    module = ModuleService.enable_module(module_id)
    if module:
        messages.success(request, f'模块 {module.name} 已启用')
    return redirect('core:modules_manage')


@login_required
def module_disable(request, module_id: str):
    """禁用模块"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    module = ModuleService.disable_module(module_id)
    if module:
        messages.success(request, f'模块 {module.name} 已禁用')
    return redirect('core:modules_manage')


@login_required
def module_dispatch(request, node_type_slug: str, node_id: int = None):
    """模块视图分发 - 根据 module.py 配置动态调用视图"""
    import importlib
    from django.http import Http404
    
    # 1. 检查模块是否已安装且启用
    module = Module.objects.filter(
        module_id=node_type_slug,
        is_installed=True,
        is_active=True
    ).first()
    
    if not module:
        raise Http404('模块不存在或未启用')
    
    # 2. 读取模块配置
    module_info = ModuleService._load_module_info(node_type_slug)
    if not module_info:
        raise Http404('模块配置无效')
    
    # 3. 确定要调用的视图函数
    view_config = module_info.get('views', {})
    
    # 根据请求路径确定要调用的函数名
    path_parts = request.path.strip('/').split('/')
    
    if len(path_parts) > 1:
        action = path_parts[1]
    else:
        action = 'list'
    
    # 映射到视图函数名
    if action == 'create':
        view_func_name = view_config.get('create')
    elif node_id:
        if 'edit' in request.path:
            view_func_name = view_config.get('edit')
        elif 'delete' in request.path:
            view_func_name = view_config.get('delete')
        else:
            view_func_name = view_config.get('view')
    else:
        view_func_name = view_config.get('list')
    
    if not view_func_name:
        raise Http404('模块未配置视图函数')
    
    # 4. 动态导入并调用视图
    try:
        module_views = importlib.import_module(f'modules.{node_type_slug}.views')
        view_func = getattr(module_views, view_func_name)
        return view_func(request, node_id=node_id) if node_id else view_func(request)
    except (ImportError, AttributeError) as e:
        raise Http404(f'模块视图函数不存在: {e}')


@login_required
def module_create(request):
    """创建模块页面"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    return render(request, 'node/modules/create.html', {
        'active_section': 'node_modules',
    })


@login_required
def module_create_action(request):
    """创建模块动作"""
    if not PermissionService.can_access_admin(request.user):
        return JsonResponse({'success': False, 'error': '需要系统管理员权限'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=400)
    
    module_id = request.POST.get('module_id', '').strip()
    name = request.POST.get('name', '').strip()
    module_type = request.POST.get('module_type', 'node').strip()
    description = request.POST.get('description', '').strip()
    icon = request.POST.get('icon', 'bi-folder').strip()
    
    if not module_id:
        return JsonResponse({'success': False, 'error': '请输入模块 ID'}, status=400)
    
    if not name:
        return JsonResponse({'success': False, 'error': '请输入模块名称'}, status=400)
    
    if not module_type:
        return JsonResponse({'success': False, 'error': '请输入模块类型'}, status=400)
    
    result = ModuleService.create_module(module_id, name, module_type, description, icon)
    
    if result.get('success'):
        return JsonResponse({'success': True, 'module_id': result['module_id']})
    else:
        return JsonResponse({'success': False, 'error': result.get('error', '创建失败')}, status=400)
