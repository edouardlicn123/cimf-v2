# -*- coding: utf-8 -*-
"""
海外客户样本数据初始化命令
用法: ./venv/bin/python manage.py init_overseas_customers
"""

from django.core.management.base import BaseCommand

from core.node.models import Node, NodeType
from modules.customer.models import CustomerFields
from core.models import User
from modules.customer.sample_data import OVERSEAS_CUSTOMERS


class Command(BaseCommand):
    help = '初始化海外客户样本数据'

    def handle(self, *args, **options):
        admin_user = User.objects.filter(is_admin=True).first()
        if not admin_user:
            self.stderr.write(self.style.ERROR('未找到管理员用户，请先创建用户'))
            return

        customer_node_type = NodeType.objects.filter(slug='customer').first()
        if not customer_node_type:
            self.stderr.write(self.style.ERROR('未找到客户节点类型 (customer)，请先运行 init_node_types'))
            return

        count = 0
        for data in OVERSEAS_CUSTOMERS:
            if CustomerFields.objects.filter(customer_name=data['customer_name']).exists():
                self.stdout.write(f"跳过已存在: {data['customer_name']}")
                continue

            node = Node.objects.create(
                node_type=customer_node_type,
                created_by=admin_user,
                updated_by=admin_user,
            )

            fields_data = {k: v for k, v in data.items() 
                          if k not in ('customer_name',)}
            CustomerFields.objects.create(
                node=node,
                customer_name=data['customer_name'],
                **fields_data,
            )
            count += 1
            self.stdout.write(f"创建: {data['customer_name']}")

        self.stdout.write(self.style.SUCCESS(f"完成! 新增 {count} 条海外客户"))
