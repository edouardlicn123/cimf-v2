# -*- coding: utf-8 -*-
"""
卡片 API 模块
"""

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator

from core.models import SystemSetting
from core.services import UserService
from core.node.models import Module


@login_required
@require_GET
def api_dashboard_cards(request):
    """获取功能卡片布局"""
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
    module_templates = {}
    rendered_cards = {}
    try:
        from importlib import import_module
        from django.template import engines

        jinja2_engine = engines['jinja2']

        active_modules = Module.objects.filter(is_active=True)
        for node_module in active_modules:
            module_path = node_module.path
            if module_path:
                try:
                    mod = import_module(f'modules.{module_path}.module')
                    if hasattr(mod, 'MODULE_INFO'):
                        mod_info = mod.MODULE_INFO
                        if 'dashboard_cards' in mod_info:
                            available_modules.append(node_module.module_id)
                        
                        # 检测 dashboard_cards 配置，提取模板路径
                        if 'dashboard_cards' in mod_info:
                            cards = mod_info['dashboard_cards']
                            if cards and isinstance(cards, list):
                                for card in cards:
                                    if 'template' in card:
                                        template_path = card['template']
                                        module_templates[node_module.module_id] = template_path
                                        
                                        # 预渲染模块卡片模板
                                        try:
                                            full_template_path = template_path
                                            template = jinja2_engine.get_template(full_template_path)
                                            stats = module_stats.get(node_module.module_id, {})
                                            rendered_cards[node_module.module_id] = template.render({
                                                'module_id': node_module.module_id,
                                                'stats': stats,
                                            })
                                        except Exception:
                                            pass
                                        break
                        
                        if mod_info.get('dashboard_stats', False):
                            service_mod = import_module(f'modules.{module_path}.services')
                            for attr_name in dir(service_mod):
                                attr = getattr(service_mod, attr_name)
                                if (attr_name.endswith('Service') and 
                                    hasattr(attr, 'get_count')):
                                    module_stats[node_module.module_id] = {
                                        'total': attr.get_count(),
                                        'recent': getattr(attr, 'get_recent_count', lambda d=7: 0)(7)
                                    }
                                    break
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
            'module_templates': module_templates,
            'rendered_cards': rendered_cards,
        }
    })


@login_required
@require_POST
def api_dashboard_cards_save(request):
    """保存功能卡片布局"""
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


@login_required
@require_GET
def api_nav_cards(request):
    """获取用户导航卡片"""
    try:
        cards = UserService.get_navigation_cards(request.user.id)
        return JsonResponse({
            'success': True,
            'cards': cards,
            'max': 12
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def api_nav_cards_save(request):
    """保存用户导航卡片"""
    try:
        data = json.loads(request.body)
        cards = data.get('cards', [])
        
        if len(cards) > 12:
            return JsonResponse({
                'success': False,
                'error': '最多只能添加12个导航卡片'
            }, status=400)
        
        UserService.save_navigation_cards(request.user.id, cards)
        return JsonResponse({'success': True, 'message': '导航卡片已保存'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def navigation_settings(request):
    """导航卡片设置页面"""
    cards = UserService.get_navigation_cards(request.user.id)
    
    return render(request, 'nav_cards/settings.html', {
        'active_section': 'nav_cards',
        'cards': cards,
        'max_cards': 12,
    })