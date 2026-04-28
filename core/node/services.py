# -*- coding: utf-8 -*-
"""
Node 节点系统服务（向后兼容）

内容已迁移到 core/node/services/ 目录
保留此文件以保持向后兼容
"""

from core.node.services import NodeTypeService, NodeService, ModuleService


def get_dynamic_model_class(module_id: str):
    """动态生成模型类（向后兼容）"""
    from core.node.models import Node
    return type(f'{module_id.title().replace("-", "").replace("_", "")}Model', (Node,), {
        '__module__': 'core.node.services',
        'Meta': type('Meta', (), {'proxy': True}),
    })


__all__ = ['NodeTypeService', 'NodeService', 'ModuleService', 'get_dynamic_model_class']