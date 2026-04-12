"""
URL configuration for cimf_django project.
"""
from django.contrib import admin
from django.urls import path, include
from core.importexport.urls import urlpatterns as importexport_urls, urlpatterns_all

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('modules/', include('modules.urls', namespace='modules')),
    path('node/', include('core.node.urls', namespace='node')),
    path('market/', include('core.marketplace.urls', namespace='market')),
    path('export/', include((urlpatterns_all, 'importexport'))),
    path('api/v1/', include('core.api_urls', namespace='api')),
]
