# -*- coding: utf-8 -*-
"""
================================================================================
文件：text.py
路径：/home/edo/cimf-v2/core/fields/text.py
================================================================================

功能说明：
    带格式文本字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class TextField(BaseField):
    name = 'text'
    label = '带格式文本'
    widget = 'rich_text'
    properties = ['value', 'format']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('value', '')
        
        required = self.field_config.get('required', False)
        
        return f'<div class="rich-text-editor" data-field="{self.field_name}">' \
               f'<textarea name="{self.field_name}" class="form-control rich-text" ' \
               f'{"required" if required else ""}>{value.get("value", "")}</textarea></div>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
