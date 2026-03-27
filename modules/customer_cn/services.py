# -*- coding: utf-8 -*-
"""
================================================================================
文件：services.py
路径：/home/edo/cimf-v2/modules/customer_cn/services.py
================================================================================

功能说明：
    国内客户管理服务，提供国内客户的 CRUD 操作

版本：
    - 1.0: 初始版本
    - 1.1: 移动到 modules/customer_cn/ 目录

依赖：
    - modules.models.CustomerCnFields: 国内客户字段模型
    - core.node.services: NodeService
"""

from typing import List, Optional, Dict, Any
import random
import string
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import CustomerCnFields
from core.node.services import NodeService

User = get_user_model()


class CustomerCnService:
    """国内客户管理服务"""
    
    @staticmethod
    def get_list(search: Optional[str] = None, enterprise_type_id: Optional[int] = None, 
                 customer_level_id: Optional[int] = None) -> List[CustomerCnFields]:
        """获取国内客户列表"""
        queryset = CustomerCnFields.objects.select_related(
            'customer_type', 'customer_level', 'enterprise_type'
        ).all()
        
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(enterprise_name__icontains=search)
            )
        
        if enterprise_type_id:
            queryset = queryset.filter(enterprise_type_id=enterprise_type_id)
        
        if customer_level_id:
            queryset = queryset.filter(customer_level_id=customer_level_id)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(customer_id: int) -> Optional[CustomerCnFields]:
        """根据 ID 获取国内客户"""
        return CustomerCnFields.objects.filter(id=customer_id).first()
    
    @staticmethod
    def get_by_node_id(node_id: int) -> Optional[CustomerCnFields]:
        """根据节点 ID 获取国内客户"""
        return CustomerCnFields.objects.filter(node_id=node_id).first()
    
    @staticmethod
    def create(user, data: Dict[str, Any]) -> CustomerCnFields:
        """创建国内客户"""
        node = NodeService.create('customer_cn', user, {})
        
        customer_code = data.get('customer_code')
        if not customer_code:
            customer_code = 'CCN' + ''.join(random.choices(string.digits, k=6))
        
        customer = CustomerCnFields.objects.create(
            node=node,
            customer_name=data.get('customer_name', ''),
            customer_code=customer_code,
            customer_type_id=data.get('customer_type_id'),
            enterprise_name=data.get('enterprise_name'),
            phone1=data.get('phone1'),
            email1=data.get('email1'),
            phone2=data.get('phone2'),
            email2=data.get('email2'),
            region=data.get('region'),
            address=data.get('address'),
            postal_code=data.get('postal_code'),
            wechat=data.get('wechat'),
            dingtalk=data.get('dingtalk'),
            industry=data.get('industry'),
            enterprise_type_id=data.get('enterprise_type_id'),
            registered_capital=data.get('registered_capital'),
            customer_level_id=data.get('customer_level_id'),
            credit_limit=data.get('credit_limit'),
            website=data.get('website'),
            notes=data.get('notes'),
        )
        
        return customer
    
    @staticmethod
    def update(customer_id: int, user, data: Dict[str, Any]) -> Optional[CustomerCnFields]:
        """更新国内客户"""
        customer = CustomerCnFields.objects.filter(id=customer_id).first()
        if not customer:
            return None
        
        NodeService.update(customer.node_id, user, {})
        
        for key, value in data.items():
            if hasattr(customer, key) and key != 'id' and key != 'node':
                setattr(customer, key, value)
        
        customer.save()
        
        return customer
    
    @staticmethod
    def delete(customer_id: int) -> bool:
        """删除国内客户"""
        customer = CustomerCnFields.objects.filter(id=customer_id).first()
        if customer:
            node_id = customer.node_id
            customer.delete()
            NodeService.delete(node_id)
            return True
        return False
    
    @staticmethod
    def get_exportable_fields() -> List[Dict]:
        """获取可导出的字段列表"""
        return [
            {'name': 'customer_name', 'label': '客户名称', 'type': 'string', 'required': True},
            {'name': 'customer_code', 'label': '客户代码', 'type': 'string', 'required': True},
            {'name': 'customer_type', 'label': '客户类型', 'type': 'fk'},
            {'name': 'enterprise_name', 'label': '企业名称', 'type': 'string'},
            {'name': 'phone1', 'label': '电话1', 'type': 'telephone'},
            {'name': 'email1', 'label': '邮箱1', 'type': 'email'},
            {'name': 'phone2', 'label': '电话2', 'type': 'telephone'},
            {'name': 'email2', 'label': '邮箱2', 'type': 'email'},
            {'name': 'wechat', 'label': '微信', 'type': 'string'},
            {'name': 'dingtalk', 'label': '钉钉', 'type': 'string'},
            {'name': 'address', 'label': '详细地址', 'type': 'string'},
            {'name': 'postal_code', 'label': '邮政编码', 'type': 'string'},
            {'name': 'region', 'label': '省市区', 'type': 'region'},
            {'name': 'industry', 'label': '行业', 'type': 'string'},
            {'name': 'enterprise_type', 'label': '企业类型', 'type': 'fk'},
            {'name': 'registered_capital', 'label': '注册资本', 'type': 'decimal'},
            {'name': 'customer_level', 'label': '客户等级', 'type': 'fk'},
            {'name': 'credit_limit', 'label': '信用额度', 'type': 'decimal'},
            {'name': 'website', 'label': '网站', 'type': 'string'},
            {'name': 'notes', 'label': '备注', 'type': 'string'},
        ]
    
    @staticmethod
    def get_count() -> int:
        """获取客户总数"""
        return CustomerCnFields.objects.count()
    
    @staticmethod
    def get_region_display(region: dict) -> str:
        """获取省市区显示文本"""
        if not region:
            return ''
        
        parts = []
        if region.get('province'):
            parts.append(region.get('province', ''))
        if region.get('city'):
            parts.append(region.get('city', ''))
        if region.get('district'):
            parts.append(region.get('district', ''))
        
        return ' '.join(parts)