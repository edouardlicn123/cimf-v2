# Node 模块技术规范

本文档定义 cimf-v2（仙芙CIMF）项目的 Node 节点类型系统技术规范，包含节点模型、服务层、视图、模板和权限控制的完整实现指引。

> **重要**：Node 系统采用 **模块化设计**，每个节点类型对应一个模块。模块信息通过 `module.py` 文件定义，并通过 `NodeModule` 注册表统一管理。

## 架构说明

项目采用「主应用 + 子应用」模式组织节点模块：

```
nodes/                          # 节点主应用
├── models.py                   # 公共模型（NodeType, Node, NodeModule）
├── views.py                    # 通用视图
├── urls.py                    # 通用路由
└── services/                  # 公共服务层
    ├── node_type_service.py   # 节点类型服务
    ├── node_service.py        # 节点主表服务
    └── node_module_service.py # 模块管理服务

nodes/customer/                # 海外客户子应用（nodes.customer）
├── module.py                  # 必选：模块信息文件
├── models.py                  # CustomerFields 模型
├── views.py                   # 客户视图
├── urls.py                    # 路由配置
├── services.py                # 客户服务
└── templates/                 # 客户模板

nodes/customer_cn/             # 国内客户子应用（nodes.customer_cn）
├── module.py                  # 必选：模块信息文件
├── models.py                  # CustomerCnFields 模型
├── views.py                   # 客户视图
├── urls.py                    # 路由配置
├── services.py                # 客户服务
└── templates/                 # 客户模板
```

> **说明**：节点子应用作为独立 Django 应用注册到 `INSTALLED_APPS`，便于权限管理和代码隔离。

---

## 一、概述

Node 系统是一个灵活的节点类型管理框架，允许通过管理界面创建各种业务节点类型，每个节点类型可以配置不同的字段。

### 1.1 两种初始化方式的区别

Node 系统支持两种初始化方式：

| 方式 | 数据来源 | 管理方式 | 状态 |
|------|----------|----------|------|
| 模块化（推荐） | `module.py` + `NodeModule` | 数据库注册表 | 启用 |
| 旧配置（已废弃） | `DEFAULT_NODE_TYPES` | 代码硬编码 | 不推荐 |

**推荐方式**：每个节点类型通过 `module.py` 定义模块信息，然后通过"检查模块"功能扫描并注册到 `NodeModule` 表。

### 1.2 目录结构

```
nodes/                           # 节点应用
├── models.py                    # 节点模型（NodeType, Node, {Node}Fields）
├── views.py                    # 视图函数
├── urls.py                     # URL 路由配置
├── apps.py                     # 应用配置
└── services/                   # 服务层
    ├── __init__.py
    ├── node_type_service.py   # 节点类型服务
    ├── node_service.py         # 节点主表服务
    └── {node_slug}_service.py  # 节点专用服务（如 customer_service.py）

templates/
└── nodes/                     # 节点模板
    ├── types/                 # 节点类型管理
    │   ├── index.html
    │   └── edit.html
    ├── customer/              # 客户（海外版）
    │   ├── list.html
    │   ├── view.html
    │   └── edit.html
    ├── customer_cn/           # 客户（国内版）
    │   ├── list.html
    │   ├── view.html
    │   └── edit.html
    └── field_types.html        # 字段类型列表
```

### 1.2 菜单入口约定

**一般情况下，模块功能的入口放置在 `frame_node` 菜单上。**

- 所有节点类型的列表页默认使用 `frame_node.html` 作为基础模板
- 菜单入口由系统根据已启用的节点类型自动生成
- 每个节点类型对应一个菜单项，点击后进入该类型的节点列表页

---

## 二、核心模型

### 2.1 节点类型模型（NodeType）

```python
# nodes/models.py
class NodeType(models.Model):
    """节点类型模型"""
    
    name = models.CharField(max_length=100, verbose_name='节点类型名称')
    slug = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='标识符')
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name='描述')
    icon = models.CharField(max_length=50, default='bi-folder', verbose_name='图标')
    fields_config = models.JSONField(default=list, verbose_name='字段配置')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'node_types'
        verbose_name = '节点类型'
        verbose_name_plural = '节点类型'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_node_count(self):
        return self.nodes.count()
```

### 2.2 节点主表模型（Node）

```python
# nodes/models.py
class Node(models.Model):
    """节点主表 - 所有节点类型的公共字段"""
    
    node_type = models.ForeignKey(
        NodeType,
        on_delete=models.CASCADE,
        related_name='nodes',
        verbose_name='节点类型'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_nodes',
        verbose_name='创建人'
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_nodes',
        verbose_name='更新人'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'nodes'
        verbose_name = '节点'
        verbose_name_plural = '节点'
        ordering = ['-created_at']
```

### 2.3 节点字段模型（{Node}Fields）

每个节点类型必须创建自己的字段模型，示例：

```python
# nodes/models.py
class CustomerFields(models.Model):
    """客户节点字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='customer_fields',
        verbose_name='关联节点'
    )
    
    # 基本信息
    customer_name = models.CharField(max_length=200, unique=True, verbose_name='客户名称')
    customer_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='客户代码')
    
    # 联系方式
    phone1 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话1')
    email1 = models.EmailField(blank=True, null=True, verbose_name='邮箱1')
    
    # 地址信息
    country = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='country_customers',
        verbose_name='国家'
    )
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='省份/城市')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='详细地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='邮政编码')
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'customer_fields'
        verbose_name = '客户'
        verbose_name_plural = '客户'
    
    @property
    def creator(self):
        """获取创建人（从关联的 Node 获取）"""
        return self.node.created_by if hasattr(self, 'node') and self.node else None
    
    def __str__(self):
        return self.customer_name
```

---

## 三、系统预定义字段类型

创建 Node 类型时，除非需要自定义字段类型，否则**必须**从以下系统预定义字段类型中选择：

| 机器名 | 标签 | 内部属性 |
|--------|------|----------|
| string | 单行文本 | value |
| string_long | 多行纯文本 | value |
| text | 带格式文本 | value, format |
| text_long | 带格式长文本 | value, format |
| text_with_summary | 含摘要文本 | value, summary, format |
| boolean | 布尔值 | value |
| integer | 整数 | value |
| decimal | 精确小数 | value |
| float | 浮点数 | value |
| entity_reference | 关联引用 | target_id, target_type |
| file | 文件 | target_id, display, description |
| image | 图片 | target_id, alt, title, width, height |
| link | 链接 | uri, title, options |
| email | 邮箱 | value |
| telephone | 电话 | value |
| datetime | 日期时间 | value |
| timestamp | 时间戳 | value |
| geolocation | 地理位置 | lat, lng, address |
| color | 颜色选择器 | color_code, opacity |
| ai_tags | 智能标签 | term_id, confidence_score |
| identity | 证件识别码 | id_number, id_type, is_verified |
| masked | 隐私脱敏字段 | raw_value, display_value, permission_level |
| biometric | 生物特征引用 | feature_vector, type, version |
| address | 标准地址 | province, city, district, street, house_number, grid_id |
| gis | 地理围栏 | point, spatial_ref |

