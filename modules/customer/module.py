# -*- coding: utf-8 -*-
"""
================================================================================
文件：module.py
路径：/home/edo/cimf-v2/modules/customer/module.py
================================================================================

功能说明：
    客户信息（海外）模块信息文件
    
    定义模块的基本信息，供系统扫描和注册使用。

版本：
    - 1.0.0: 初始版本
"""

MODULE_INFO = {
    'id': 'customer',
    'name': '客户信息（海外）',
    'type': 'node',
    'version': '1.0.0',
    'author': 'edouardlicn',
    'description': '海外客户信息管理模块',
    'models': ['CustomerFields'],
    'dependencies': [],
    'icon': 'bi-people',
    'views': {
        'list': 'customer_list',
        'create': 'customer_create',
        'view': 'customer_view',
        'edit': 'customer_edit',
        'delete': 'customer_delete',
    },
}


def get_install_sql():
    """获取模块安装时执行的 SQL（可选）"""
    return None


def get_uninstall_sql():
    """获取模块卸载时执行的 SQL（可选）"""
    return None
