# -*- coding: utf-8 -*-
"""
海外客户样本数据初始化命令
用法: ./venv/bin/python manage.py init_overseas_customers
"""

from importlib import import_module

from django.core.management.base import BaseCommand

from core.node.models import Node, NodeType
from core.models import User


class Command(BaseCommand):
    help = '初始化海外客户样本数据'

    def handle(self, *args, **options):
        # 动态导入模块
        try:
            customer_module = import_module('modules.customer.module')
            customer_models = import_module('modules.customer.models')
            customer_sample_data = import_module('modules.customer.sample_data')
        except (ImportError, ModuleNotFoundError) as e:
            self.stderr.write(self.style.ERROR(f'模块导入失败: {e}'))
            return
        
        # 获取模型和样本数据
        CustomerFields = getattr(customer_models, 'CustomerFields', None)
        OVERSEAS_CUSTOMERS = getattr(customer_sample_data, 'OVERSEAS_CUSTOMERS', None)
        
        if not CustomerFields:
            self.stderr.write(self.style.ERROR('未找到 CustomerFields 模型'))
            return
        
        if not OVERSEAS_CUSTOMERS:
            self.stderr.write(self.style.ERROR('未找到 OVERSEAS_CUSTOMERS 样本数据'))
            return
        
        # 获取管理员用户
        admin_user = User.objects.filter(is_admin=True).first()
        if not admin_user:
            self.stderr.write(self.style.ERROR('未找到管理员用户，请先创建用户'))
            return
        
        # 获取节点类型
        module_info = getattr(customer_module, 'MODULE_INFO', {})
        module_id = module_info.get('id', 'customer')
        
        customer_node_type = NodeType.objects.filter(slug=module_id).first()
        if not customer_node_type:
            self.stderr.write(self.style.ERROR(f'未找到节点类型 ({module_id})，请先运行 init_node_types'))
            return
        
        # 创建样本数据
        count = 0
        for data in OVERSEAS_CUSTOMERS:
            customer_name = data.get('customer_name')
            if not customer_name:
                continue
            
            if CustomerFields.objects.filter(customer_name=customer_name).exists():
                self.stdout.write(f"跳过已存在: {customer_name}")
                continue
            
            node = Node.objects.create(
                node_type=customer_node_type,
                created_by=admin_user,
                updated_by=admin_user,
            )
            
            fields_data = {k: v for k, v in data.items() if k != 'customer_name'}
            CustomerFields.objects.create(
                node=node,
                customer_name=customer_name,
                **fields_data,
            )
            count += 1
            self.stdout.write(f"创建: {customer_name}")
        
        self.stdout.write(self.style.SUCCESS(f"完成! 新增 {count} 条海外客户"))
