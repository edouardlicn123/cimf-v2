# -*- coding: utf-8 -*-
"""
================================================================================
文件：services.py
路径：/home/edo/cimf-v2/core/node/services.py
================================================================================

功能说明：
    Node 节点系统服务层，包含节点类型服务和节点服务
    
    主要服务：
    - NodeTypeService: 节点类型 CRUD
    - NodeService: 节点 CRUD

版本：
    - 1.0: 从 nodes/services/ 迁移

依赖：
    - core.node.models: NodeType, Node
    - django.contrib.auth: 用户模型
"""

from typing import List, Optional, Dict, Any
import os
import importlib.util
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.node.models import NodeType, Node, NodeModule

User = get_user_model()


DEFAULT_NODE_TYPES = [
    {
        'name': '客户信息（海外）',
        'slug': 'customer',
        'description': '海外客户信息管理',
        'icon': 'bi-people',
        'fields_config': [
            {'field_type': 'string', 'name': 'customer_name', 'label': '客户名称', 'required': True, 'unique': True},
            {'field_type': 'string', 'name': 'contact_person', 'label': '联系人', 'required': False},
            {'field_type': 'telephone', 'name': 'phone', 'label': '电话', 'required': False},
            {'field_type': 'email', 'name': 'email', 'label': '邮箱', 'required': False},
            {'field_type': 'address', 'name': 'address', 'label': '地址', 'required': False},
            {'field_type': 'entity_reference', 'name': 'customer_type', 'label': '客户类型', 'required': False, 'reference_type': 'taxonomy'},
            {'field_type': 'string_long', 'name': 'notes', 'label': '备注', 'required': False},
        ],
        'is_active': True,
    },
    {
        'name': '客户信息（国内）',
        'slug': 'customer_cn',
        'description': '国内客户信息管理',
        'icon': 'bi-people',
        'fields_config': [
            {'field_type': 'string', 'name': 'customer_name', 'label': '客户名称', 'required': True, 'unique': True},
            {'field_type': 'string', 'name': 'customer_code', 'label': '客户代码', 'required': False},
            {'field_type': 'entity_reference', 'name': 'customer_type', 'label': '客户类型', 'required': False, 'reference_type': 'taxonomy'},
            {'field_type': 'string', 'name': 'enterprise_name', 'label': '企业名称', 'required': False},
            {'field_type': 'telephone', 'name': 'phone1', 'label': '电话1', 'required': False},
            {'field_type': 'email', 'name': 'email1', 'label': '邮箱1', 'required': False},
            {'field_type': 'telephone', 'name': 'phone2', 'label': '电话2', 'required': False},
            {'field_type': 'email', 'name': 'email2', 'label': '邮箱2', 'required': False},
            {'field_type': 'region_select', 'name': 'region', 'label': '省市区', 'required': False},
            {'field_type': 'string', 'name': 'address', 'label': '详细地址', 'required': False},
            {'field_type': 'string', 'name': 'postal_code', 'label': '邮政编码', 'required': False},
            {'field_type': 'string', 'name': 'wechat', 'label': '微信号', 'required': False},
            {'field_type': 'string', 'name': 'dingtalk', 'label': '钉钉号', 'required': False},
            {'field_type': 'string', 'name': 'industry', 'label': '所属行业', 'required': False},
            {'field_type': 'entity_reference', 'name': 'enterprise_type', 'label': '企业性质', 'required': False, 'reference_type': 'taxonomy'},
            {'field_type': 'decimal', 'name': 'registered_capital', 'label': '注册资本', 'required': False},
            {'field_type': 'entity_reference', 'name': 'customer_level', 'label': '客户等级', 'required': False, 'reference_type': 'taxonomy'},
            {'field_type': 'decimal', 'name': 'credit_limit', 'label': '信用额度', 'required': False},
            {'field_type': 'link', 'name': 'website', 'label': '网站', 'required': False},
            {'field_type': 'text_long', 'name': 'notes', 'label': '备注', 'required': False},
        ],
        'is_active': True,
    },
]


