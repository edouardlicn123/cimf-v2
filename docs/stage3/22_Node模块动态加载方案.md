# Node 模块动态加载方案

> 状态：规划中  
> 版本：1.0

---

## 一、目标

实现一个完全动态的 Node 模块系统：
1. 系统启动不依赖任何 node 模块
2. 模块在初始化时动态扫描、安装
3. 模块可通过"列表加载"和"安装"操作管理

---

## 二、核心概念

### 2.1 模块状态定义

| 状态 | 定义 | 字段 |
|------|------|------|
| 不存在 | 模块目录不存在，不是系统管理的范围 | - |
| 未安装 | 目录存在 + 已写入 NodeModule + 未完成数据库结构操作 | `is_installed=False` |
| 已安装 | 目录存在 + 已完成数据库结构操作 | `is_installed=True` |
| 启用 | 系统加载并应用模块的全部功能 | `is_active=True` |
| 禁用 | 系统不加载该模块 | `is_active=False` |

### 2.2 操作定义

| 操作 | 说明 |
|------|------|
| 列表加载 | 扫描 nodes/ 目录下所有 module.py，与 NodeModule 表对比，写入/更新/删除记录 |
| 安装 | 执行数据库结构操作（migrate、同步 NodeType），标记为已安装 |
| 启用 | 设置 is_active=True，系统加载模块功能 |
| 禁用 | 设置 is_active=False，系统不加载模块功能 |

---

## 三、流程设计

### 3.1 完整流程

```
┌─────────────────────────────────────────────────────────────┐
│                      系统初始化/启动                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. 列表加载                                                 │
│     - 扫描 nodes/ 目录下所有 module.py                       │
│     - 对比 NodeModule 表                                    │
│     - 新模块写入 NodeModule（is_installed=False）          │
│     - 已存在则更新信息                                      │
│     - 扫描不到 + 数据库有记录 → 删除记录（模块不存在）       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 安装（完成数据库结构操作）                                 │
│     - 遍历已加载的模块                                       │
│     - 未安装则：                                             │
│       * 动态注册应用（临时添加到 apps）                       │
│       * 执行 makemigrations + migrate                        │
│       * 同步创建 NodeType                                    │
│       * 标记 is_installed=True                               │
│     - 已安装则跳过                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 启用/禁用                                                │
│     - 启用：is_active=True，模块功能可访问                   │
│     - 禁用：is_active=False，模块功能不可访问                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 手动触发场景

| 场景 | 操作 |
|------|------|
| 首次初始化 | 列表加载 + 安装（自动执行） |
| 检查模块 | 列表加载 + 安装未安装的模块 |
| 启用模块 | 安装（已安装则跳过）+ 设置 is_active=True |
| 禁用模块 | 设置 is_active=False |

---

## 四、技术实现

### 4.1 修改 settings.py

移除 INSTALLED_APPS 中的硬编码模块：

```python
# cimf_django/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'nodes',
    # 移除硬编码的模块：
    # 'nodes.customer',
    # 'nodes.customer_cn',
]
```

### 4.2 修改 nodes/urls.py

使用通配符路由替代硬编码路由：

```python
# nodes/urls.py

from django.urls import path, include
from . import views

app_name = 'nodes'

urlpatterns = [
    # 首页
    path('', views.nodes_index, name='index'),
    
    # 模块管理
    path('modules/', views.node_modules, name='modules'),
    path('modules/scan/', views.module_scan, name='module_scan'),
    path('modules/install/<str:module_id>/', views.module_install, name='module_install'),
    path('modules/enable/<str:module_id>/', views.module_enable, name='module_enable'),
    path('modules/disable/<str:module_id>/', views.module_disable, name='module_disable'),
    
    # 节点类型管理
    path('types/', views.node_types, name='node_types'),
    path('type/create/', views.node_type_create, name='node_type_create'),
    path('type/<int:node_type_id>/edit/', views.node_type_edit, name='node_type_edit'),
    path('type/<int:node_type_id>/delete/', views.node_type_delete, name='node_type_delete'),
    path('type/<int:node_type_id>/toggle/', views.node_type_toggle, name='node_type_toggle'),
    
    # 通配符路由 - 动态模块分发
    path('<slug:module_slug>/', views.module_dispatch, name='module_dispatch'),
    path('<slug:module_slug>/create/', views.module_dispatch, name='module_create'),
    path('<slug:module_slug>/<int:node_id>/', views.module_dispatch, name='module_view'),
    path('<slug:module_slug>/<int:node_id>/edit/', views.module_dispatch, name='module_edit'),
    path('<slug:module_slug>/<int:node_id>/delete/', views.module_dispatch, name='module_delete'),
]
```

### 4.3 模块视图分发

根据 module.py 配置动态调用视图：

```python
# nodes/views.py

