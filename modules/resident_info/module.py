# -*- coding: utf-8 -*-
"""
模块信息
"""

MODULE_INFO = {
    'id': 'resident_info',
    'name': '居民信息',
    'type': 'node',
    'version': '1.0.0',
    'author': '',
    'description': '管理居民住户信息，适合居委会及网格员使用。',
    'icon': 'bi-person-vcard',
    'dashboard_cards': [
        {
            'id': 'resident_info_card',
            'name': '居民信息',
            'template': 'resident_info/dashboard_card.html',
        }
    ],
    'taxonomies': [
        {'slug': 'resident_relation', 'name': '与户主关系', 'items': ['户主', '配偶', '子女', '父母', '租户', '其他']},
        {'slug': 'resident_type', 'name': '人员类型', 'items': ['常住人口', '流动人口', '暂住人口']},
        {'slug': 'grid', 'name': '所属网格', 'items': ['网格1', '网格2', '网格3', '网格4', '网格5']},
        {'slug': 'key_category', 'name': '重点类别', 'items': ['独居老人', '低保户', '残疾人', '重症患者', '刑满释放人员', '社区矫正对象', '涉毒人员', '其他']},
        {'slug': 'nation', 'name': '民族', 'items': ['汉族', '壮族', '满族', '回族', '苗族', '维吾尔族', '蒙古族', '藏族', '其他']},
        {'slug': 'political_status', 'name': '政治面貌', 'items': ['中共党员', '中共预备党员', '共青团员', '群众']},
        {'slug': 'marital_status', 'name': '婚姻状况', 'items': ['未婚', '已婚', '离异', '丧偶']},
        {'slug': 'education', 'name': '文化程度', 'items': ['研究生', '本科', '大专', '高中', '初中', '小学', '文盲']},
        {'slug': 'health_status', 'name': '健康状况', 'items': ['健康', '良好', '残疾', '疾病', '慢性病']},
    ],
}


def get_install_sql():
    """获取模块安装时执行的 SQL（可选）"""
    return None


def get_uninstall_sql():
    """获取模块卸载时执行的 SQL（可选）"""
    return None