class NodeTypeService:
    """节点类型服务"""
    
    @staticmethod
    def get_all() -> List[NodeType]:
        """获取所有启用的节点类型"""
        return NodeType.objects.filter(is_active=True)
    
    @staticmethod
    def get_all_including_inactive() -> List[NodeType]:
        """获取所有节点类型（包括禁用的）"""
        return NodeType.objects.all()
    
    @staticmethod
    def get_by_id(node_type_id: int) -> Optional[NodeType]:
        """根据 ID 获取节点类型"""
        return NodeType.objects.filter(id=node_type_id).first()
    
    @staticmethod
    def get_by_slug(slug: str) -> Optional[NodeType]:
        """根据 slug 获取启用的节点类型"""
        return NodeType.objects.filter(slug=slug, is_active=True).first()
    
    @staticmethod
    def get_by_slug_including_inactive(slug: str) -> Optional[NodeType]:
        """根据 slug 获取节点类型（包括禁用的）"""
        return NodeType.objects.filter(slug=slug).first()
    
    @staticmethod
    def create(data: Dict[str, Any]) -> NodeType:
        """创建节点类型"""
        node_type = NodeType.objects.create(**data)
        return node_type
    
    @staticmethod
    def update(node_type_id: int, data: Dict[str, Any]) -> Optional[NodeType]:
        """更新节点类型"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            for key, value in data.items():
                if hasattr(node_type, key):
                    setattr(node_type, key, value)
            node_type.save()
        return node_type
    
    @staticmethod
    def delete(node_type_id: int) -> bool:
        """删除节点类型（软删除）"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = False
            node_type.save()
            return True
        return False
    
    @staticmethod
    def enable(node_type_id: int) -> bool:
        """启用节点类型"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = True
            node_type.save()
            return True
        return False
    
    @staticmethod
    def disable(node_type_id: int) -> bool:
        """禁用节点类型"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = False
            node_type.save()
            return True
        return False
    
    @staticmethod
    def get_node_count(node_type_id: int) -> int:
        """获取节点类型的节点数量"""
        return Node.objects.filter(node_type_id=node_type_id).count()
    
    @staticmethod
    def init_default_node_types() -> None:
        """初始化预置节点类型"""
        for nt_data in DEFAULT_NODE_TYPES:
            existing = NodeType.objects.filter(slug=nt_data['slug']).first()
            if existing:
                continue
            
            NodeType.objects.create(
                name=nt_data['name'],
                slug=nt_data['slug'],
                description=nt_data.get('description', ''),
                icon=nt_data.get('icon', 'bi-folder'),
                fields_config=nt_data.get('fields_config', []),
                is_active=nt_data.get('is_active', True)
            )


class NodeService:
    """节点服务"""
    
    @staticmethod
    def get_list(node_type_slug: str, search: Optional[str] = None) -> List[Node]:
        """获取节点列表"""
        node_type = NodeTypeService.get_by_slug(node_type_slug)
        if not node_type:
            return []
        
        queryset = Node.objects.filter(node_type=node_type)
        
        if search:
            try:
                node_id = int(search)
                queryset = queryset.filter(id=node_id)
            except ValueError:
                pass
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(node_id: int) -> Optional[Node]:
        """根据 ID 获取节点"""
        return Node.objects.filter(id=node_id).first()
    
    @staticmethod
    def create(node_type_slug: str, user, data: Dict[str, Any]) -> Optional[Node]:
        """创建节点"""
        node_type = NodeTypeService.get_by_slug(node_type_slug)
        if not node_type:
            return None
        
        node = Node.objects.create(
            node_type=node_type,
            created_by=user,
            updated_by=user
        )
        
        return node
    
    @staticmethod
    def update(node_id: int, user, data: Dict[str, Any]) -> Optional[Node]:
        """更新节点"""
        node = Node.objects.filter(id=node_id).first()
        if not node:
            return None
        
        node.updated_by = user
        node.save()
        
        return node
    
    @staticmethod
    def delete(node_id: int) -> bool:
        """删除节点"""
        node = Node.objects.filter(id=node_id).first()
        if node:
            node.delete()
            return True
        return False
    
    @staticmethod
    def get_customer_nodes(search: Optional[str] = None) -> List[Node]:
        """获取客户节点列表"""
        return NodeService.get_list('customer', search)


