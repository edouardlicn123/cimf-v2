# -*- coding: utf-8 -*-
"""
外键解析器

解析外键字段的值，查找对应的 TaxonomyItem 等
"""

from typing import Optional, Any


class FKResolverPool:
    """外键解析器池"""
    
    _resolvers = {}
    
    @classmethod
    def register(cls, model_name: str, resolver):
        """注册解析器"""
        cls._resolvers[model_name] = resolver
    
    @classmethod
    def resolve(cls, fk_model, value: str, taxonomy_slug: Optional[str] = None) -> Any:
        """解析外键值"""
        if not value:
            return None
        
        model_name = fk_model._meta.model_name
        
        if model_name in cls._resolvers:
            return cls._resolvers[model_name].resolve(value, taxonomy_slug)
        
        return cls._default_resolve(fk_model, value, taxonomy_slug)
    
    @staticmethod
    def _default_resolve(fk_model, value: str, taxonomy_slug: Optional[str] = None) -> Any:
        """默认解析逻辑"""
        from core.models import TaxonomyItem
        
        model_name = fk_model._meta.model_name
        
        if model_name == 'taxonomyitem':
            if taxonomy_slug:
                item = TaxonomyItem.objects.filter(
                    taxonomy__slug=taxonomy_slug,
                    name=value
                ).first()
            else:
                item = TaxonomyItem.objects.filter(name=value).first()
            return item
        
        try:
            if hasattr(fk_model, 'name'):
                return fk_model.objects.filter(name=value).first()
            elif hasattr(fk_model, 'customer_name'):
                return fk_model.objects.filter(customer_name=value).first()
        except Exception:
            pass
        
        return None