---

## 四、服务层

### 4.1 节点类型服务（NodeTypeService）

```python
# core/node/services.py
from typing import List, Optional, Dict, Any
from core.node.models import NodeType

# 注意：DEFAULT_NODE_TYPES 配置已废弃，请使用 NodeModule 模块系统


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
    def create(data: Dict[str, Any]) -> NodeType:
        """创建节点类型"""
        return NodeType.objects.create(**data)
    
    @staticmethod
    def update(node_type_id: int, data: Dict[str, Any]) -> Optional[NodeType]:
        """更新节点类型"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            for key, value in data.items():
                setattr(node_type, key, value)
            node_type.save()
        return node_type
    
    @staticmethod
    def delete(node_type_id: int) -> bool:
        """删除节点类型"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.delete()
            return True
        return False
    
    @staticmethod
    def toggle_active(node_type_id: int) -> Optional[NodeType]:
        """切换启用状态"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = not node_type.is_active
            node_type.save()
        return node_type
```

### 4.2 节点主表服务（NodeService）

```python
# nodes/services/node_service.py
from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from nodes.models import Node, NodeType

User = get_user_model()


class NodeService:
    """节点主表服务"""
    
    @staticmethod
    def get_list(node_type_slug: str, search: Optional[str] = None) -> List[Node]:
        """获取节点列表"""
        node_type = NodeTypeService.get_by_slug(node_type_slug)
        if not node_type:
            return []
        
        queryset = Node.objects.filter(node_type=node_type)
        
        if search:
            queryset = queryset.filter(id__icontains=search)
        
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
```

### 4.3 节点专用服务（{Node}Service）

```python
# nodes/services/customer_service.py
from typing import List, Optional, Dict, Any
import random
import string
from django.contrib.auth import get_user_model
from nodes.models import Node, CustomerFields
from nodes.services import NodeService

User = get_user_model()


class CustomerService:
    """客户管理服务"""
    
    @staticmethod
    def get_list(search: Optional[str] = None) -> List[CustomerFields]:
        """获取客户列表"""
        queryset = CustomerFields.objects.all()
        
        if search:
            queryset = queryset.filter(
                customer_name__icontains=search
            ) | queryset.filter(
                enterprise_name__icontains=search
            )
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(customer_id: int) -> Optional[CustomerFields]:
        """根据 ID 获取客户"""
        return CustomerFields.objects.filter(id=customer_id).first()
    
    @staticmethod
    def get_by_node_id(node_id: int) -> Optional[CustomerFields]:
        """根据节点 ID 获取客户"""
        return CustomerFields.objects.filter(node_id=node_id).first()
    
    @staticmethod
    def create(user, data: Dict[str, Any]) -> CustomerFields:
        """创建客户"""
        node = NodeService.create('customer', user, {})
        
        # 自动生成客户代码
        customer_code = data.get('customer_code')
        if not customer_code:
            customer_code = 'CC' + ''.join(random.choices(string.digits, k=6))
        
        customer = CustomerFields.objects.create(
            node=node,
            customer_name=data.get('customer_name', ''),
            customer_code=customer_code,
            # ... 其他字段
        )
        
        return customer
    
    @staticmethod
    def update(customer_id: int, user, data: Dict[str, Any]) -> Optional[CustomerFields]:
        """更新客户"""
        customer = CustomerFields.objects.filter(id=customer_id).first()
        if not customer:
            return None
        
        # 更新 Node 的 updated_by
        NodeService.update(customer.node_id, user, {})
        
        # 更新字段
        for key, value in data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        customer.save()
        
        return customer
    
    @staticmethod
    def delete(customer_id: int) -> bool:
        """删除客户"""
        customer = CustomerFields.objects.filter(id=customer_id).first()
        if customer:
            node_id = customer.node_id
            customer.delete()
            NodeService.delete(node_id)
            return True
        return False
```

---

## 五、视图层

### 5.1 节点类型管理视图

```python
# nodes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from nodes.models import NodeType, Node, CustomerFields
from nodes.services import NodeTypeService, NodeService, CustomerService
from core.services import PermissionService


@login_required
def node_types(request):
    """节点类型列表"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    node_types = NodeTypeService.get_all_including_inactive()
    return render(request, 'nodes/types/index.html', {
        'node_types': node_types,
        'active_section': 'node_types',
    })


@login_required
def node_type_create(request):
    """创建节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        icon = request.POST.get('icon', 'bi-folder').strip()
        
        NodeTypeService.create({
            'name': name,
            'slug': slug,
            'description': description,
            'icon': icon,
        })
        messages.success(request, '节点类型创建成功')
        return redirect('nodes:node_types')
    
    return render(request, 'nodes/types/edit.html', {
        'node_type': None,
        'active_section': 'node_types',
    })


@login_required
def node_type_edit(request, node_type_id: int):
    """编辑节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    node_type = get_object_or_404(NodeType, id=node_type_id)
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', '').strip(),
            'slug': request.POST.get('slug', '').strip(),
            'description': request.POST.get('description', '').strip(),
            'icon': request.POST.get('icon', 'bi-folder').strip(),
        }
        NodeTypeService.update(node_type_id, data)
        messages.success(request, '节点类型更新成功')
        return redirect('nodes:node_types')
    
    return render(request, 'nodes/types/edit.html', {
        'node_type': node_type,
        'active_section': 'node_types',
    })


@login_required
def node_type_delete(request, node_type_id: int):
    """删除节点类型"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    NodeTypeService.delete(node_type_id)
    messages.success(request, '节点类型已删除')
    return redirect('nodes:node_types')


@login_required
def node_type_toggle(request, node_type_id: int):
    """切换节点类型启用状态"""
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    node_type = NodeTypeService.toggle_active(node_type_id)
    if node_type:
        status = '启用' if node_type.is_active else '禁用'
        messages.success(request, f'节点类型已{status}')
    return redirect('nodes:node_types')
```

### 5.2 节点 CRUD 视图

