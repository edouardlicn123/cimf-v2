# -*- coding: utf-8 -*-
"""
模型注册表

将 node_type_slug 映射到对应的 Django 模型类
"""

from typing import Dict, Type, Optional


class ModelRegistry:
    """模型注册表"""
    
    _registry: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, slug: str, model_class: Type):
        """注册模型"""
        cls._registry[slug] = model_class
    
    @classmethod
    def get_model(cls, slug: str):
        """获取模型类"""
        if slug in cls._registry and cls._registry[slug] is not None:
            return cls._registry[slug]
        
        if slug == 'customer':
            from nodes.customer.models import CustomerFields
            cls._registry[slug] = CustomerFields
            return CustomerFields
        elif slug == 'customer_cn':
            from nodes.customer_cn.models import CustomerCnFields
            cls._registry[slug] = CustomerCnFields
            return CustomerCnFields
        
        return None
    
    @classmethod
    def get_all_slugs(cls):
        """获取所有已注册的 slug"""
        return list(cls._registry.keys())
