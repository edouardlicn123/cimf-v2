# -*- coding: utf-8 -*-
"""
用户管理视图模块
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.decorators import admin_required
from core.models import User
from core.services import UserService


@admin_required
def system_users(request):
    """系统用户列表"""
    search_term = request.GET.get('search', '')
    only_active = request.GET.get('only_active', 'true') == 'true'
    role_filter = request.GET.get('role_filter', '')
    
    users = UserService.get_user_list(
        search_term=search_term if search_term else None,
        only_active=only_active,
        exclude_admin=True,
        role=role_filter if role_filter else None
    )
    
    return render(request, 'admin/system_users.html', {
        'users': users,
        'search_term': search_term,
        'only_active': only_active,
        'role_filter': role_filter,
        'active_section': 'users',
    })


@admin_required
def user_create(request):
    """创建用户"""
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
    
    return render(request, 'admin/system_user_edit.html', {
        'user': None,
        'is_create': True,
    })


@admin_required
def user_edit(request, user_id: int):
    """编辑用户"""
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
    
    return render(request, 'admin/system_user_edit.html', {
        'user': user,
        'is_create': False,
    })


@admin_required
def user_delete(request, user_id: int):
    """删除用户"""
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