```python
# nodes/views.py
@login_required
def node_list(request, node_type_slug: str):
    """节点列表"""
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        raise Http404('节点类型不存在')
    
    search = request.GET.get('search', '')
    node_types = NodeTypeService.get_all()
    
    # 特定节点类型的处理
    if node_type_slug == 'customer':
        customers = CustomerService.get_list(search if search else None)
        return render(request, 'nodes/customer/list.html', {
            'node_type': node_type,
            'node_types': node_types,
            'customers': customers,
            'search': search,
            'active_section': node_type_slug,
        })
    
    # 通用节点列表
    nodes = NodeService.get_list(node_type_slug, search if search else None)
    return render(request, 'nodes/list.html', {
        'node_type': node_type,
        'node_types': node_types,
        'nodes': nodes,
        'search': search,
        'active_section': node_type_slug,
    })


@login_required
def node_create(request, node_type_slug: str):
    """创建节点"""
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        raise Http404('节点类型不存在')
    
    node_types = NodeTypeService.get_all()
    
    # 特定节点类型的处理
    if node_type_slug == 'customer':
        # 获取词汇表选项
        from core.services import TaxonomyService
        # ... 获取选项数据
        
        if request.method == 'POST':
            data = {
                'customer_name': request.POST.get('customer_name', '').strip(),
                'customer_code': request.POST.get('customer_code', '').strip() or None,
                # ... 其他字段
            }
            
            try:
                CustomerService.create(request.user, data)
                messages.success(request, '客户创建成功')
                return redirect('nodes:node_list', node_type_slug=node_type_slug)
            except Exception as e:
                messages.error(request, str(e))
        
        return render(request, 'nodes/customer/edit.html', {
            'node_type': node_type,
            'node_types': node_types,
            'customer': None,
            'active_section': node_type_slug,
            # ... 选项数据
        })
    
    # 通用节点创建
    return render(request, 'nodes/edit.html', {
        'node_type': node_type,
        'node_types': node_types,
        'node': None,
        'active_section': node_type_slug,
    })


@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """查看节点"""
    node = NodeService.get_by_id(node_id)
    if not node:
        raise Http404('节点不存在')
    
    # 权限检查（特定节点类型）
    if node_type_slug == 'customer':
        has_perm, error_msg = check_customer_permission(request.user, node, 'view')
        if not has_perm:
            messages.error(request, error_msg)
            return redirect('nodes:node_list', node_type_slug=node_type_slug)
    
    node_types = NodeTypeService.get_all()
    
    # 特定节点类型的处理
    if node_type_slug == 'customer':
        customer = CustomerService.get_by_node_id(node_id)
        return render(request, 'nodes/customer/view.html', {
            'node_type': node.node_type,
            'node_types': node_types,
            'node': node,
            'customer': customer,
            'active_section': node_type_slug,
        })
    
    return render(request, 'nodes/view.html', {
        'node_type': node.node_type,
        'node_types': node_types,
        'node': node,
        'active_section': node_type_slug,
    })


@login_required
def node_edit(request, node_type_slug: str, node_id: int):
    """编辑节点"""
    node = NodeService.get_by_id(node_id)
    if not node:
        raise Http404('节点不存在')
    
    # 权限检查（特定节点类型）
    if node_type_slug == 'customer':
        has_perm, error_msg = check_customer_permission(request.user, node, 'edit')
        if not has_perm:
            messages.error(request, error_msg)
            return redirect('nodes:node_list', node_type_slug=node_type_slug)
    
    node_types = NodeTypeService.get_all()
    
    # 特定节点类型的处理
    if node_type_slug == 'customer':
        customer = CustomerService.get_by_node_id(node_id)
        # ... 获取选项数据
        
        if request.method == 'POST':
            data = {
                'customer_name': request.POST.get('customer_name', '').strip(),
                # ... 其他字段
            }
            
            try:
                CustomerService.update(customer.id, request.user, data)
                messages.success(request, '客户更新成功')
                return redirect('nodes:node_view', node_type_slug=node_type_slug, node_id=node_id)
            except Exception as e:
                messages.error(request, str(e))
        
        return render(request, 'nodes/customer/edit.html', {
            'node_type': node.node_type,
            'node_types': node_types,
            'customer': customer,
            'active_section': node_type_slug,
            # ... 选项数据
        })
    
    return render(request, 'nodes/edit.html', {
        'node_type': node.node_type,
        'node_types': node_types,
        'node': node,
        'active_section': node_type_slug,
    })


@login_required
def node_delete(request, node_type_slug: str, node_id: int):
    """删除节点"""
    # 权限检查（特定节点类型）
    if node_type_slug == 'customer':
        node = NodeService.get_by_id(node_id)
        if node:
            has_perm, error_msg = check_customer_permission(request.user, node, 'delete')
            if not has_perm:
                messages.error(request, error_msg)
                return redirect('nodes:node_list', node_type_slug=node_type_slug)
            
            customer = CustomerService.get_by_node_id(node_id)
            if customer:
                CustomerService.delete(customer.id)
                messages.success(request, '客户已删除')
    
    return redirect('nodes:node_list', node_type_slug=node_type_slug)
```

---

## 六、路由设计

### 6.1 节点管理路由

| 路径 | 函数 | 说明 |
|------|------|------|
| `/nodes/` | `nodes:index` | 事务总览 |
| `/nodes/types/` | `nodes:node_types` | 节点类型列表 |
| `/nodes/type/create/` | `nodes:node_type_create` | 创建节点类型 |
| `/nodes/type/<id>/edit/` | `nodes:node_type_edit` | 编辑节点类型 |
| `/nodes/type/<id>/delete/` | `nodes:node_type_delete` | 删除节点类型 |
| `/nodes/type/<id>/toggle/` | `nodes:node_type_toggle` | 切换启用状态 |
| `/nodes/field-types/` | `nodes:field_types` | 字段类型列表 |
| `/nodes/<slug>/` | `nodes:node_list` | 节点列表 |
| `/nodes/<slug>/create/` | `nodes:node_create` | 创建节点 |
| `/nodes/<slug>/<id>/` | `nodes:node_view` | 查看节点 |
| `/nodes/<slug>/<id>/edit/` | `nodes:node_edit` | 编辑节点 |
| `/nodes/<slug>/<id>/delete/` | `nodes:node_delete` | 删除节点 |

### 6.2 导入导出路由

| 路径 | 函数 | 说明 |
|------|------|------|
| `/nodes/export/` | `nodes:export_list` | 导出列表 |
| `/nodes/export/<slug>/` | `nodes:export_select_fields` | 选择导出字段 |
| `/nodes/export/<slug>/confirm/` | `nodes:export_confirm` | 确认导出 |
| `/nodes/export/<slug>/exporting/` | `nodes:export_exporting` | 执行导出 |
| `/nodes/export/<slug>/do/` | `nodes:do_export` | 下载导出文件 |
| `/nodes/import/` | `nodes:import_list` | 导入列表 |
| `/nodes/import/<slug>/` | `nodes:import_page` | 导入页面 |
| `/nodes/import/<slug>/template/` | `nodes:download_template` | 下载模板 |
| `/nodes/import/<slug>/upload/` | `nodes:upload_preview` | 上传预览 |
| `/nodes/import/<slug>/do/` | `nodes:do_import` | 执行导入 |
| `/nodes/import/<slug>/errors/` | `nodes:download_errors` | 下载错误报告 |

### 6.3 API 路由

| 路径 | 函数 | 说明 |
|------|------|------|
| `/nodes/api/field-types/` | `nodes:field_types_api` | 字段类型 API |
| `/nodes/api/taxonomy-items/` | `nodes:taxonomy_items_api` | 词汇表自动补全 |

> **注意**：URL 中的 `<slug>` 是节点类型的标识符，`<id>` 是节点的主键（Node.id）。

---

## 七、模板规范

### 7.1 列表页模板

