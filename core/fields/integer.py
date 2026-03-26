# -*- coding: utf-8 -*-
"""
================================================================================
文件：integer.py
路径：/home/edo/cimf-v2/core/fields/integer.py
================================================================================

功能说明：
    整数字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class IntegerField(BaseField):
    name = 'integer'
    label = '整数'
    widget = 'input'
    properties = ['value', 'min', 'max']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return str(value.get('value', ''))
        
        min_val = self.field_config.get('min', '')
        max_val = self.field_config.get('max', '')
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '')
        
        attrs = f'min="{min_val}" ' if min_val else ''
        attrs += f'max="{max_val}" ' if max_val else ''
        attrs += f'placeholder="{placeholder}"'
        
        return f'<input type="number" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" {attrs} {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        val = value.get('value')
        if self.field_config.get('required') and not val:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        if val:
            try:
                int_val = int(val)
                if self.field_config.get('min') and int_val < int(self.field_config['min']):
                    errors.append(f'{self.field_config.get("label")} 不能小于 {self.field_config["min"]}')
                if self.field_config.get('max') and int_val > int(self.field_config['max']):
                    errors.append(f'{self.field_config.get("label")} 不能大于 {self.field_config["max"]}')
            except ValueError:
                errors.append(f'{self.field_config.get("label")} 必须是整数')
        return errors
