# -*- coding: utf-8 -*-
"""
================================================================================
文件：views.py
路径：/home/edo/cimf-v2/core/views.py
================================================================================

功能说明：
    核心应用视图，包含认证、管理后台、词汇表等页面视图
    
版本：
    - 1.0: 从 Flask 迁移

依赖：
    - django: Web 框架
    - core.services: 服务层
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from core.models import User, Taxonomy
from core.services import SettingsService, PermissionService, UserService, AuthService, TimeService, get_cron_service
from core.services.permission_service import UserRole
from core.forms import ProfileForm, PreferencesForm, ChangePasswordForm

def login_view(request):
    """
    用户登录页面
    
    GET: 显示登录表单
    POST: 处理登录请求
    """
    if request.user.is_authenticated:
        messages.info(request, '您已登录，无需重复登录')
        return redirect('core:dashboard')
    
    error_message = None
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        result = AuthService.login(request, username, password)
        
        if result['success']:
            user = result['user']
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')
        else:
            error_message = result['message']
    
    return render(request, 'core/auth/login.html', {
        'error_message': error_message,
        'settings': SettingsService.get_all_settings(),
    })


def logout_view(request):
    """用户登出"""
    logout(request)
    messages.info(request, '您已安全退出登录')
    return redirect('core:login')


@login_required
def dashboard(request):
    """仪表盘"""
    stats = UserService.get_user_stats()
    settings = SettingsService.get_all_settings()
    user_display_name = request.user.nickname or request.user.username
    settings['welcome_subtitle'] = settings.get('welcome_subtitle') or '让我们一起把项目完善吧。'
    settings['welcome_intro'] = settings.get('welcome_intro') or '初始用户名：admin 初始密码：admin123'
    
    return render(request, 'core/dashboard.html', {
        'stats': stats,
        'settings': settings,
        'user_display_name': user_display_name,
        'page_title': user_display_name,
    })


@login_required
def admin_dashboard(request):
    """管理后台仪表盘"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    return redirect('core:system_settings')


@login_required
def system_users(request):
    """系统用户列表"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    search_term = request.GET.get('search', '')
    only_active = request.GET.get('only_active', 'true') == 'true'
    role_filter = request.GET.get('role_filter', '')
    
    users = UserService.get_user_list(
        search_term=search_term if search_term else None,
        only_active=only_active,
        exclude_admin=True,
        role=role_filter if role_filter else None
    )
    
    return render(request, 'core/admin/system_users.html', {
        'users': users,
        'search_term': search_term,
        'only_active': only_active,
        'role_filter': role_filter,
        'active_section': 'users',
    })


@login_required
def user_create(request):
    """创建用户"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        nickname = request.POST.get('nickname', '').strip()
        email = request.POST.get('email', '').strip() or None
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'employee')
        is_admin = request.POST.get('is_admin') == 'on'
        
        try:
            UserService.create_user(
                username=username,
                nickname=nickname or username,
                email=email,
                password=password,
                role=role,
                is_admin=is_admin
            )
            messages.success(request, '用户创建成功')
            return redirect('core:system_users')
        except ValueError as e:
            messages.error(request, str(e))
    
    return render(request, 'core/admin/system_user_edit.html', {
        'user': None,
        'is_create': True,
    })


@login_required
def user_edit(request, user_id: int):
    """编辑用户"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if user_id == 1:
        messages.error(request, '系统管理员账号禁止编辑')
        return redirect('core:system_users')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        nickname = request.POST.get('nickname', '').strip()
        email = request.POST.get('email', '').strip() or None
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'employee')
        is_admin = request.POST.get('is_admin') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            UserService.update_user(
                user_id=user_id,
                username=username,
                nickname=nickname,
                email=email,
                password=password if password else None,
                role=role,
                is_admin=is_admin,
                is_active=is_active
            )
            messages.success(request, '用户信息更新成功')
            return redirect('core:system_users')
        except (ValueError, PermissionError) as e:
            messages.error(request, str(e))
    
    return render(request, 'core/admin/system_user_edit.html', {
        'user': user,
        'is_create': False,
    })


@login_required
def user_delete(request, user_id: int):
    """删除用户"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    if user_id == 1:
        messages.error(request, '系统管理员账号禁止删除')
        return redirect('core:system_users')
    
    if user_id == request.user.id:
        messages.error(request, '禁止删除当前登录账号')
        return redirect('core:system_users')
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, '用户已删除')
    return redirect('core:system_users')


