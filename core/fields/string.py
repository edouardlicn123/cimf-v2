# -*- coding: utf-8 -*-
"""
================================================================================
文件：string.py
路径：/home/edo/cimf-v2/core/fields/string.py
================================================================================

功能说明：
    单行文本字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class StringField(BaseField):
    name = 'string'
    label = '单行文本'
    widget = 'input'
    properties = ['value', 'max_length']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('value', '')
        
        max_length = self.field_config.get('max_length', 255)
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '')
        
        return f'<input type="text" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'maxlength="{max_length}" class="form-control" ' \
               f'{"required" if required else ""} placeholder="{placeholder}">'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
