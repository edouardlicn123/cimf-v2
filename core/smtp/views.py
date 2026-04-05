# -*- coding: utf-8 -*-
"""
SMTP 邮件模块视图
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from core.services import PermissionService
from core.smtp.services import SmtpService, EmailService
from core.smtp.forms import SmtpConfigForm
from core.smtp.models import EmailLog


@login_required
@require_http_methods(['GET', 'POST'])
def smtp_config(request):
    """SMTP 配置页面"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限')
        return redirect('core:dashboard')
    
    config = SmtpService.get_current_config()
    presets = SmtpService.get_provider_presets()
    
    if request.method == 'POST':
        form = SmtpConfigForm(request.POST)
        if form.is_valid():
            config_data = form.cleaned_data
            
            if not config_data.get('password'):
                config_data['password'] = config.get('password', '')
            
            SmtpService.save_config(config_data)
            messages.success(request, 'SMTP 配置已保存')
            return redirect('core:smtp_config')
    else:
        initial = {
            'provider': config.get('provider', 'gmail_tls'),
            'host': config.get('host', ''),
            'port': config.get('port', 587),
            'use_ssl': config.get('use_ssl', False),
            'use_tls': config.get('use_tls', True),
            'username': config.get('username', ''),
            'password': '',
            'from_email': config.get('from_email', ''),
            'from_name': config.get('from_name', '仙芙CIMF'),
            'timeout': config.get('timeout', 30),
            'skip_verify': config.get('skip_verify', False),
            'enabled': config.get('enabled', False),
            'batch_size': config.get('batch_size', 10),
            'rate_limit': config.get('rate_limit', 0),
            'log_days': config.get('log_days', 30),
            'failed_notify': config.get('failed_notify', False),
            'notify_email': config.get('notify_email', ''),
            'system_url': config.get('system_url', ''),
        }
        form = SmtpConfigForm(initial=initial)
    
    recent_logs = EmailLog.objects.all()[:10]
    
    return render(request, 'core/smtp/config.html', {
        'form': form,
        'config': config,
        'presets': presets,
        'active_section': 'smtp',
        'recent_logs': recent_logs,
    })


@login_required
@require_http_methods(['POST'])
def smtp_test(request):
    """测试 SMTP 连接"""
    if not PermissionService.can_access_admin(request.user):
        return JsonResponse({'success': False, 'error': '需要管理员权限'}, status=403)
    
    config = SmtpService.get_current_config()
    success, message = SmtpService.test_connection(config)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('core:smtp_config')


@login_required
def smtp_presets(request):
    """获取服务商预设（AJAX）"""
    if not request.user.is_admin:
        return JsonResponse({'error': '需要管理员权限'}, status=403)
    
    provider = request.GET.get('provider', 'gmail_tls')
    preset = SmtpService.get_provider_presets(provider)
    
    return JsonResponse({
        'success': True,
        'preset': preset,
    })


@login_required
def smtp_history(request):
    """发送历史页面"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限')
        return redirect('core:dashboard')
    
    logs = EmailService.get_send_history(limit=100)
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        logs = [log for log in logs if log.status == status_filter]
    
    return render(request, 'core/smtp/history.html', {
        'logs': logs,
        'status_filter': status_filter,
        'active_section': 'smtp',
    })


@login_required
@require_http_methods(['POST'])
def smtp_cleanup_logs(request):
    """手动清理邮件日志"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限')
        return redirect('core:smtp_config')
    
    deleted_count = EmailService.cleanup_old_logs()
    messages.success(request, f'已清理 {deleted_count} 条过期日志')
    
    return redirect('core:smtp_config')