@login_required
def system_settings(request):
    """系统设置页面"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        settings_dict = {}
        
        # 处理所有设置项
        for key in SettingsService.DEFAULT_SETTINGS.keys():
            # 布尔类型设置（checkbox）
            if key in ['enable_audit_log', 'enable_web_watermark', 'enable_watermark_console_detection',
                       'enable_watermark_shortcut_block', 'enable_export_watermark',
                       'cron_time_sync_enabled', 'cron_cache_cleanup_enabled', 'site_logo_enabled']:
                value = 'true' if request.POST.get(key) else 'false'
            # 多选类型（水印显示内容）
            elif key == 'web_watermark_content':
                values = request.POST.getlist(key)
                value = ','.join(values) if values else ''
            else:
                value = request.POST.get(key)
            
            if value is not None:
                settings_dict[key] = value
        
        # 处理 Logo 上传
        logo_file = request.FILES.get('site_logo_upload')
        if logo_file:
            import os
            from django.conf import settings
            
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'logos')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 删除旧文件
            old_path = os.path.join(upload_dir, 'custom.png')
            if os.path.exists(old_path):
                os.remove(old_path)
            
            # 保存新文件
            with open(old_path, 'wb+') as destination:
                for chunk in logo_file.chunks():
                    destination.write(chunk)
            
            settings_dict['site_logo_path'] = 'logos/custom.png'
        
        SettingsService.save_settings_bulk(settings_dict)
        messages.success(request, '系统设置已保存')
        return redirect('core:system_settings')
    
    settings = SettingsService.get_all_settings()
    return render(request, 'core/admin/system_settings.html', {
        'settings': settings,
        'active_section': 'settings',
    })


@login_required
def system_permissions(request):
    """权限管理页面"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # 保存经理权限
        manager_perms = request.POST.getlist('permissions_manager')
        PermissionService.save_role_permissions('manager', manager_perms)
        
        # 保存组长权限
        leader_perms = request.POST.getlist('permissions_leader')
        PermissionService.save_role_permissions('leader', leader_perms)
        
        # 保存员工权限
        employee_perms = request.POST.getlist('permissions_employee')
        PermissionService.save_role_permissions('employee', employee_perms)
        
        # 保存角色名称
        from core.models import SystemSetting
        for role in ['manager', 'leader', 'employee']:
            role_name = request.POST.get(f'role_name_{role}', '').strip()
            if role_name:
                SystemSetting.objects.update_or_create(
                    key=f'role_name_{role}',
                    defaults={'value': role_name, 'description': f'{role} 角色显示名称'}
                )
        
        messages.success(request, '权限已保存')
        return redirect('core:system_permissions')
    
    # 获取角色自定义名称
    from core.models import SystemSetting
    role_labels = dict(UserRole.LABELS)
    for role in ['manager', 'leader', 'employee']:
        setting = SystemSetting.objects.filter(key=f'role_name_{role}').first()
        if setting and setting.value:
            role_labels[role] = setting.value
    
    node_perms = PermissionService.get_node_permissions()
    system_perms = PermissionService.get_system_permissions()
    roles = ['manager', 'leader', 'employee']
    role_permissions = {role: PermissionService.get_role_permissions_from_db(role) for role in roles}
    
    return render(request, 'core/admin/system_permissions.html', {
        'node_permissions': node_perms,
        'system_permissions': system_perms,
        'role_permissions': role_permissions,
        'role_labels': role_labels,
        'roles': roles,
        'active_section': 'permissions',
    })


@login_required
def taxonomies(request):
    """词汇表列表"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    page_num = request.GET.get('page', 1)
    all_taxonomies = Taxonomy.objects.all()
    
    paginator = Paginator(all_taxonomies, 10)
    page_obj = paginator.get_page(page_num)
    
    return render(request, 'core/structure/taxonomies/index.html', {
        'taxonomies': page_obj.object_list,
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'active_section': 'taxonomies',
    })


@login_required
def taxonomy_create(request):
    """创建词汇表"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        
        Taxonomy.objects.create(
            name=name,
            slug=slug,
            description=description
        )
        messages.success(request, '词汇表创建成功')
        return redirect('core:taxonomies')
    
    return render(request, 'core/structure/taxonomies/edit.html', {
        'taxonomy': None,
        'active_section': 'taxonomies',
    })


