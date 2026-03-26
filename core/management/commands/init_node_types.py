# -*- coding: utf-8 -*-
"""
初始化节点类型数据
用法: ./venv/bin/python manage.py init_node_types
"""

from django.core.management.base import BaseCommand

from core.node.models import NodeType


class Command(BaseCommand):
    help = '初始化节点类型数据'

    def handle(self, *args, **options):
        node_types = [
            {
                'name': '海外客户',
                'slug': 'customer',
                'icon': 'bi-people',
                'description': '海外客户信息管理',
            },
            {
                'name': '客户信息（国内）',
                'slug': 'customer_cn',
                'icon': 'bi-people',
                'description': '国内客户信息管理',
            },
        ]

        count = 0
        for data in node_types:
            if NodeType.objects.filter(slug=data['slug']).exists():
                self.stdout.write(f"跳过已存在: {data['name']}")
                continue

            NodeType.objects.create(
                name=data['name'],
                slug=data['slug'],
                icon=data['icon'],
                description=data.get('description', ''),
                is_active=True,
            )
            count += 1
            self.stdout.write(f"创建: {data['name']}")

        self.stdout.write(self.style.SUCCESS(f"完成! 新增 {count} 个节点类型"))
