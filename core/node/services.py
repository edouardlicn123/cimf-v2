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
from io import StringIO
import os
import importlib.util
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.node.models import NodeType, Node, Module

User = get_user_model()


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
    def get_node_types_from_modules() -> List[Dict[str, Any]]:
        """从模块配置中动态获取节点类型定义"""
        from importlib import import_module
        
        node_types = []
        modules_dir = 'modules'
        
        if not os.path.exists(modules_dir):
            return node_types
        
        for item in os.listdir(modules_dir):
            item_path = os.path.join(modules_dir, item)
            
            if not os.path.isdir(item_path):
                continue
            
            module_file = os.path.join(item_path, 'module.py')
            if not os.path.exists(module_file):
                continue
            
            try:
                mod = import_module(f'modules.{item}.module')
                if hasattr(mod, 'MODULE_INFO'):
                    module_info = mod.MODULE_INFO
                    
                    # 只处理 node 类型的模块
                    if module_info.get('type') == 'node':
                        node_type_config = module_info.get('node_type', {})
                        
                        # 如果模块没有 node_type 配置，使用模块基本信息
                        if not node_type_config:
                            node_type_config = {
                                'name': module_info.get('name', item),
                                'slug': module_info.get('id', item),
                                'description': module_info.get('description', ''),
                                'icon': module_info.get('icon', 'bi-folder'),
                            }
                        
                        node_types.append(node_type_config)
            except (ImportError, ModuleNotFoundError, AttributeError):
                pass
        
        return node_types
    
    @staticmethod
    def init_default_node_types() -> None:
        """初始化预置节点类型（从模块配置动态读取）"""
        # 从模块配置中获取节点类型定义
        node_types_config = NodeTypeService.get_node_types_from_modules()
        
        for nt_data in node_types_config:
            slug = nt_data.get('slug')
            if not slug:
                continue
            
            existing = NodeType.objects.filter(slug=slug).first()
            if existing:
                continue
            
            NodeType.objects.create(
                name=nt_data.get('name', slug),
                slug=slug,
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
    def _check_tables_exist(module_id: str) -> bool:
        """检查模块的表是否已存在"""
        from django.apps import apps
        from django.db import connection
        
        try:
            models = apps.get_app_config(module_id).get_models()
            table_names = connection.introspection.table_names(connection.cursor())
            
            for model in models:
                if model._meta.db_table not in table_names:
                    return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def install_module(module_id: str) -> bool:
        """安装模块 - 完成数据库结构操作"""
        from django.apps import apps
        from django.core.management import call_command
        from django.db import connection
        
        module = Module.objects.filter(module_id=module_id).first()
        if not module:
            return False
        
        # 检查模块目录是否存在
        module_path = os.path.join(ModuleService.MODULES_DIR, module_id)
        if not os.path.exists(module_path):
            return False
        
        # 检查 migrations 目录是否存在
        migrations_path = os.path.join(module_path, 'migrations')
        
        # 如果标记为已安装，先验证表是否真正存在
        if module.is_installed and os.path.exists(migrations_path):
            if not ModuleService._check_tables_exist(module_id):
                # 表不存在但标记为已安装，说明迁移可能失败过
                # 取消安装标记，重新执行迁移
                module.is_installed = False
                module.save()
        
        # 如果已安装且表存在，跳过迁移
        if module.is_installed:
            return True
        
        # 执行迁移
        if os.path.exists(migrations_path):
            migration_errors = []
            
            # 1. 执行 makemigrations
            try:
                out = StringIO()
                call_command('makemigrations', module_id, verbosity=1, interactive=False, stdout=out)
            except Exception as e:
                migration_errors.append(f'makemigrations 失败: {e}')
            
            # 2. 执行 migrate
            try:
                out = StringIO()
                call_command('migrate', module_id, verbosity=1, interactive=False, run_syncdb=True, stdout=out)
            except Exception as e:
                migration_errors.append(f'migrate 失败: {e}')
            
            # 3. 验证迁移是否成功
            if not ModuleService._check_tables_exist(module_id):
                migration_errors.append(f'迁移后表仍未创建，模块 {module_id} 可能配置不正确')
            
            # 如果有迁移错误，记录并抛出
            if migration_errors:
                error_msg = '; '.join(migration_errors)
                raise RuntimeError(f'模块 {module_id} 安装失败: {error_msg}')
        
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
        success = ModuleService.install_module(module.module_id)
        if not success:
            raise RuntimeError(f"模块 {module.module_id} 安装失败")
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