@login_required
def taxonomy_view(request, taxonomy_id: int):
    """查看词汇表"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    page_num = request.GET.get('page', 1)
    
    all_items = taxonomy.items.all().order_by('weight', 'name')
    paginator = Paginator(all_items, 10)
    page_obj = paginator.get_page(page_num)
    
    return render(request, 'core/structure/taxonomies/view.html', {
        'taxonomy': taxonomy,
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'active_section': 'taxonomies',
    })


@login_required
def taxonomy_edit(request, taxonomy_id: int):
    """编辑词汇表"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    
    if request.method == 'POST':
        taxonomy.name = request.POST.get('name', '').strip()
        taxonomy.slug = request.POST.get('slug', '').strip()
        taxonomy.description = request.POST.get('description', '').strip()
        taxonomy.save()
        
        messages.success(request, '词汇表更新成功')
        return redirect('core:taxonomies')
    
    return render(request, 'core/structure/taxonomies/edit.html', {
        'taxonomy': taxonomy,
        'active_section': 'taxonomies',
    })


@login_required
def taxonomy_delete(request, taxonomy_id: int):
    """删除词汇表"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    taxonomy.delete()
    messages.success(request, '词汇表已删除')
    return redirect('core:taxonomies')


@login_required
def taxonomy_item_create(request, taxonomy_id: int):
    """创建词汇项"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            from core.services.taxonomy_service import TaxonomyService
            TaxonomyService.create_item(taxonomy_id, name, description)
            messages.success(request, '词汇项创建成功')
        
        return redirect('core:taxonomy_view', taxonomy_id)
    
    return redirect('core:taxonomy_view', taxonomy_id)


@login_required
def taxonomy_item_update(request, taxonomy_id: int, item_id: int):
    """更新词汇项"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            from core.services.taxonomy_service import TaxonomyService
            TaxonomyService.update_item(item_id, name=name, description=description)
            messages.success(request, '词汇项更新成功')
        
        return redirect('core:taxonomy_view', taxonomy_id)
    
    return redirect('core:taxonomy_view', taxonomy_id)


@login_required
def taxonomy_item_delete(request, taxonomy_id: int, item_id: int):
    """删除词汇项"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    from core.services.taxonomy_service import TaxonomyService
    TaxonomyService.delete_item(item_id)
    messages.success(request, '词汇项已删除')
    return redirect('core:taxonomy_view', taxonomy_id)


@login_required
def profile_view(request):
    """个人中心 - 查看个人信息"""
    role_labels = {
        'manager': '一类用户',
        'leader': '二类用户',
        'employee': '三类用户',
    }
    
    return render(request, 'core/usermenu/profile.html', {
        'role_labels': role_labels,
    })


@login_required
def profile_settings(request):
    """用户设置页面：个人信息 + 偏好设置 + 修改密码"""
    profile_form = ProfileForm(request.POST or None, user_id=request.user.id)
    pref_form = PreferencesForm(request.POST or None)
    pwd_form = ChangePasswordForm(request.POST or None, user=request.user)
    
    if request.method == 'POST':
        if 'submit_profile' in request.POST and profile_form.is_valid():
            try:
                UserService.update_profile(
                    user_id=request.user.id,
                    nickname=profile_form.cleaned_data.get('nickname'),
                    email=profile_form.cleaned_data.get('email')
                )
                messages.success(request, '个人信息已更新成功')
            except ValueError as e:
                messages.error(request, str(e))
        
        elif 'submit_preferences' in request.POST and pref_form.is_valid():
            try:
                UserService.update_preferences(
                    user_id=request.user.id,
                    theme=pref_form.cleaned_data.get('theme'),
                    notifications_enabled=pref_form.cleaned_data.get('notifications_enabled'),
                    preferred_language=pref_form.cleaned_data.get('preferred_language')
                )
                messages.success(request, '偏好设置已保存')
            except ValueError as e:
                messages.error(request, str(e))
        
        elif 'submit_password' in request.POST and pwd_form.is_valid():
            try:
                new_password = pwd_form.cleaned_data.get('new_password')
                UserService.change_password(request.user.id, new_password)
                messages.success(request, '密码修改成功，请使用新密码重新登录')
                logout(request)
                return redirect('core:login')
            except ValueError as e:
                messages.error(request, str(e))
        
        return redirect('core:profile_settings')
    
    profile_form = ProfileForm(user_id=request.user.id, initial={
        'nickname': request.user.nickname,
        'email': request.user.email,
    })
    pref_form = PreferencesForm(initial={
        'theme': request.user.theme,
        'notifications_enabled': request.user.notifications_enabled,
        'preferred_language': request.user.preferred_language,
    })
    pwd_form = ChangePasswordForm(user=request.user)
    
    return render(request, 'core/usermenu/settings.html', {
        'profile_form': profile_form,
        'pref_form': pref_form,
        'pwd_form': pwd_form,
    })