```html
{% extends "core/frames/frame_node.html" %}

{% set show_nav = true %}
{% set show_header = false %}

{% block admin_title %}{{ node_type.name }}{% endblock %}

{% block admin_title_buttons %}
<a href="{{ url('nodes:node_create', node_type.slug) }}" class="btn btn-primary">
    <i class="bi bi-plus-lg"></i> 新建
</a>
{% endblock %}

{% block admin_content %}
<div class="row">
    <div class="col-12">
        <!-- 搜索表单 -->
        <div class="card mb-4">
            <div class="card-body">
                <form method="get" class="row g-3">
                    <div class="col-md-4">
                        <label class="form-label small text-muted">关键词</label>
                        <input type="text" name="search" class="form-control" placeholder="搜索..." value="{{ search|default('') }}">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small text-muted">客户类型</label>
                        <select name="customer_type" class="form-select">
                            <option value="">全部</option>
                            {% for item in customer_types %}
                            <option value="{{ item.id }}" {% if filter_customer_type == item.id|string %}selected{% endif %}>{{ item.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-2 d-flex align-items-end">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-search"></i> 搜索
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- 数据列表 -->
        <div class="card">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr>
                            <th>客户名称</th>
                            <th>客户代码</th>
                            <th>创建时间</th>
                            <th style="width: 150px;">操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for customer in customers %}
                        <tr>
                            <td>
                                <a href="{{ url('nodes:node_view', node_type.slug, customer.node_id) }}">
                                    {{ customer.customer_name|default('-') }}
                                </a>
                            </td>
                            <td><code>{{ customer.customer_code|default('-') }}</code></td>
                            <td>{{ customer.created_at|date("Y-m-d") }}</td>
                            <td>
                                <a href="{{ url('nodes:node_view', node_type.slug, customer.node_id) }}" class="btn btn-sm btn-outline-primary">查看</a>
                                <a href="{{ url('nodes:node_edit', node_type.slug, customer.node_id) }}" class="btn btn-sm btn-outline-secondary">编辑</a>
                                <a href="{{ url('nodes:node_delete', node_type.slug, customer.node_id) }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定删除?')">删除</a>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="4" class="text-center text-muted">暂无数据</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 7.2 编辑页模板

```html
{% extends "core/frames/frame_node.html" %}

{% set show_nav = true %}
{% set show_header = false %}

{% block admin_title %}{% if customer %}编辑{% else %}新建{% endif %}{{ node_type.name }}{% endblock %}

{% block admin_content %}
<form method="post">
    {{ csrf_token }}
    
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label">客户名称 *</label>
            <input type="text" name="customer_name" class="form-control" value="{{ customer.customer_name|default('') if customer else '' }}" required>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label">客户代码</label>
            <input type="text" name="customer_code" class="form-control" value="{{ customer.customer_code|default('') if customer else '' }}">
            <small class="text-muted">留空将自动生成</small>
        </div>
    </div>
    
    <!-- 其他字段... -->
    
    <div class="text-end">
        <a href="{{ url('nodes:node_list', node_type.slug) }}" class="btn btn-secondary">取消</a>
        <button type="submit" class="btn btn-primary">保存</button>
    </div>
</form>
{% endblock %}
```

---

## 八、权限控制

### 8.1 权限类型

Node 模块支持两类权限：

1. **基础权限** - 所有节点类型
   - `node.{slug}.create` - 创建
   - `node.{slug}.read` - 查看
   - `node.{slug}.update` - 修改
   - `node.{slug}.delete` - 删除

2. **扩展权限** - 特定节点类型（如 customer）
   - `node.{slug}.view_others` - 查看别人的内容
   - `node.{slug}.edit_others` - 修改别人的内容
   - `node.{slug}.delete_others` - 删除别人的内容

### 8.2 权限检查函数

```python
# nodes/views.py

def check_customer_permission(user, node, permission_type: str) -> tuple:
    """
    检查客户节点操作权限
    
    返回: (has_permission: bool, error_message: str)
    - 如果是创建者，有权限
    - 如果有对应权限，有权限
    - 否则无权限
    """
    if user.is_admin:
        return True, None
    
    is_creator = node.created_by_id == user.id
    
    if is_creator:
        return True, None
    
    perm_map = {
        'view': 'node.customer.view_others',
        'edit': 'node.customer.edit_others',
        'delete': 'node.customer.delete_others',
    }
    
    perm = perm_map.get(permission_type)
    if perm and PermissionService.has_permission(user, perm):
        return True, None
    
    return False, f'您没有权限{permission_type}别人的客户信息'
```

### 8.3 权限服务扩展

在 `PermissionService.get_node_permissions()` 中为特定节点添加扩展权限：

```python
# core/services/permission_service.py

@staticmethod
def get_node_permissions() -> Dict[str, Dict]:
    """获取节点权限，按节点类型分组"""
    from nodes.models import NodeType
    
    node_permissions = {}
    active_types = NodeType.objects.filter(is_active=True)
    
    for node_type in active_types:
        perms = [
            (f'node.{node_type.slug}.create', f'{node_type.name} - 创建'),
            (f'node.{node_type.slug}.read', f'{node_type.name} - 查看'),
            (f'node.{node_type.slug}.update', f'{node_type.name} - 修改'),
            (f'node.{node_type.slug}.delete', f'{node_type.name} - 删除'),
        ]
        
        # 为特定节点添加扩展权限
        if node_type.slug == 'customer':
            perms.extend([
                (f'node.{node_type.slug}.view_others', f'{node_type.name} - 查看别人的内容'),
                (f'node.{node_type.slug}.edit_others', f'{node_type.name} - 修改别人的内容'),
                (f'node.{node_type.slug}.delete_others', f'{node_type.name} - 删除别人的内容'),
            ])
        
        node_permissions[node_type.slug] = {
            'name': node_type.name,
            'icon': node_type.icon or 'bi-folder',
            'permissions': perms
        }
    
    return node_permissions
```

### 8.4 权限检查流程

```
用户操作节点
    │
    ▼
检查 is_admin（管理员直接放行）
    │
    ├── 是 → 允许操作
    │
    ▼ 否
检查是否是创建者
    │
    ├── 是 → 允许操作
    │
    ▼ 否
检查是否有对应权限
    │
    ├── 有 → 允许操作
    │
    ▼ 无
