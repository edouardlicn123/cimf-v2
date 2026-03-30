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
from core.node.models import NodeType, Node, Module

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


class ModuleService:
    """Node 模块服务"""
    
    MODULES_DIR = 'modules'
    
    # ===== 扫描功能 =====
    
    @staticmethod
    def scan_modules() -> List[Dict[str, Any]]:
        """扫描 modules/ 目录下的所有模块"""
        modules = []
        base_path = ModuleService.MODULES_DIR
        
        if not os.path.exists(base_path):
            return modules
        
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            
            if not os.path.isdir(item_path):
                continue
            
            module_file = os.path.join(item_path, 'module.py')
            if not os.path.exists(module_file):
                continue
            
            module_info = ModuleService._load_module_info(item)
            if module_info:
                registered = Module.objects.filter(module_id=module_info['id']).first()
                module_info['is_registered'] = registered is not None
                module_info['is_installed'] = registered.is_installed if registered else False
                module_info['is_active'] = registered.is_active if registered else False
                module_info['path'] = item
                modules.append(module_info)
        
        return modules
    
    @staticmethod
    def _load_module_info(module_dir: str) -> Optional[Dict[str, Any]]:
        """加载模块信息 - 使用 ast 直接解析文件，无需 importlib"""
        import ast
        
        def parse_node(node):
            """递归解析 AST 节点"""
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.NameConstant):
                return node.value
            elif isinstance(node, ast.List):
                return [parse_node(elem) for elem in node.elts]
            elif isinstance(node, ast.Dict):
                result = {}
                for k, v in zip(node.keys, node.values):
                    key = parse_node(k)
                    value = parse_node(v)
                    if key is not None:
                        result[key] = value
                return result
            else:
                return None
        
        try:
            module_file = os.path.join(
                ModuleService.MODULES_DIR, 
                module_dir, 
                'module.py'
            )
            
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if (isinstance(target, ast.Name) and 
                            target.id == 'MODULE_INFO' and
                            isinstance(node.value, ast.Dict)):
                            
                            module_info = parse_node(node.value)
                            
                            if not isinstance(module_info, dict):
                                return None
                            
                            if 'type' not in module_info:
                                raise ValueError(f"模块 {module_dir} 缺少 type 字段")
                            
                            return module_info
            
            return None
            
        except ValueError:
            raise
        except Exception as e:
            print(f"解析模块 {module_dir} 信息失败: {e}")
            return None
    
    # ===== 注册功能 =====
    
    @staticmethod
    def register_module(module_info: Dict[str, Any]) -> Module:
        """注册模块 - 写入数据库，标记为未安装"""
        module_id = module_info['id']
        existing = Module.objects.filter(module_id=module_id).first()
        
        if existing:
            existing.is_installed = False
            existing.is_active = False
            existing.module_type = module_info.get('type', 'node')
            existing.save()
            return existing
        
        module = Module.objects.create(
            module_id=module_id,
            name=module_info.get('name', module_id),
            version=module_info.get('version', '1.0.0'),
            author=module_info.get('author'),
            description=module_info.get('description'),
            path=module_info.get('path', module_id),
            module_type=module_info.get('type', 'node'),
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
        
        module = Module.objects.filter(module_id=module_id).first()
        if not module:
            return False
        
        # 检查是否已安装
        if module.is_installed:
            return True
        
        # 检查模块目录是否存在
        module_path = os.path.join(ModuleService.MODULES_DIR, module_id)
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
        
        # 同步 NodeType（仅 node 类型模块需要）
        if module.module_type == 'node':
            ModuleService.sync_node_type(module)
        
        # 创建模块定义的词汇表
        ModuleService.create_module_taxonomies(module)
        
        # 标记为已安装
        module.is_installed = True
        module.installed_at = timezone.now()
        module.save()
        
        return True
    
    @staticmethod
    def register_and_install(module_info: Dict[str, Any]) -> Module:
        """注册并安装模块"""
        module = ModuleService.register_module(module_info)
        ModuleService.install_module(module.module_id)
        ModuleService.enable_module(module.module_id)
        module.refresh_from_db()
        return module
    
    @staticmethod
    def create_module_taxonomies(module: Module) -> int:
        """创建模块定义的词汇表"""
        from core.models import Taxonomy, TaxonomyItem
        
        # 加载模块信息
        module_info = ModuleService._load_module_info(module.path)
        if not module_info:
            return 0
        
        # 检查是否有词汇表定义
        taxonomies = module_info.get('taxonomies', [])
        if not taxonomies:
            return 0
        
        created_count = 0
        
        for tax_data in taxonomies:
            slug = tax_data.get('slug')
            name = tax_data.get('name')
            items = tax_data.get('items', [])
            
            if not slug or not name:
                continue
            
            # 检查词汇表是否已存在
            existing = Taxonomy.objects.filter(slug=slug).first()
            if existing:
                # 词汇表已存在，检查是否需要添加词汇项
                for item_name in items:
                    TaxonomyItem.objects.get_or_create(
                        taxonomy=existing,
                        name=item_name,
                        defaults={'weight': 0}
                    )
                continue
            
            # 创建词汇表
            taxonomy = Taxonomy.objects.create(
                name=name,
                slug=slug,
                description=f'{module.name} 模块词汇表'
            )
            
            # 创建词汇项
            for idx, item_name in enumerate(items):
                TaxonomyItem.objects.create(
                    taxonomy=taxonomy,
                    name=item_name,
                    weight=idx
                )
            
            created_count += 1
        
        return created_count
    
    # ===== 启用/禁用功能 =====
    
    @staticmethod
    def enable_module(module_id: str) -> Optional[Module]:
        """启用模块并同步节点类型"""
        try:
            module = Module.objects.get(module_id=module_id)
            if module.is_installed:
                module.is_active = True
                module.activated_at = timezone.now()
                module.save(update_fields=['is_active', 'activated_at'])
                
                if module.module_type == 'node':
                    node_type = NodeType.objects.filter(slug=module.module_id).first()
                    if node_type:
                        node_type.is_active = True
                        node_type.save(update_fields=['is_active'])
                
                return module
        except Module.DoesNotExist:
            pass
        return None
    
    @staticmethod
    def disable_module(module_id: str) -> Optional[Module]:
        """禁用模块并同步节点类型"""
        try:
            module = Module.objects.get(module_id=module_id)
            module.is_active = False
            module.save(update_fields=['is_active'])
            
            if module.module_type == 'node':
                node_type = NodeType.objects.filter(slug=module.module_id).first()
                if node_type:
                    node_type.is_active = False
                    node_type.save(update_fields=['is_active'])
            
            return module
        except Module.DoesNotExist:
            pass
        return None
    
    # ===== 删除注册功能 =====
    
    @staticmethod
    def cleanup_uninstalled_modules() -> List[str]:
        """清理已卸载的模块注册记录"""
        registered_modules = Module.objects.filter(is_installed=True)
        cleaned = []
        
        for module in registered_modules:
            module_path = os.path.join(ModuleService.MODULES_DIR, module.path)
            module_file = os.path.join(module_path, 'module.py')
            
            if not os.path.exists(module_file) and not module.is_active:
                module.delete()
                cleaned.append(module.module_id)
        
        return cleaned
    
    # ===== 查询功能 =====
    
    @staticmethod
    def get_all() -> List[Module]:
        """获取所有已注册的模块"""
        return list(Module.objects.all())
    
    @staticmethod
    def get_installed() -> List[Module]:
        """获取已安装的模块"""
        return list(Module.objects.filter(is_installed=True))
    
    @staticmethod
    def get_active() -> List[Module]:
        """获取已启用的模块"""
        return list(Module.objects.filter(is_installed=True, is_active=True))
    
    @staticmethod
    def get_by_id(module_id: str) -> Optional[Module]:
        """根据 ID 获取模块"""
        return Module.objects.filter(module_id=module_id).first()
    
    # ===== 同步功能 =====
    
    @staticmethod
    def sync_node_type(module: Module) -> NodeType:
        """同步模块与节点类型"""
        # 从 module.py 读取图标
        module_info = ModuleService._load_module_info(module.path)
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
    def create_module(module_id: str, name: str, module_type: str = 'node', description: str = '', icon: str = 'bi-folder') -> Dict[str, Any]:
        """创建新模块 - 在文件系统中创建模块目录和基础文件"""
        import shutil
        
        module_path = os.path.join(ModuleService.MODULES_DIR, module_id)
        
        # 检查目录是否已存在
        if os.path.exists(module_path):
            return {'success': False, 'error': f'模块目录已存在: {module_id}'}
        
        # 检查模块 ID 格式
        if not module_id or not module_id.replace('_', '').replace('-', '').isalnum():
            return {'success': False, 'error': '模块 ID 只能包含字母、数字、下划线和连字符'}
        
        # 检查模块 ID 是否已注册
        existing = Module.objects.filter(module_id=module_id).first()
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
    'type': '{module_type}',
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