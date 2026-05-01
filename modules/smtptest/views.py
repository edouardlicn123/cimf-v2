# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def list_view(request):
    return JsonResponse({'message': 'List view for smtptest'})


@login_required
@require_http_methods(["GET"])
def detail_view(request, pk):
    return JsonResponse({'message': f'Detail view for {pk}'})