@login_required
def api_time_current(request):
    """获取当前时间 API"""
    status = TimeService.get_sync_status()
    synced = status.get('status') == 'success'
    
    return JsonResponse({
        'time': TimeService.get_current_time(),
        'timezone': TimeService.get_timezone(),
        'synced': synced,
    })


@login_required
def api_time_test(request):
    """测试时间服务器连接"""
    from core.services import get_time_sync_service
    time_sync = get_time_sync_service()
    server_url = time_sync.get_server_url()
    server_time = time_sync._fetch_time_from_server(server_url)
    
    return JsonResponse({
        'success': server_time is not None,
        'server': server_url,
        'time': server_time.strftime('%Y-%m-%d %H:%M:%S') if server_time else None,
    })


@login_required
def api_time_status(request):
    """获取时间同步状态"""
    return JsonResponse(TimeService.get_sync_status())


@login_required
def cron_manager(request):
    """Cron 调度管理页面"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    cron = get_cron_service()
    
    # 确保 cron 服务正在运行
    status = cron.get_status()
    if not status['running']:
        cron.start()
        status = cron.get_status()
    
    task_descriptions = {
        'time_sync': '时间同步任务 - 定时与远程时间服务器同步',
        'cache_cleanup': '缓存清理任务 - 清理过期的系统缓存',
    }
    
    for task in status['tasks'].values():
        task['description'] = task_descriptions.get(task['name'], '未知任务')
    
    return render(request, 'core/admin/system_cron_manager.html', {
        'cron_status': status,
        'active_section': 'cron',
    })


@login_required
def cron_status(request):
    """获取 Cron 状态 API"""
    cron = get_cron_service()
    return JsonResponse(cron.get_status())


@login_required
def cron_run_task(request, task_name: str):
    """手动触发任务"""
    if not PermissionService.can_access_admin(request.user):
        return JsonResponse({'success': False, 'error': '权限不足'}, status=403)
    
    cron = get_cron_service()
    result = cron.trigger(task_name)
    return JsonResponse(result)


@login_required
def cron_toggle_task(request, task_name: str):
    """切换任务启用状态"""
    if not PermissionService.can_access_admin(request.user):
        return JsonResponse({'success': False, 'error': '权限不足'}, status=403)
    
    import json
    data = json.loads(request.body) if request.body else {}
    enabled = data.get('enabled', True)
    
    cron = get_cron_service()
    result = cron.toggle(task_name, enabled)
    return JsonResponse(result)


@login_required
def permission_check(request):
    """权限检测页面 - 检测哪些页面需要 admin 权限"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    filter_status = request.GET.get('filter', 'all')
    try:
        page_num = int(request.GET.get('page', 1))
        if page_num < 1:
            page_num = 1
    except (ValueError, TypeError):
        page_num = 1
    
    all_pages = get_all_pages_with_permission_status()
    
    if filter_status == 'restricted':
        pages = [p for p in all_pages if p['has_admin_check']]
    elif filter_status == 'unrestricted':
        pages = [p for p in all_pages if not p['has_admin_check']]
    else:
        pages = all_pages
    
    paginator = Paginator(pages, 20)
    page_obj = paginator.get_page(page_num)
    
    restricted_count = len([p for p in all_pages if p['has_admin_check']])
    unrestricted_count = len([p for p in all_pages if not p['has_admin_check']])
    
    return render(request, 'core/admin/permission_check.html', {
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'filter_status': filter_status,
        'total_count': len(all_pages),
        'restricted_count': restricted_count,
        'unrestricted_count': unrestricted_count,
    })


