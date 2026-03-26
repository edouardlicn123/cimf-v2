# -*- coding: utf-8 -*-
from django.apps import AppConfig


class CustomerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nodes.customer'
    label = 'customer'
    verbose_name = '海外客户'
