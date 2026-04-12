# -*- coding: utf-8 -*-
"""
模块市场视图
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import MarketService


@login_required
def market_index(request):
    """市场首页"""
    modules = MarketService.get_modules()
    
    for module in modules:
        module_id = module.get('id', '')
        status = MarketService.get_module_status(module_id)
        module['installed'] = status['installed']
        module['installed_version'] = status['installed_version']
        module['market_version'] = status['market_version']
        module['has_update'] = status['has_update']
    
    return render(request, 'marketplace/index.html', {
        'modules': modules,
        'active_section': 'market',
    })


@csrf_exempt
@login_required
def market_install(request, module_id: str):
    """下载安装模块"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'})
    
    result = MarketService.download_and_extract(module_id)
    return JsonResponse(result)
