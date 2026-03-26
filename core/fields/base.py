# -*- coding: utf-8 -*-
"""
================================================================================
文件：base.py
路径：/home/edo/cimf-v2/core/fields/base.py
================================================================================

功能说明：
    字段类型基类，所有自定义字段类型继承此基类
    
版本：
    - 1.0: 从 Flask 迁移

依赖：
    - 无
"""

class BaseField:
    """字段类型基类"""
    name = None
    label = None
    widget = None
    properties = []
    
    def __init__(self, field_name: str, field_config: dict):
        self.field_name = field_name
        self.field_config = field_config
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        """渲染字段表单控件
        
        参数：
            value: 字段当前值
            mode: 渲染模式 (edit/view)
        """
        raise NotImplementedError
    
    def validate(self, value: dict) -> list:
        """验证字段值
        
        参数：
            value: 待验证的值
            
        返回：
            错误信息列表
        """
        return []
    
    def format(self, value) -> any:
        """格式化字段值用于显示
        
        参数：
            value: 原始值
            
        返回：
            格式化后的值
        """
        return value
    
    def get_widget_config(self) -> dict:
        """获取控件配置
        
        返回：
            控件配置字典
        """
        return {}