def get_all_pages_with_permission_status():
    """获取所有页面的权限状态"""
    from django.urls import get_resolver
    import inspect
    
    pages = []
    visited_views = set()
    
    def extract_patterns(patterns):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                extract_patterns(pattern.url_patterns)
            elif hasattr(pattern, 'callback') and pattern.callback:
                view_func = pattern.callback
                view_name = getattr(view_func, '__name__', pattern.name or 'unknown')
                url_pattern = str(pattern.pattern)
                url_pattern = url_pattern.lstrip('^').rstrip('$')
                
                if not url_pattern or url_pattern == '/':
                    continue
                
                admin_views = ['changelist_view', 'add_view', 'change_view', 
                               'delete_view', 'history_view', 'app_index', 'autocomplete_view',
                               'i18n_javascript', 'password_change', 'password_change_done',
                               'user_change_password', 'catch_all_view', 'view', 'shortcut',
                               'login', 'logout', 'index', 'jsi18n']
                if view_name in admin_views and not pattern.name:
                    continue
                
                # 排除无意义的正则参数URL，保留节点页面
                if '<' in url_pattern and not pattern.name:
                    if 'node_type_slug' not in url_pattern and 'node_id' not in url_pattern:
                        continue
                
                # 排除特定无意义URL
                skip_patterns = ['app_label', 'path:object_id', 'path:content_type_id']
                if any(p in url_pattern for p in skip_patterns):
                    continue
                
                if view_name in visited_views:
                    continue
                visited_views.add(view_name)
                
                has_admin_check = check_view_has_admin_permission(view_func)
                page_name = pattern.name or view_name
                
                pages.append({
                    'name': page_name,
                    'url': url_pattern,
                    'view': view_name,
                    'has_admin_check': has_admin_check,
                    'app': detect_app_from_url(url_pattern),
                })
    
    root_resolver = get_resolver()
    extract_patterns(root_resolver.url_patterns)
    return sorted(pages, key=lambda x: x['url'])


def check_view_has_admin_permission(view_func):
    """检测视图函数是否有 admin 权限检查"""
    import inspect
    try:
        source = inspect.getsource(view_func)
        return 'can_access_admin' in source
    except Exception:
        return False


def detect_app_from_url(url_str):
    """从 URL 检测所属应用"""
    url = url_str.lstrip('/')
    if url.startswith('system/'):
        return 'system'
    elif url.startswith('nodes/') or url.startswith('types/') or url.startswith('type/') or url.startswith('field-types'):
        return 'nodes'
    elif url.startswith('taxonomies') or url.startswith('taxonomy'):
        return 'core'
    elif url.startswith('accounts/'):
        return 'auth'
    elif url.startswith('profile/'):
        return 'profile'
    elif url.startswith('api/'):
        return 'api'
    # 节点页面
    elif 'node_type_slug' in url_str or 'node_id' in url_str:
        return 'nodes'
    return 'other'


def error_400(request, exception):
    """400 - 错误请求"""
    return render(request, 'core/errors/400.html', {
        'exception': exception,
    }, status=400)


def error_403(request, exception):
    """403 - 无权限"""
    return render(request, 'core/errors/403.html', {
        'exception': exception,
    }, status=403)


def error_404(request, exception):
    """404 - 页面未找到"""
    return render(request, 'core/errors/404.html', {
        'exception': exception,
    }, status=404)


def error_500(request):
    """500 - 服务器错误"""
    return render(request, 'core/errors/500.html', {
        'exception': None,
    }, status=500)


# ===== 中国行政区划 API =====

from django.views.decorators.http import require_GET, require_POST
from core.services import ChinaRegionService


@login_required
@require_GET
def api_regions_provinces(request):
    """获取所有省份"""
    provinces = ChinaRegionService.get_provinces()
    return JsonResponse({
        'success': True,
        'data': [{'code': p.code, 'name': p.name} for p in provinces]
    })


@login_required
@require_GET
def api_regions_cities(request):
    """获取某省份的城市"""
    province_code = request.GET.get('province')
    if not province_code:
        return JsonResponse({'success': False, 'error': '缺少province参数'}, status=400)
    
    cities = ChinaRegionService.get_cities(province_code)
    return JsonResponse({
        'success': True,
        'data': [{'code': c.code, 'name': c.name} for c in cities]
    })


