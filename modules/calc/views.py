# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.node.models import Module, ToolType


@login_required
def tool_view(request):
    """计算器工具页面"""
    tool_type_ids = Module.objects.filter(
        module_type='tool',
        is_active=True
    ).values_list('module_id', flat=True)
    tools = ToolType.objects.filter(slug__in=tool_type_ids, is_active=True)
    
    return render(request, 'calc/calc.html', {
        'tools': tools,
    })


@login_required
def calculate(request):
    """计算表达式AJAX接口"""
    import json
    from django.http import JsonResponse
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            
            result = eval(expression, {"__builtins__": {}}, {})
            
            return JsonResponse({'result': result})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)