拒绝操作，返回错误消息
```

---

## 九、自动生成代码

### 9.1 DEFAULT_NODE_TYPES 配置模板

```python
DEFAULT_NODE_TYPES = [
    {
        'name': '{节点显示名称}',
        'slug': '{slug}',
        'description': '{描述}',
        'icon': 'bi-{图标}',
        'fields_config': [
            {'field_type': 'string', 'name': '{field_name}', 'label': '{字段标签}', 'required': True/False},
            # ... 其他字段
        ],
        'is_active': True,
    },
]
```

### 9.2 节点字段模型模板

```python
class {Node}Fields(models.Model):
    """{节点名称}字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='{slug}_fields',
        verbose_name='关联节点'
    )
    
    # ===== 基本信息 =====
    {field_name} = models.CharField(max_length=200, unique=True, verbose_name='{字段名称}')
    
    # ... 其他字段
    
    # ===== 时间字段 =====
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = '{slug}_fields'
        verbose_name = '{节点名称}'
        verbose_name_plural = '{节点名称}'
    
    def __str__(self):
        return self.{field_name}
```

### 9.3 Service 类模板

```python
class {Node}Service:
    """{节点名称}服务"""
    
    @staticmethod
    def get_list(search: Optional[str] = None) -> List[{Node}Fields]:
        """获取列表"""
        queryset = {Node}Fields.objects.all()
        
        if search:
            queryset = queryset.filter(
                {search_field}__icontains=search
            )
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id({id_name}: int) -> Optional[{Node}Fields]:
        """根据 ID 获取"""
        return {Node}Fields.objects.filter(id={id_name}).first()
    
    @staticmethod
    def get_by_node_id(node_id: int) -> Optional[{Node}Fields]:
        """根据节点 ID 获取"""
        return {Node}Fields.objects.filter(node_id=node_id).first()
    
    @staticmethod
    def create(user, data: Dict[str, Any]) -> {Node}Fields:
        """创建"""
        node = NodeService.create('{slug}', user, {})
        return {Node}Fields.objects.create(node=node, **data)
    
    @staticmethod
    def update({id_name}: int, user, data: Dict[str, Any]) -> Optional[{Node}Fields]:
        """更新"""
        {node} = {Node}Fields.objects.filter(id={id_name}).first()
        if {node}:
            NodeService.update({node}.node_id, user, {})
            for key, value in data.items():
                if hasattr({node}, key):
                    setattr({node}, key, value)
            {node}.save()
        return {node}
    
    @staticmethod
    def delete({id_name}: int) -> bool:
        """删除"""
        {node} = {Node}Fields.objects.filter(id={id_name}).first()
        if {node}:
            node_id = {node}.node_id
            {node}.delete()
            NodeService.delete(node_id)
            return True
        return False
```

### 9.4 权限检查函数模板

```python
def check_{slug}_permission(user, node, permission_type: str) -> tuple:
    """
    检查{节点名称}节点操作权限
    
    返回: (has_permission: bool, error_message: str)
    """
    if user.is_admin:
        return True, None
    
    is_creator = node.created_by_id == user.id
    
    if is_creator:
        return True, None
    
    perm_map = {
        'view': 'node.{slug}.view_others',
        'edit': 'node.{slug}.edit_others',
        'delete': 'node.{slug}.delete_others',
    }
    
    perm = perm_map.get(permission_type)
    if perm and PermissionService.has_permission(user, perm):
        return True, None
    
    return False, f'您没有权限{permission_type}别人的{节点名称}'
```

---

## 十、代码示例

### 10.1 完整的 CustomerFields 实现

```python
# nodes/models.py
class CustomerFields(models.Model):
    """客户节点字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='customer_fields',
        verbose_name='关联节点'
    )
    
    # ===== 基本信息 =====
    customer_name = models.CharField(max_length=200, unique=True, verbose_name='客户名称')
    customer_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='客户代码')
    customer_type = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_type_customers',
        verbose_name='客户类型'
    )
    enterprise_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='企业名称')
    
    # ===== 联系方式 =====
    phone1 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话1')
    email1 = models.EmailField(blank=True, null=True, verbose_name='邮箱1')
    phone2 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话2')
    email2 = models.EmailField(blank=True, null=True, verbose_name='邮箱2')
    
    # ===== 地址信息 =====
    country = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='country_customers',
        verbose_name='国家'
    )
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='省份/城市')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='详细地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='邮政编码')
    
    # ===== 企业信息 =====
    industry = models.CharField(max_length=50, blank=True, null=True, verbose_name='所属行业')
    enterprise_type = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enterprise_type_customers',
        verbose_name='企业性质'
    )
    registered_capital = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='注册资本')
    
    # ===== 其他 =====
    customer_level = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_level_customers',
        verbose_name='客户等级'
    )
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='信用额度')
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name='网站')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    
    # ===== 时间字段 =====
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'customer_fields'
        verbose_name = '客户'
        verbose_name_plural = '客户'
    
    @property
    def creator(self):
        """获取创建人"""
        return self.node.created_by if hasattr(self, 'node') and self.node else None
    
    def __str__(self):
        return self.customer_name
```

### 10.2 权限检查集成示例

```python
# 在视图中使用权限检查

@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """查看节点"""
    node = NodeService.get_by_id(node_id)
    if not node:
        raise Http404('节点不存在')
    
    # 客户节点权限检查
    if node_type_slug == 'customer':
        has_perm, error_msg = check_customer_permission(request.user, node, 'view')
        if not has_perm:
            messages.error(request, error_msg)
            return redirect('nodes:node_list', node_type_slug=node_type_slug)
    
    # ... 后续处理