def module_dispatch(request, module_slug, node_id=None):
    """模块视图分发"""
    from core.node.models import NodeModule
    import importlib.util
    
    # 1. 检查模块是否已安装且启用
    module = NodeModule.objects.filter(
        module_id=module_slug,
        is_installed=True,
        is_active=True
    ).first()
    
    if not module:
        raise Http404('模块不存在或未启用')
    
    # 2. 读取模块配置
    module_info = NodeModuleService._load_module_info(module_slug)
    if not module_info:
        raise Http404('模块配置无效')
    
    # 3. 确定要调用的视图函数
    view_config = module_info.get('views', {})
    
    # 根据请求路径确定要调用的函数名
    if 'create' in request.path:
        view_func_name = view_config.get('create')
    elif node_id:
        if 'edit' in request.path:
            view_func_name = view_config.get('edit')
        elif 'delete' in request.path:
            view_func_name = view_config.get('delete')
        else:
            view_func_name = view_config.get('view')
    else:
        view_func_name = view_config.get('list')
    
    if not view_func_name:
        raise Http404('模块未配置视图函数')
    
    # 4. 动态导入并调用视图
    try:
        module_views = importlib.import_module(f'nodes.{module_slug}.views')
        view_func = getattr(module_views, view_func_name)
        return view_func(request, node_id=node_id) if node_id else view_func(request)
    except (ImportError, AttributeError) as e:
        raise Http404(f'模块视图函数不存在: {e}')
```

### 4.4 module.py 配置示例

```python
# nodes/customer/module.py

MODULE_INFO = {
    'id': 'customer',
    'name': '客户信息（海外）',
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
    return None

def get_uninstall_sql():
    return None
```

### 4.5 动态注册应用并执行迁移

```python
# core/node/services.py

class NodeModuleService:
    """Node 模块服务"""
    
    @staticmethod
    def install_module(module_id: str) -> bool:
        """安装模块 - 动态注册应用并执行迁移"""
        from django.apps import apps
        from django.core.management import call_command
        import os
        
        module = NodeModule.objects.filter(module_id=module_id).first()
        if not module:
            return False
        
        # 检查是否已安装
        if module.is_installed:
            return True
        
        # 检查模块目录是否存在
        module_path = f'nodes/{module_id}'
        if not os.path.exists(module_path):
            return False
        
        # 检查 migrations 目录是否存在
        migrations_path = f'{module_path}/migrations'
        if os.path.exists(migrations_path):
            # 动态注册应用
            try:
                # 检查应用是否已注册
                app_config = apps.get_app_config(f'nodes.{module_id}')
            except LookupError:
                # 动态创建 AppConfig
                from django.apps import AppConfig
                app_name = f'nodes.{module_id}'
                app_path = os.path.join(os.getcwd(), module_path)
                
                # 创建临时 AppConfig
                app_config = AppConfig.create(app_name)
                apps.app_registry.populate([app_config])
            
            # 执行 makemigrations
            try:
                call_command('makemigrations', module_id, verbosity=0)
            except Exception:
                pass  # 忽略错误，可能已存在
            
            # 执行 migrate
            try:
                call_command('migrate', module_id, verbosity=0)
            except Exception:
                pass  # 忽略错误，可能已存在
        
        # 同步 NodeType
        NodeModuleService.sync_node_type(module)
        
        # 标记为已安装
        module.is_installed = True
        module.save()
        
        return True
```

---

## 五、涉及文件清单

| 文件 | 变更说明 |
|------|----------|
| `cimf_django/settings.py` | 移除 INSTALLED_APPS 中的硬编码模块 |
| `nodes/urls.py` | 添加通配符路由，移除硬编码路由 |
| `nodes/views.py` | 添加模块视图分发函数 |
| `core/node/services.py` | 修改列表加载和安装逻辑 |
| `core/node/models.py` | NodeModule 模型（已存在） |
| `init_db.py` | 修改初始化流程，同时执行列表加载+安装 |

---

## 六、实施顺序

1. 修改 `cimf_django/settings.py` - 移除硬编码模块
2. 修改 `nodes/urls.py` - 添加通配符路由
3. 修改 `nodes/views.py` - 实现模块视图分发
4. 修改 `core/node/services.py` - 完善列表加载和安装逻辑
5. 修改 `init_db.py` - 更新初始化流程
6. 更新模块管理页面
7. 更新技术规范文档

---

## 七、注意事项

1. **视图函数命名**：每个模块需要在 module.py 中配置 views 映射
2. **模块独立性**：模块的 models、views、services 保持独立目录结构
3. **迁移处理**：动态注册应用后，Django 会自动发现 migrations 目录
4. **错误处理**：安装失败时需要回滚状态

---

*文档创建：2026-03-25*  
*版本：1.0*