@login_required
@require_GET
def api_regions_districts(request):
    """获取某城市的区县"""
    city_code = request.GET.get('city')
    if not city_code:
        return JsonResponse({'success': False, 'error': '缺少city参数'}, status=400)
    
    districts = ChinaRegionService.get_districts(city_code)
    return JsonResponse({
        'success': True,
        'data': [{'code': d.code, 'name': d.name} for d in districts]
    })


@login_required
@require_GET
def api_regions_search(request):
    """搜索行政区划"""
    keyword = request.GET.get('q', '')
    if not keyword:
        return JsonResponse({'success': False, 'error': '缺少q参数'}, status=400)
    
    results = ChinaRegionService.search(keyword)
    return JsonResponse({
        'success': True,
        'data': [
            {
                'code': r.code,
                'name': r.name,
                'level': r.level,
                'full_path': r.full_path
            }
            for r in results
        ]
    })


@require_GET
def api_regions_path(request):
    """获取完整路径"""
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'success': False, 'error': '缺少code参数'}, status=400)
    
    path = ChinaRegionService.get_full_path(code)
    return JsonResponse({
        'success': True,
        'data': {'code': code, 'path': path}
    })


@login_required
@require_GET
def api_regions_stats(request):
    """获取统计信息"""
    stats = ChinaRegionService.get_stats()
    return JsonResponse({
        'success': True,
        'data': stats
    })


# ===== 内容结构 Dashboard =====

@login_required
def structure_dashboard(request):
    """内容结构首页"""
    if not request.user.is_admin:
        return redirect('core:dashboard')
    return render(request, 'core/structure/structure_dashboard.html', {
        'active_section': 'dashboard',
    })


@login_required
def importexport_dashboard(request):
    """数据导入导出首页"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')
    return render(request, 'core/importexport/importexport_dashboard.html', {
        'active_section': 'dashboard',
    })


# ===== 功能卡片区域 API =====

@login_required
@require_GET
def api_dashboard_cards(request):
    """获取功能卡片布局"""
    from core.models import SystemSetting
    import json

    setting = SystemSetting.objects.filter(key='user_dashboard_card_positions').first()
    positions = {}
    if setting and setting.value:
        try:
            positions = json.loads(setting.value)
        except Exception:
            positions = {}

    default_positions = {str(i): {'module': None, 'size': 'medium', 'config': {}} for i in range(1, 7)}
    for k, v in positions.items():
        default_positions[k] = v

    available_modules = []
    module_stats = {}
    try:
        from core.node.models import NodeModule
        from importlib import import_module

        active_modules = NodeModule.objects.filter(is_active=True)
        for node_module in active_modules:
            module_path = node_module.path
            if module_path:
                try:
                    mod = import_module(f'modules.{module_path}.module')
                    if hasattr(mod, 'MODULE_INFO'):
                        mod_info = mod.MODULE_INFO
                        if 'dashboard_cards' in mod_info or True:
                            available_modules.append(node_module.module_id)
                        
                        if node_module.module_id in ['customer', 'customer_cn']:
                            service_map = {
                                'customer': 'CustomerService',
                                'customer_cn': 'CustomerCnService'
                            }
                            service_name = service_map.get(node_module.module_id)
                            if service_name:
                                stats_mod = import_module(f'modules.{module_path}.services')
                                if hasattr(stats_mod, service_name):
                                    service_class = getattr(stats_mod, service_name)
                                    if hasattr(service_class, 'get_count'):
                                        module_stats[node_module.module_id] = {
                                            'total': service_class.get_count(),
                                            'recent': getattr(service_class, 'get_recent_count', lambda d=7: 0)(7)
                                        }
                except Exception:
                    pass
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'data': {
            'positions': default_positions,
            'available_modules': available_modules,
            'module_stats': module_stats,
        }
    })


@login_required
@require_POST
def api_dashboard_cards_save(request):
    """保存功能卡片布局"""
    from core.models import SystemSetting
    import json

    try:
        data = json.loads(request.body)
        positions = data.get('positions', {})

        SystemSetting.objects.update_or_create(
            key='user_dashboard_card_positions',
            defaults={'value': json.dumps(positions), 'description': '用户首页功能卡片布局'}
        )

        return JsonResponse({'success': True, 'message': '布局已保存'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