```

---

## 十一、模块注册机制

### 11.1 模块注册表模型（NodeModule）

每个 Node 模块需要在数据库中注册，以便系统识别和管理。

```python
# core/node/models.py
class NodeModule(models.Model):
    """Node 模块注册表"""
    
    module_id = models.CharField(max_length=50, unique=True, verbose_name='模块ID')
    name = models.CharField(max_length=100, verbose_name='模块名称')
    version = models.CharField(max_length=20, verbose_name='版本号')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    path = models.CharField(max_length=200, verbose_name='模块路径')
    
    is_installed = models.BooleanField(default=False, verbose_name='是否已安装')
    is_active = models.BooleanField(default=False, verbose_name='是否启用')
    is_system = models.BooleanField(default=False, verbose_name='是否系统默认模块')
    
    installed_at = models.DateTimeField(null=True, blank=True, verbose_name='安装时间')
    activated_at = models.DateTimeField(null=True, blank=True, verbose_name='启用时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'node_modules'
        verbose_name = 'Node模块'
        verbose_name_plural = 'Node模块'
        ordering = ['name']
    
    @property
    def path_exists(self) -> bool:
        """检查模块目录是否存在"""
        import os
        from django.conf import settings
        if not self.path:
            return False
        module_path = os.path.join(settings.BASE_DIR, 'nodes', self.path)
        return os.path.isdir(module_path)
    
    def __str__(self):
        return f"{self.name} ({self.module_id})"
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| module_id | CharField(50) | 模块唯一标识，与 module.py 中的 id 一致 |
| name | CharField(100) | 模块显示名称 |
| version | CharField(20) | 模块版本号 |
| author | CharField(100) | 模块作者 |
| description | TextField | 模块描述 |
| path | CharField(200) | 模块相对于 nodes/ 的路径 |
| is_installed | BooleanField | 是否已注册到系统 |
| is_active | BooleanField | 是否启用（模块可用） |
| is_system | BooleanField | 是否系统默认模块（不可删除） |
| installed_at | DateTimeField | 注册时间 |
| activated_at | DateTimeField | 启用时间 |
| path_exists | Property | 运行时属性，检查目录是否存在（不存储在数据库） |

---

### 11.2 模块状态流转

```
未发现模块 ──扫描──> 未注册模块 ──注册/安装──> 已安装（未启用） ──启用──> 已启用
                          ↑                                    │
                          │                                    ▼
                          │                              禁用 <── 已启用（可禁用）
                          │                                    │
                          │                                    ▼
                          └─── 删除注册 <── 已安装              ── 目录删除
                                ↑                               │
                                │                               ▼
                        扫描不到 module.py              不存在（目录缺失）
                          + is_active=False
```

**术语定义**：

| 术语 | 定义 |
|------|------|
| 扫描 | 检测 `nodes/` 下的子目录是否存在 `module.py` |
| 注册/安装 | 发现新模块（module.py 存在）+ 数据库无记录 → 写入 NodeModule |
| 启用 | 设置 is_active=True，模块可使用 |
| 禁用 | 设置 is_active=False，模块暂停使用 |
| 删除注册 | module.py 不存在 + is_active=False → 删除 NodeModule 记录 |
| 不存在 | 模块目录被删除，但数据库记录仍存在 |

---

### 11.3 模块完整状态定义

| 状态 | 判断条件 | 界面显示 |
|------|----------|----------|
| 不存在 | path_exists=False | 红色 badge "不存在" |
| 未安装 | path_exists=True AND is_installed=False | 黄色 badge "未安装" |
| 已安装 | path_exists=True AND is_installed=True AND is_active=False | 灰色 badge "已安装" |
| 已启用 | path_exists=True AND is_active=True | 绿色 badge "已启用" |

**优先级判断**：判断模块状态时，应首先检查 `path_exists`，因为目录不存在是最严重的问题。

---

## 十二、模块信息文件

### 12.1 文件位置与命名

每个 Node 模块必须在模块根目录下包含 `module.py` 文件，作为模块的信息入口点。

```
nodes/customer/
├── module.py         # 必选：模块信息文件
├── models.py
├── views.py
└── templates/
```

### 12.2 文件格式

```python
# nodes/customer/module.py

MODULE_INFO = {
    'id': 'customer',
    'name': '客户信息（海外）',
    'version': '1.0.0',
    'author': 'CIMF Team',
    'description': '海外客户信息管理模块，支持客户信息的 CRUD 操作',
    'models': ['CustomerFields'],
    'dependencies': [],
}

def get_install_sql():
    """
    获取模块安装时执行的 SQL（可选）
    返回：SQL 字符串 或 None
    """
    return None

def get_uninstall_sql():
    """
    获取模块卸载时执行的 SQL（可选）
    返回：SQL 字符串 或 None
    注意：此方法仅在删除模块时调用，不删除业务数据表
    """
    return None
```

### 12.3 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | String | 是 | 模块唯一标识，不能与已注册模块重复 |
| name | String | 是 | 模块显示名称 |
| version | String | 是 | 版本号，建议使用语义化版本（如 1.0.0） |
| author | String | 否 | 模块作者 |
| description | String | 否 | 模块功能描述 |
| models | List[String] | 否 | 模块包含的数据模型类名列表 |
| dependencies | List[String] | 否 | 依赖的其他模块 ID 列表 |

### 12.4 示例：国内客户模块

```python
# nodes/customer_cn/module.py

MODULE_INFO = {
    'id': 'customer_cn',
    'name': '客户信息（国内）',
    'version': '1.0.0',
    'author': 'CIMF Team',
    'description': '国内客户信息管理模块，支持省市区联动功能',
    'models': ['CustomerCnFields'],
    'dependencies': [],
}
```

---

## 十三、模块服务层

### 13.1 NodeModuleService

```python
# nodes/services/node_module_service.py
import os
import importlib.util
from typing import List, Optional, Dict, Any
from django.utils import timezone
from nodes.models import NodeModule


class NodeModuleService:
    """Node 模块服务"""
    
    MODULES_DIR = 'nodes'
    
    # ===== 扫描功能 =====
    
    @staticmethod
    def scan_modules() -> List[Dict[str, Any]]:
        """
        扫描 nodes/ 目录下的所有模块
        
        返回：模块信息列表，包含以下字段：
            - id, name, version, author, description
            - path: 相对于 nodes/ 的路径
            - is_registered: 是否已在数据库注册
            - module_obj: 模块对象（如果可导入）
        """
        modules = []
        base_path = NodeModuleService.MODULES_DIR
        
        if not os.path.exists(base_path):
            return modules
        
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            
            # 检查是否是目录
            if not os.path.isdir(item_path):
                continue
            
            # 检查是否存在 module.py
            module_file = os.path.join(item_path, 'module.py')
            if not os.path.exists(module_file):
                continue
            
            # 读取模块信息
            module_info = NodeModuleService._load_module_info(item)
            if module_info:
                # 检查是否已注册
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
            spec = importlib.util.spec_from_file_location(f"nodes.{module_dir}.module", module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'MODULE_INFO'):
                return module.MODULE_INFO
            return None
        except Exception as e:
            print(f"加载模块 {module_dir} 信息失败: {e}")
            return None
    
    # ===== 注册/安装功能 =====
    
    @staticmethod
    def register_module(module_info: Dict[str, Any]) -> NodeModule:
        """
        注册模块（安装模块）
        
        参数：module_info - 模块信息字典
        返回：NodeModule 实例
        """
        module_id = module_info['id']
        existing = NodeModule.objects.filter(module_id=module_id).first()
        
        if existing:
            # 已存在则更新
            existing.is_installed = True
            existing.installed_at = timezone.now()
            existing.save()
            return existing
        
        # 创建新记录
        return NodeModule.objects.create(
            module_id=module_id,
            name=module_info.get('name', module_id),
            version=module_info.get('version', '1.0.0'),
            author=module_info.get('author'),
            description=module_info.get('description'),
            path=module_info.get('path', module_id),
            is_installed=True,
            is_active=False,
            is_system=False,
            installed_at=timezone.now(),
        )
    
    # ===== 启用/禁用功能 =====
    
    @staticmethod
    def enable_module(module_id: str) -> Optional[NodeModule]:
        """启用模块"""
        module = NodeModule.objects.filter(module_id=module_id).first()
        if module and module.is_installed:
            module.is_active = True
            module.activated_at = timezone.now()
            module.save()
            return module
        return None
    
    @staticmethod
    def disable_module(module_id: str) -> Optional[NodeModule]:
        """禁用模块"""
        module = NodeModule.objects.filter(module_id=module_id).first()
        if module:
            module.is_active = False
            module.save()
            return module
        return None
    
    # ===== 删除注册功能 =====
    
    @staticmethod
    def cleanup_uninstalled_modules():
        """
        清理已卸载的模块注册记录
        
        条件：module.py 不存在 + is_active=False
        """
        registered_modules = NodeModule.objects.filter(is_installed=True)
        cleaned = []
        
        for module in registered_modules:
            module_path = os.path.join(NodeModuleService.MODULES_DIR, module.path)
            module_file = os.path.join(module_path, 'module.py')
            
            # 如果 module.py 不存在且模块未启用，则删除注册记录
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
```

---

## 十四、模块管理页面

### 14.1 页面功能

模块管理页面提供以下功能：

1. **扫描模块**：检测 nodes/ 目录下的所有模块
2. **显示已注册模块**：列出所有已安装的模块及状态（包括目录是否存在）
3. **显示未注册模块**：显示扫描到但未注册的模块
4. **安装模块**：将未注册模块注册到系统
5. **启用/禁用模块**：切换模块的启用状态（目录不存在时禁用）
6. **删除注册**：在模块被删除（module.py 不存在）且已禁用时，清理注册记录

### 14.2 页面结构

```html
{% extends "core/frames/frame_admin.html" %}

{% block admin_title %}Node 模块管理{% endblock %}

{% block admin_content %}
<div class="row">
    <div class="col-12">
        <!-- 扫描按钮 -->
        <div class="mb-3">
            <a href="{{ url('node:module_scan') }}" class="btn btn-primary">
                <i class="bi bi-search"></i> 扫描模块
            </a>
        </div>
        
        <!-- 已注册模块列表 -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">已安装模块</h5>
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>模块名称</th>
                            <th>ID</th>
                            <th>版本</th>
                            <th>状态</th>
                            <th>描述</th>
                            <th>安装时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for module in modules %}
                        <tr>
                            <td>{{ module.name }}</td>
                            <td><code>{{ module.module_id }}</code></td>
                            <td>{{ module.version }}</td>
                            <td>
                                {% if not module.path_exists %}
                                <span class="badge bg-danger">不存在</span>
                                {% elif module.is_active %}
                                <span class="badge bg-success">已启用</span>
                                {% elif module.is_installed %}
                                <span class="badge bg-secondary">已安装</span>
                                {% else %}
                                <span class="badge bg-warning">未安装</span>
                                {% endif %}
                            </td>
                            <td>{{ module.description|default:'-'|truncatechars:30 }}</td>
                            <td>{{ module.installed_at|date:"Y-m-d H:i" if module.installed_at else '-' }}</td>
                            <td>
                                {% if not module.path_exists %}
                                <span class="text-muted">目录缺失</span>
                                {% elif module.is_installed and not module.is_active %}
                                <a href="{{ url('node:module_enable', module.module_id) }}" class="btn btn-sm btn-success">启用</a>
                                {% elif module.is_active %}
                                <a href="{{ url('node:module_disable', module.module_id) }}" class="btn btn-sm btn-warning">禁用</a>
                                {% else %}
                                <a href="{{ url('node:module_install', module.module_id) }}" class="btn btn-sm btn-primary">安装</a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 未注册模块列表 -->
        {% if unregistered_modules %}
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">未注册模块</h5>
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>模块名称</th>
                            <th>ID</th>
                            <th>版本</th>
                            <th>作者</th>
                            <th>描述</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for module in unregistered_modules %}
                        <tr>
                            <td>{{ module.name }}</td>
                            <td><code>{{ module.id }}</code></td>
                            <td>{{ module.version }}</td>
                            <td>{{ module.author|default('-') }}</td>
                            <td>{{ module.description|default('-')|truncatechars:50 }}</td>
                            <td>
                                <a href="{{ url('node:module_install', module.id) }}" class="btn btn-sm btn-primary">安装</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

**模板要点**：
1. 使用 `module.path_exists` 判断目录是否存在
2. 目录不存在时显示红色 badge 并禁用操作按钮
3. 增加"描述"列展示模块信息
4. 未注册模块单独显示，便于安装

### 14.3 路由配置

| 路径 | 函数 | 说明 |
|------|------|------|
| `/nodes/modules/` | `node_modules` | 模块管理首页 |
| `/nodes/modules/scan/` | `module_scan` | 扫描模块并同步 |
| `/nodes/modules/install/<id>/` | `module_install` | 安装模块（注册+执行迁移） |
| `/nodes/modules/enable/<id>/` | `module_enable` | 启用模块 |
| `/nodes/modules/disable/<id>/` | `module_disable` | 禁用模块 |

> **注意**：模块管理属于 `core` 应用（路径前缀 `node:`），不是 `nodes` 应用。

---

## 十五、新建模块功能

### 15.1 功能说明

在模块管理页面提供"新建模块"功能，输入基本信息后：
1. 在 `nodes/` 目录下创建对应模块名目录
2. 生成基础文件结构
3. 生成 `module.py` 信息文件

### 15.2 创建的目录结构

```
nodes/{module_id}/
├── __init__.py
├── module.py          # 模块信息文件
├── models.py          # 数据模型（空模板）
├── services.py        # 服务层（空模板）
├── views.py          # 视图（空模板）
├── urls.py           # 路由（空模板）
├── apps.py           # 应用配置
├── admin.py          # Admin 配置
├── migrations/
│   └── __init__.py
└── templates/
    └── list.html
```

### 15.3 module.py 模板

```python
# nodes/{module_id}/module.py

MODULE_INFO = {
    'id': '{module_id}',
    'name': '{module_name}',
    'version': '1.0.0',
    'author': '',
    'description': '',
    'models': [],
    'dependencies': [],
}

def get_install_sql():
    return None

def get_uninstall_sql():
    return None
```

### 15.4 models.py 模板

```python
# nodes/{module_id}/models.py
# -*- coding: utf-8 -*-

from django.db import models
from core.node.models import Node


class {ModuleName}Fields(models.Model):
    """{模块名称}字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='{module_id}_fields',
        verbose_name='关联节点'
    )
    
    # ===== 基本信息 =====
    name = models.CharField(max_length=200, verbose_name='名称')
    
    # ===== 时间字段 =====
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = '{module_id}_fields'
        verbose_name = '{模块名称}'
        verbose_name_plural = '{模块名称}'
    
    def __str__(self):
        return self.name
```

---

## 十六、默认模块处理

### 16.1 系统默认模块

系统初始化时，以下模块被标记为默认模块：

| 模块 ID | 模块名称 | 说明 |
|---------|----------|------|
| customer | 客户信息（海外） | 海外客户信息管理 |
| customer_cn | 客户信息（国内） | 国内客户信息管理，支持省市区联动 |

### 16.2 初始化流程

在系统首次初始化数据库时（`init_db.py` 或管理命令）：

1. **创建模块目录和文件**：确保 `nodes/customer/` 和 `nodes/customer_cn/` 目录存在，且包含 `module.py`
2. **执行数据库迁移**：执行 `makemigrations` 和 `migrate` 创建数据表
3. **注册到 NodeModule**：
   - 设置 `is_installed=True`
   - 设置 `is_active=True`
   - 设置 `is_system=True`（系统默认模块，不可删除）

### 16.3 初始化代码示例

```python
# init_db.py 或 management command

def install_default_modules():
    """安装默认模块"""
    from nodes.services import NodeModuleService
    from django.core.management import call_command
    
    default_modules = ['customer', 'customer_cn']
    
    for module_id in default_modules:
        # 检查模块目录是否存在
        module_path = os.path.join('nodes', module_id, 'module.py')
        if not os.path.exists(module_path):
            print(f"警告：默认模块 {module_id} 的 module.py 不存在，跳过")
            continue
        
        # 执行数据库迁移
        try:
            call_command('makemigrations', module_id, verbosity=0)
            call_command('migrate', module_id, verbosity=0)
        except Exception as e:
            print(f"模块 {module_id} 迁移失败: {e}")
        
        # 读取模块信息并注册
        module_info = NodeModuleService._load_module_info(module_id)
        if module_info:
            module = NodeModuleService.register_module(module_info)
            NodeModuleService.enable_module(module.module_id)
            
            # 标记为系统默认模块
            module.is_system = True
            module.save()
            
            print(f"默认模块 {module_id} 已安装")
```

> **重要提醒**：`DEFAULT_NODE_TYPES` 配置（见第四章）已废弃，所有节点类型应通过 NodeModule 模块系统管理。旧配置中的 `customer-cn` 已统一为 `customer_cn`。

---

## 十七、模块与节点类型的关系

### 17.1 对应关系

每个已安装并启用的 Node 模块会自动关联到一个 NodeType：

| 模块 | NodeType | 说明 |
|------|----------|------|
| customer | NodeType(slug='customer') | 海外客户 |
| customer_cn | NodeType(slug='customer_cn') | 国内客户 |

### 17.2 同步机制

当模块被安装或启用时，系统应自动确保对应的 NodeType 存在：

```python
@staticmethod
def sync_node_type(module: NodeModule) -> NodeType:
    """同步模块与节点类型"""
    node_type = NodeType.objects.filter(slug=module.module_id).first()
    
    if not node_type:
        # 创建新的节点类型
        node_type = NodeType.objects.create(
            name=module.name,
            slug=module.module_id,
            description=module.description,
            icon='bi-folder',
            is_active=module.is_active,
        )
    else:
        # 更新现有节点类型
        node_type.name = module.name
        node_type.description = module.description
        node_type.is_active = module.is_active
        node_type.save()
    
    return node_type
```

---

## 十八、INSTALLED_APPS 动态加载机制

### 18.1 设计目标

新增模块时无需修改任何配置文件（包括 settings.py 和 INSTALLED_APPS）。只需创建模块目录和 module.py，系统启动时自动发现并加载。

### 18.2 实现方式

在 `cimf_django/settings.py` 中使用动态扫描替代硬编码：

```python
# 基础应用（必须保留）
_base_apps = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'nodes',
]

# 动态扫描 nodes/ 下的模块
_node_modules = []
_nodes_dir = os.path.join(BASE_DIR, 'nodes')
if os.path.isdir(_nodes_dir):
    for item in os.listdir(_nodes_dir):
        module_path = os.path.join(_nodes_dir, item)
        if os.path.isdir(module_path) and os.path.exists(os.path.join(module_path, 'module.py')):
            _node_modules.append(f'nodes.{item}')

INSTALLED_APPS = _base_apps + _node_modules
```

### 18.3 工作原理

1. **settings.py 加载时**：Python 执行 settings.py，触发动态扫描
2. **扫描 nodes/ 目录**：检查每个子目录是否存在 module.py
3. **自动添加到 INSTALLED_APPS**：发现的模块自动加入列表
4. **Django 正常启动**：INSTALLED_APPS 已包含所有模块

### 18.4 新增模块流程

```
1. 创建模块目录：nodes/{module_id}/
2. 创建 module.py：定义模块信息
3. 创建业务模型：models.py, services.py, views.py 等
4. 重启服务：python run.py
5. 系统自动发现并加载
```

**无需修改任何配置文件！**

### 18.5 验证函数

在 `run.py` 和 `init_db.py` 中保留验证函数，用于输出已加载的模块信息：

```python
def validate_and_fix_installed_apps():
    """验证并输出 INSTALLED_APPS 中的模块状态"""
    from django.conf import settings
    
    loaded_node_modules = [app for app in settings.INSTALLED_APPS if app.startswith('nodes.')]
    print(f"  已加载 Node 模块: {', '.join(loaded_node_modules) if loaded_node_modules else '无'}")
```

### 18.6 限制说明

由于 Django 的设计限制，动态加载存在以下限制：

1. **需要重启**：新增模块后必须重启服务才能被识别
2. **需要数据库迁移**：新模块的模型需要执行 migrate
3. **需要注册到 NodeModule**：首次启动后需在管理页面安装模块

这些限制是 Django 架构决定的，无法通过代码绕过。

> **注意**：原第 18 章的"自动修复机制"已不再需要，因为 settings.py 已实现动态加载。

---

## 十九、测试场景

### 19.1 新增模块场景

**场景**：新增一个模块，无需修改任何配置文件

1. 在 `nodes/` 目录下创建新模块目录，如 `nodes/supplier/`
2. 创建 `module.py` 文件，定义模块信息
3. 创建 `models.py`、`services.py`、`views.py` 等业务文件
4. 重启服务 `python run.py`
5. 系统自动发现并加载模块
6. 在模块管理页面执行"安装"操作

**验证**：在启动日志中应看到"已加载 Node 模块: nodes.customer, nodes.customer_cn, nodes.supplier"

### 19.2 删除模块场景

**场景**：删除模块目录后启动系统

1. 用户删除 `nodes/customer/` 目录
2. 执行 `python run.py`
3. settings.py 动态扫描时发现目录不存在，不会添加到 INSTALLED_APPS
4. Django 正常启动，不报错
5. 模块管理页面显示该模块状态为"不存在"（如果数据库中有记录的话）

### 19.3 恢复模块场景

**场景**：恢复已删除的模块目录

1. 重新创建 `nodes/customer/` 目录及所有必要文件
2. 重启系统
3. settings.py 自动扫描到并添加到 INSTALLED_APPS
4. 模块恢复正常

### 19.2 模块管理页面测试

**测试点**：

| 测试项 | 预期结果 |
|--------|----------|
| 目录存在 + 未安装 | 显示黄色 badge "未安装"，显示"安装"按钮 |
| 目录存在 + 已安装未启用 | 显示灰色 badge "已安装"，显示"启用"按钮 |
| 目录存在 + 已启用 | 显示绿色 badge "已启用"，显示"禁用"按钮 |
| 目录不存在 | 显示红色 badge "不存在"，显示"目录缺失"（不可操作） |

### 19.3 清理机制测试

**场景**：module.py 被删除 + 模块已禁用

1. 模块目录存在但 module.py 被删除
2. 用户访问模块管理页面并点击"扫描模块"
3. `cleanup_uninstalled_modules()` 被调用
4. 系统自动删除该模块的注册记录

---

*文档版本：1.4*  
*最后更新：2026-03-25*  
*更新内容：实现 INSTALLED_APPS 动态加载，新增模块无需修改配置文件*
