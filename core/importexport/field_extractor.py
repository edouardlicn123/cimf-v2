# -*- coding: utf-8 -*-
"""
字段提取器

从 Django 模型中提取字段信息用于导入导出
"""

from typing import List, Dict, Type
from django.db import models


class FieldDefExtractor:
    """字段定义提取器"""
    
    EXCLUDE_FIELDS = {'id', 'created_at', 'updated_at', 'node'}
    
    FK_FIELD_MAP = {
        'customer_type': 'customer_type',
        'customer_level': 'customer_level',
        'country': 'country',
        'enterprise_type': 'enterprise_type',
    }
    
    @classmethod
    def extract(cls, model_class: Type) -> List[Dict]:
        """提取模型的可导入导出字段"""
        fields = []
        
        for field in model_class._meta.get_fields():
            if hasattr(field, 'attname') and field.name not in cls.EXCLUDE_FIELDS:
                field_info = {
                    'name': field.name,
                    'label': getattr(field, 'verbose_name', field.name),
                    'type': cls._get_field_type(field),
                    'required': not field.blank and not field.null and not field.has_default(),
                }
                
                if isinstance(field, models.ForeignKey):
                    field_info['fk_to'] = field.related_model._meta.model_name
                    field_info['taxonomy'] = cls.FK_FIELD_MAP.get(field.name)
                
                if hasattr(field, 'choices') and field.choices:
                    field_info['choices'] = [{'value': c[0], 'label': c[1]} for c in field.choices]
                
                if isinstance(field, (models.CharField, models.TextField)):
                    field_info['max_length'] = getattr(field, 'max_length', None)
                
                fields.append(field_info)
        
        return fields
    
    @classmethod
    def _get_field_type(cls, field) -> str:
        """获取字段类型"""
        if isinstance(field, models.AutoField):
            return 'auto'
        elif isinstance(field, models.CharField):
            return 'string'
        elif isinstance(field, models.TextField):
            return 'text'
        elif isinstance(field, models.IntegerField):
            return 'integer'
        elif isinstance(field, models.FloatField):
            return 'float'
        elif isinstance(field, models.DecimalField):
            return 'decimal'
        elif isinstance(field, models.BooleanField):
            return 'boolean'
        elif isinstance(field, models.DateField):
            return 'date'
        elif isinstance(field, models.DateTimeField):
            return 'datetime'
        elif isinstance(field, models.EmailField):
            return 'email'
        elif isinstance(field, models.URLField):
            return 'url'
        elif isinstance(field, models.JSONField):
            return 'json'
        elif isinstance(field, models.ForeignKey):
            return 'fk'
        else:
            return 'unknown'
    
    @classmethod
    def get_exportable_fields(cls, model_class: Type) -> List[Dict]:
        """获取可导出字段（包含关联字段）"""
        fields = cls.extract(model_class)
        
        for field in model_class._meta.get_fields():
            if hasattr(field, 'attname') and field.name not in cls.EXCLUDE_FIELDS:
                if isinstance(field, models.ForeignKey):
                    fields.append({
                        'name': f'{field.name}_display',
                        'label': f'{getattr(field, "verbose_name", field.name)} (显示)',
                        'type': 'display',
                    })
        
        return fields
