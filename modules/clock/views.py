# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .services import ClockService


@login_required
@require_http_methods(["GET"])
def api_time(request):
    """获取当前时间 API"""
    return JsonResponse({
        'success': True,
        'data': ClockService.get_current_time(),
    })