class NodeModuleService:
    """Node 模块服务"""
    
    MODULES_DIR = 'modules'
    
    # ===== 扫描功能 =====
    
    @staticmethod
    def scan_modules() -> List[Dict[str, Any]]:
        """扫描 nodes/ 目录下的所有模块"""
        modules = []
        base_path = NodeModuleService.MODULES_DIR
        
        if not os.path.exists(base_path):
            return modules
        
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            
            if not os.path.isdir(item_path):
                continue
            
            module_file = os.path.join(item_path, 'module.py')
            if not os.path.exists(module_file):
                continue
            
            module_info = NodeModuleService._load_module_info(item)
            if module_info:
                registered = NodeModule.objects.filter(module_id=module_info['id']).first()
                module_info['is_registered'] = registered is not None
                module_info['is_installed'] = registered.is_installed if registered else False
                module_info['is_active'] = registered.is_active if registered else False
                module_info['path'] = item
                modules.append(module_info)
        
        return modules
    
    @staticmethod
    def _load_module_info(module_dir: str) -> Optional[Dict[str, Any]]:
        """加载模块信息"""
        try:
            module_file = os.path.join(NodeModuleService.MODULES_DIR, module_dir, 'module.py')
            spec = importlib.util.spec_from_file_location(f"modules.{module_dir}.module", module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'MODULE_INFO'):
                return module.MODULE_INFO
            return None
        except Exception as e:
            print(f"加载模块 {module_dir} 信息失败: {e}")
            return None
    
    # ===== 注册功能 =====
    
    @staticmethod
    def register_module(module_info: Dict[str, Any]) -> NodeModule:
        """注册模块 - 写入数据库，标记为未安装"""
        module_id = module_info['id']
        existing = NodeModule.objects.filter(module_id=module_id).first()
        
        if existing:
            existing.is_installed = False
            existing.is_active = False
            existing.save()
            return existing
        
        module = NodeModule.objects.create(
            module_id=module_id,
            name=module_info.get('name', module_id),
            version=module_info.get('version', '1.0.0'),
            author=module_info.get('author'),
            description=module_info.get('description'),
            path=module_info.get('path', module_id),
            is_installed=False,
            is_active=False,
            is_system=False,
        )
        
        return module
    
    # ===== 安装功能 =====
    
    @staticmethod
    def install_module(module_id: str) -> bool:
        """安装模块 - 完成数据库结构操作"""
        from django.apps import apps
        from django.core.management import call_command
        
        module = NodeModule.objects.filter(module_id=module_id).first()
        if not module:
            return False
        
        # 检查是否已安装
        if module.is_installed:
            return True
        
        # 检查模块目录是否存在
        module_path = os.path.join(NodeModuleService.MODULES_DIR, module_id)
        if not os.path.exists(module_path):
            return False
        
        # 检查 migrations 目录是否存在
        migrations_path = os.path.join(module_path, 'migrations')
        if os.path.exists(migrations_path):
            # 简化处理：直接执行 migrate，使用 --run-syncdb 确保表存在
            try:
                call_command('makemigrations', module_id, verbosity=0, interactive=False)
            except Exception:
                pass
            
            try:
                call_command('migrate', module_id, verbosity=0, interactive=False, run_syncdb=True)
            except Exception:
                pass
        
        # 同步 NodeType
        NodeModuleService.sync_node_type(module)
        
        # 标记为已安装
        module.is_installed = True
        module.installed_at = timezone.now()
        module.save()
        
        return True
    
    @staticmethod
    def register_and_install(module_info: Dict[str, Any]) -> NodeModule:
        """注册并安装模块"""
        module = NodeModuleService.register_module(module_info)
        NodeModuleService.install_module(module.module_id)
        NodeModuleService.enable_module(module.module_id)
        module.refresh_from_db()
        return module
    
    # ===== 启用/禁用功能 =====
    
    @staticmethod
    def enable_module(module_id: str) -> Optional[NodeModule]:
        """启用模块并同步节点类型"""
        try:
            module = NodeModule.objects.get(module_id=module_id)
            if module.is_installed:
                module.is_active = True
                module.activated_at = timezone.now()
                module.save(update_fields=['is_active', 'activated_at'])
                
                node_type = NodeType.objects.filter(slug=module.module_id).first()
                if node_type:
                    node_type.is_active = True
                    node_type.save(update_fields=['is_active'])
                
                return module
        except NodeModule.DoesNotExist:
            pass
        return None
    
    @staticmethod
    def disable_module(module_id: str) -> Optional[NodeModule]:
        """禁用模块并同步节点类型"""
        try:
            module = NodeModule.objects.get(module_id=module_id)
            module.is_active = False
            module.save(update_fields=['is_active'])
            
            node_type = NodeType.objects.filter(slug=module.module_id).first()
            if node_type:
                node_type.is_active = False
                node_type.save(update_fields=['is_active'])
            
            return module
        except NodeModule.DoesNotExist:
            pass
        return None
    
    # ===== 删除注册功能 =====
    
    @staticmethod
    def cleanup_uninstalled_modules() -> List[str]:
        """清理已卸载的模块注册记录"""
        registered_modules = NodeModule.objects.filter(is_installed=True)
        cleaned = []
        
        for module in registered_modules:
            module_path = os.path.join(NodeModuleService.MODULES_DIR, module.path)
            module_file = os.path.join(module_path, 'module.py')
            
            if not os.path.exists(module_file) and not module.is_active:
                module.delete()
                cleaned.append(module.module_id)
        
        return cleaned
    
    # ===== 查询功能 =====
    
    @staticmethod
    def get_all() -> List[NodeModule]:
        """获取所有已注册的模块"""
        return list(NodeModule.objects.all())
    
    @staticmethod
    def get_installed() -> List[NodeModule]:
        """获取已安装的模块"""
        return list(NodeModule.objects.filter(is_installed=True))
    
    @staticmethod
    def get_active() -> List[NodeModule]:
        """获取已启用的模块"""
        return list(NodeModule.objects.filter(is_installed=True, is_active=True))
    
    @staticmethod
    def get_by_id(module_id: str) -> Optional[NodeModule]:
        """根据 ID 获取模块"""
        return NodeModule.objects.filter(module_id=module_id).first()
    
    # ===== 同步功能 =====
    
    @staticmethod
    def sync_node_type(module: NodeModule) -> NodeType:
        """同步模块与节点类型"""
        # 从 module.py 读取图标
        module_info = NodeModuleService._load_module_info(module.path)
        icon = module_info.get('icon', 'bi-folder') if module_info else 'bi-folder'
        
        node_type = NodeType.objects.filter(slug=module.module_id).first()
        
        if not node_type:
            node_type = NodeType.objects.create(
                name=module.name,
                slug=module.module_id,
                description=module.description or '',
                icon=icon,
                is_active=module.is_active,
            )
        else:
            node_type.name = module.name
            node_type.description = module.description or ''
            node_type.icon = icon
            node_type.is_active = module.is_active
            node_type.save()
        
        return node_type

    @staticmethod
    def create_module(module_id: str, name: str, description: str = '', icon: str = 'bi-folder') -> Dict[str, Any]:
        """创建新模块 - 在文件系统中创建模块目录和基础文件"""
        import shutil
        
        module_path = os.path.join(NodeModuleService.MODULES_DIR, module_id)
        
        # 检查目录是否已存在
        if os.path.exists(module_path):
            return {'success': False, 'error': f'模块目录已存在: {module_id}'}
        
        # 检查模块 ID 格式
        if not module_id or not module_id.replace('_', '').replace('-', '').isalnum():
            return {'success': False, 'error': '模块 ID 只能包含字母、数字、下划线和连字符'}
        
        # 检查模块 ID 是否已注册
        existing = NodeModule.objects.filter(module_id=module_id).first()
        if existing:
            return {'success': False, 'error': f'模块 ID 已注册: {module_id}'}
        
        try:
            # 创建模块目录
            os.makedirs(module_path, mode=0o755)
            
            # 创建 __init__.py
            with open(os.path.join(module_path, '__init__.py'), 'w') as f:
                f.write('# -*- coding: utf-8 -*-\n')
            
            # 创建 module.py
            module_py_content = f'''# -*- coding: utf-8 -*-
"""
模块信息
"""

MODULE_INFO = {{
    'id': '{module_id}',
    'name': '{name}',
    'version': '1.0.0',
    'author': '',
    'description': '{description}',
    'icon': '{icon}',
}}
'''
            with open(os.path.join(module_path, 'module.py'), 'w') as f:
                f.write(module_py_content)
            
            # 创建 models.py
            models_content = f'''# -*- coding: utf-8 -*-
from django.db import models


class {module_id.title().replace('-', '').replace('_', '')}Model(models.Model):
    pass
'''
            with open(os.path.join(module_path, 'models.py'), 'w') as f:
                f.write(models_content)
            
            # 创建 views.py
            views_content = f'''# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def list_view(request):
    return JsonResponse({{'message': 'List view for {module_id}'}})


@login_required
@require_http_methods(["GET"])
def detail_view(request, pk):
    return JsonResponse({{'message': f'Detail view for {{pk}}'}})
'''
            with open(os.path.join(module_path, 'views.py'), 'w') as f:
                f.write(views_content)
            
            # 创建 migrations 目录
            migrations_path = os.path.join(module_path, 'migrations')
            os.makedirs(migrations_path, mode=0o755)
            
            # 创建 migrations/__init__.py
            with open(os.path.join(migrations_path, '__init__.py'), 'w') as f:
                f.write('# -*- coding: utf-8 -*-\n')
            
            return {'success': True, 'module_id': module_id, 'path': module_path}
            
        except PermissionError:
            return {'success': False, 'error': '权限不足，无法创建目录'}
        except Exception as e:
            # 清理已创建的目录
            if os.path.exists(module_path):
                shutil.rmtree(module_path)
            return {'success': False, 'error': f'创建模块失败: {str(e)}'}