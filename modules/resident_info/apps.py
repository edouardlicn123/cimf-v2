# -*- coding: utf-8 -*-
from django.apps import AppConfig


class ResidentInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.resident_info'
    label = 'resident_info'
    verbose_name = '居民信息'