# 客户信息 Node 模块实现指南

本文档以"客户信息"节点类型为例，展示完整的 Node 系统实现流程。

---

## 一、概述

客户信息是系统预置的节点类型之一，用于记录客户的基本信息。

### 1.1 目录结构

```
nodes/
├── models.py                     # 节点模型（包含 NodeType, Node, CustomerFields）
├── views.py                      # 视图
├── urls.py                       # URL 配置
├── forms.py                      # 表单
├── admin.py                      # Django Admin
├── apps.py                       # 应用配置
└── services/
    ├── __init__.py
    ├── node_type_service.py      # 节点类型服务
    ├── node_service.py           # 节点服务
    └── customer_service.py       # 客户专用服务

templates/
├── nodes/
│   ├── index.html               # 事务总览
│   ├── types/                   # 节点类型管理
│   │   ├── index.html
│   │   └── edit.html
│   ├── field_types.html         # 字段类型列表
│   └── customer/
│       ├── list.html            # 客户列表
│       ├── view.html            # 客户详情
│       └── edit.html            # 客户编辑
└── core/
    └── frame_node.html          # 框架模板
```

### 1.2 路由设计

| 路径 | 函数 | 说明 |
|------|------|------|
| `/nodes/` | `nodes:index` | 事务总览 |
| `/nodes/types/` | `nodes:node_types` | 节点类型管理 |
| `/nodes/customer/` | `nodes:node_list` | 客户列表 |
| `/nodes/customer/create/` | `nodes:node_create` | 新建客户 |
| `/nodes/customer/<id>/` | `nodes:node_view` | 查看客户 |
| `/nodes/customer/<id>/edit/` | `nodes:node_edit` | 编辑客户 |
| `/nodes/customer/<id>/delete/` | `nodes:node_delete` | 删除客户 |

> **注意**：客户使用通用节点路由，URL 中的 `customer` 是节点类型的 `slug`，`<id>` 是节点的 `node_id`（而非 customer_fields 的 id）。

---

## 二、数据模型

### 2.1 节点类型模型

```python
# nodes/models.py - NodeType
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

### 2.2 节点主表模型

```python
# nodes/models.py - Node
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
    
    def __str__(self):
        return f'Node {self.id} ({self.node_type.slug})'
```

### 2.3 客户字段模型

本系统客户信息包含以下字段：

#### 字段总览

| 字段 | 类型 | 说明 |
|------|------|------|
| customer_name | CharField | 客户名称（必填，唯一） |
| customer_code | CharField | 客户代码（唯一编号） |
| customer_type | ForeignKey | 客户类型（关联词汇表） |
| enterprise_name | CharField | 企业名称 |
| phone1 | CharField | 电话1 |
| email1 | EmailField | 邮箱1 |
| phone2 | CharField | 电话2（可选） |
| email2 | EmailField | 邮箱2（可选） |
| country | CharField | 国家 |
| province | CharField | 省份/城市 |
| address | CharField | 详细地址 |
| postal_code | CharField | 邮政编码 |
| industry | CharField | 所属行业 |
| enterprise_type | ForeignKey | 企业性质（关联词汇表） |
| registered_capital | DecimalField | 注册资本 |
| customer_level | ForeignKey | 客户等级（关联词汇表） |
| credit_limit | DecimalField | 信用额度 |
| website | URLField | 网站 |
| notes | TextField | 备注 |

#### 模型定义

```python
# nodes/models.py - CustomerFields
class CustomerFields(models.Model):
    """客户节点字段表
    
    客户类型的专用字段，与 Node 一对一关联
    共20个字段
    """
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='customer_fields',
        verbose_name='关联节点'
    )
    
    # 基本信息
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
    
    # 联系方式（各2个）
    phone1 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话1')
    email1 = models.EmailField(blank=True, null=True, verbose_name='邮箱1')
    phone2 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话2')
    email2 = models.EmailField(blank=True, null=True, verbose_name='邮箱2')
    
    # 地址信息
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='国家')
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='省份/城市')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='详细地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='邮政编码')
    
    # 企业信息（可选）
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
    
    # 其他
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
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'customer_fields'
        verbose_name = '客户'
        verbose_name_plural = '客户'
    
    def __str__(self):
        return self.customer_name
```

### 2.4 字段配置

系统预置客户信息节点类型时使用以下字段配置：

```python
# nodes/services/node_type_service.py
DEFAULT_NODE_TYPES = [
    {
        'name': '客户信息',
        'slug': 'customer',
        'description': '记录客户基本信息',
        'icon': 'bi-people',
        'fields_config': [
            # 基本信息
            {'field_type': 'string', 'name': 'customer_name', 'label': '客户名称', 'required': True, 'unique': True},
            {'field_type': 'string', 'name': 'customer_code', 'label': '客户代码', 'required': False, 'unique': True},
            {'field_type': 'entity_reference', 'name': 'customer_type', 'label': '客户类型', 'required': False, 'reference_type': 'taxonomy', 'taxonomy_slug': 'customer_type'},
            {'field_type': 'string', 'name': 'enterprise_name', 'label': '企业名称', 'required': False},
            
            # 联系方式（各2个）
            {'field_type': 'telephone', 'name': 'phone1', 'label': '电话1', 'required': False},
            {'field_type': 'email', 'name': 'email1', 'label': '邮箱1', 'required': False},
            {'field_type': 'telephone', 'name': 'phone2', 'label': '电话2', 'required': False},
            {'field_type': 'email', 'name': 'email2', 'label': '邮箱2', 'required': False},
            
            # 地址信息
            {'field_type': 'string', 'name': 'country', 'label': '国家', 'required': False},
            {'field_type': 'string', 'name': 'province', 'label': '省份/城市', 'required': False},
            {'field_type': 'string', 'name': 'address', 'label': '详细地址', 'required': False},
            {'field_type': 'string', 'name': 'postal_code', 'label': '邮政编码', 'required': False},
            
            # 企业信息
            {'field_type': 'string', 'name': 'industry', 'label': '所属行业', 'required': False},
            {'field_type': 'entity_reference', 'name': 'enterprise_type', 'label': '企业性质', 'required': False, 'reference_type': 'taxonomy', 'taxonomy_slug': 'economic_type'},
            {'field_type': 'decimal', 'name': 'registered_capital', 'label': '注册资本', 'required': False},
            
            # 其他
            {'field_type': 'entity_reference', 'name': 'customer_level', 'label': '客户等级', 'required': False, 'reference_type': 'taxonomy', 'taxonomy_slug': 'customer_level'},
            {'field_type': 'decimal', 'name': 'credit_limit', 'label': '信用额度', 'required': False},
            {'field_type': 'link', 'name': 'website', 'label': '网站', 'required': False},
            {'field_type': 'string_long', 'name': 'notes', 'label': '备注', 'required': False},
        ],
        'is_active': True,
    },
]
```

---

## 三、服务层

### 3.1 节点类型服务

`nodes/services/node_type_service.py` 提供节点类型的 CRUD 操作：

```python
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
        return NodeType.objects.create(**data)
    
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
```

### 3.2 节点服务

`nodes/services/node_service.py` 提供节点主表的 CRUD 操作：

```python
class NodeService:
    """节点主表服务"""
    
    @staticmethod
    def get_list(node_type_slug: str, search: Optional[str] = None) -> QuerySet:
        """获取节点列表"""
        node_type = NodeTypeService.get_by_slug(node_type_slug)
        if not node_type:
            return Node.objects.none()
        
        queryset = Node.objects.filter(node_type=node_type)
        
        if search:
            # 动态搜索字段表
            pass
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(node_id: int) -> Optional[Node]:
        """根据 ID 获取节点"""
        return Node.objects.filter(id=node_id).first()
    
    @staticmethod
    def create(node_type_slug: str, user, fields_data: Dict) -> Node:
        """创建节点"""
        node_type = NodeTypeService.get_by_slug(node_type_slug)
        if not node_type:
            raise ValueError(f"节点类型 {node_type_slug} 不存在")
        
        return Node.objects.create(
            node_type=node_type,
            created_by=user,
            updated_by=user
        )
    
    @staticmethod
    def update(node_id: int, user, fields_data: Dict) -> Optional[Node]:
        """更新节点"""
        node = Node.objects.filter(id=node_id).first()
        if node:
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

### 3.3 客户专用服务

`nodes/services/customer_service.py` 提供客户数据的 CRUD 操作：

```python
# -*- coding: utf-8 -*-
"""
客户管理服务，提供客户的 CRUD 操作

主要功能：
- 获取客户列表
- 创建/更新/删除客户
- 获取客户详情
"""

from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from nodes.models import Node, CustomerFields
from nodes.services import NodeService

User = get_user_model()


class CustomerService:
    """客户管理服务"""
    
    @staticmethod
    def get_list(search: Optional[str] = None) -> List[CustomerFields]:
        """获取客户列表
        
        参数：
            search: 搜索关键字
        
        返回：
            客户查询集
        """
        queryset = CustomerFields.objects.all()
        
        if search:
            queryset = queryset.filter(
                customer_name__icontains=search
            ) | queryset.filter(
                contact_person__icontains=search
            ) | queryset.filter(
                phone__icontains=search
            )
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(customer_id: int) -> Optional[CustomerFields]:
        """根据 ID 获取客户
        
        参数：
            customer_id: 客户 ID
        
        返回：
            客户对象或 None
        """
        return CustomerFields.objects.filter(id=customer_id).first()
    
    @staticmethod
    def get_by_node_id(node_id: int) -> Optional[CustomerFields]:
        """根据节点 ID 获取客户
        
        参数：
            node_id: 节点 ID
        
        返回：
            客户对象或 None
        """
        return CustomerFields.objects.filter(node_id=node_id).first()
    
    @staticmethod
    def create(user, data: Dict[str, Any]) -> CustomerFields:
        """创建客户
        
        参数：
            user: 创建人用户对象
            data: 客户数据字典
        
        返回：
            创建的客户对象
        """
        # 先创建主表记录
        node = NodeService.create('customer', user, {})
        
        # 再创建字段表记录
        customer = CustomerFields.objects.create(
            node=node,
            customer_name=data.get('customer_name', ''),
            contact_person=data.get('contact_person'),
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address', {}),
            customer_type_id=data.get('customer_type_id'),
            notes=data.get('notes')
        )
        
        return customer
    
    @staticmethod
    def update(customer_id: int, data: Dict[str, Any]) -> Optional[CustomerFields]:
        """更新客户
        
        参数：
            customer_id: 客户 ID
            data: 客户数据字典
        
        返回：
            更新后的客户对象或 None
        """
        customer = CustomerFields.objects.filter(id=customer_id).first()
        if not customer:
            return None
        
        for key, value in data.items():
            if hasattr(customer, key) and key != 'id' and key != 'node':
                setattr(customer, key, value)
        
        customer.save()
        return customer
    
    @staticmethod
    def delete(customer_id: int) -> bool:
        """删除客户
        
        参数：
            customer_id: 客户 ID
        
        返回：
            是否删除成功
        """
        customer = CustomerFields.objects.filter(id=customer_id).first()
        if customer:
            node = customer.node
            customer.delete()
            if node:
                node.delete()
            return True
        return False
```

---

## 四、视图层

### 4.1 节点列表视图

```python
# nodes/views.py
@login_required
def node_list(request, node_type_slug: str):
    """节点列表
    
    根据 node_type_slug 路由到不同的节点类型处理
    """
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        raise Http404('节点类型不存在')
    
    search = request.GET.get('search', '')
    node_types = NodeTypeService.get_all()
    
    # 客户节点特殊处理
    if node_type_slug == 'customer':
        customers = CustomerService.get_list(search if search else None)
        return render(request, 'nodes/customer/list.html', {
            'node_type': node_type,
            'node_types': node_types,
            'customers': customers,
            'search': search,
            'active_section': node_type_slug,
        })
    
    # 其他节点类型使用通用模板
    nodes = NodeService.get_list(node_type_slug, search if search else None)
    return render(request, 'nodes/list.html', {
        'node_type': node_type,
        'node_types': node_types,
        'nodes': nodes,
        'search': search,
        'active_section': node_type_slug,
    })
```

### 4.2 创建节点视图

```python
@login_required
def node_create(request, node_type_slug: str):
    """创建节点"""
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        raise Http404('节点类型不存在')
    
    node_types = NodeTypeService.get_all()
    
    if node_type_slug == 'customer':
        if request.method == 'POST':
            data = {
                'customer_name': request.POST.get('customer_name', '').strip(),
                'contact_person': request.POST.get('contact_person', '').strip() or None,
                'phone': request.POST.get('phone', '').strip() or None,
                'email': request.POST.get('email', '').strip() or None,
                'notes': request.POST.get('notes', '').strip() or None,
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
        })
    
    return redirect('nodes:node_list', node_type_slug=node_type_slug)
```

### 4.3 查看节点视图

```python
@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """查看节点"""
    node = NodeService.get_by_id(node_id)
    if not node:
        raise Http404('节点不存在')
    
    node_types = NodeTypeService.get_all()
    
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
```

### 4.4 编辑节点视图

```python
@login_required
def node_edit(request, node_type_slug: str, node_id: int):
    """编辑节点"""
    node = NodeService.get_by_id(node_id)
    if not node:
        raise Http404('节点不存在')
    
    node_types = NodeTypeService.get_all()
    
    if node_type_slug == 'customer':
        customer = CustomerService.get_by_node_id(node_id)
        
        if request.method == 'POST':
            data = {
                'customer_name': request.POST.get('customer_name', '').strip(),
                'contact_person': request.POST.get('contact_person', '').strip() or None,
                'phone': request.POST.get('phone', '').strip() or None,
                'email': request.POST.get('email', '').strip() or None,
                'notes': request.POST.get('notes', '').strip() or None,
            }
            
            try:
                CustomerService.update(customer.id, data)
                messages.success(request, '客户更新成功')
                return redirect('nodes:node_view', node_type_slug=node_type_slug, node_id=node_id)
            except Exception as e:
                messages.error(request, str(e))
        
        return render(request, 'nodes/customer/edit.html', {
            'node_type': node.node_type,
            'node_types': node_types,
            'node': node,
            'customer': customer,
            'active_section': node_type_slug,
        })
    
    return redirect('nodes:node_view', node_type_slug=node_type_slug, node_id=node_id)
```

### 4.5 删除节点视图

```python
@login_required
def node_delete(request, node_type_slug: str, node_id: int):
    """删除节点"""
    if node_type_slug == 'customer':
        customer = CustomerService.get_by_node_id(node_id)
        if customer:
            CustomerService.delete(customer.id)
            messages.success(request, '客户已删除')
    
    return redirect('nodes:node_list', node_type_slug=node_type_slug)
```

---

## 五、模板层

### 5.1 客户列表模板

`templates/nodes/customer/list.html`：

```html
{% extends "core/frame_node.html" %}

{% set show_nav = true %}
{% set show_header = false %}

{% block admin_title %}
  {{ node_type.name }}
{% endblock %}

{% block admin_title_buttons %}
<a href="{{ url('nodes:node_create', node_type.slug) }}" class="btn btn-primary">
    <i class="bi bi-plus-lg"></i> 新建
</a>
{% endblock %}

{% block admin_content %}
<div class="row mb-4">
    <div class="col-12">
        <form method="get" class="d-flex gap-2">
            <input type="text" name="search" class="form-control" placeholder="搜索..." value="{{ search }}">
            <button type="submit" class="btn btn-primary">搜索</button>
        </form>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr>
                            <th>客户名称</th>
                            <th>联系人</th>
                            <th>电话</th>
                            <th>邮箱</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for customer in customers %}
                        <tr>
                            <td>{{ customer.customer_name }}</td>
                            <td>{{ customer.contact_person|default('-') }}</td>
                            <td>{{ customer.phone|default('-') }}</td>
                            <td>{{ customer.email|default('-') }}</td>
                            <td>{{ customer.created_at|date('Y-m-d H:i') }}</td>
                            <td>
                                <a href="{{ url('nodes:node_view', node_type.slug, customer.node_id) }}" class="btn btn-sm btn-outline-primary">查看</a>
                                <a href="{{ url('nodes:node_edit', node_type.slug, customer.node_id) }}" class="btn btn-sm btn-outline-secondary">编辑</a>
                                <a href="{{ url('nodes:node_delete', node_type.slug, customer.node_id) }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定删除?')">删除</a>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="6" class="text-center text-muted">暂无数据</td>
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

### 5.2 客户详情模板

`templates/nodes/customer/view.html`：

```html
{% extends "core/frame_node.html" %}

{% set show_nav = true %}
{% set show_header = false %}

{% block admin_title %}
  {{ customer.customer_name }}
{% endblock %}

{% block admin_title_buttons %}
<a href="{{ url('nodes:node_edit', node_type.slug, node.id) }}" class="btn btn-primary">编辑</a>
<a href="{{ url('nodes:node_list', node_type.slug) }}" class="btn btn-secondary">返回列表</a>
{% endblock %}

{% block admin_content %}
<div class="card">
    <div class="card-body">
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label text-muted">客户名称</label>
                <p class="mb-0">{{ customer.customer_name }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label text-muted">联系人</label>
                <p class="mb-0">{{ customer.contact_person|default('-') }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label text-muted">电话</label>
                <p class="mb-0">{{ customer.phone|default('-') }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label text-muted">邮箱</label>
                <p class="mb-0">{{ customer.email|default('-') }}</p>
            </div>
            <div class="col-12 mb-3">
                <label class="form-label text-muted">备注</label>
                <p class="mb-0">{{ customer.notes|default('-') }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label text-muted">创建时间</label>
                <p class="mb-0">{{ customer.created_at|date('Y-m-d H:i') }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label text-muted">更新时间</label>
                <p class="mb-0">{{ customer.updated_at|date('Y-m-d H:i') }}</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 5.3 客户编辑模板

`templates/nodes/customer/edit.html`：

```html
{% extends "core/frame_node.html" %}

{% set show_nav = true %}
{% set show_header = false %}

{% block admin_title %}
  {% if customer %}编辑{% else %}新建{% endif %}{{ node_type.name }}
{% endblock %}

{% block admin_content %}
<form method="post">
    {{ csrf_token() }}
    
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">基本信息</h5>
        </div>
        <div class="card-body">
            <div class="mb-3">
                <label class="form-label">客户名称 *</label>
                <input type="text" name="customer_name" class="form-control" value="{{ customer.customer_name|default('') }}" required>
            </div>
            <div class="mb-3">
                <label class="form-label">联系人</label>
                <input type="text" name="contact_person" class="form-control" value="{{ customer.contact_person|default('') }}">
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">电话</label>
                    <input type="text" name="phone" class="form-control" value="{{ customer.phone|default('') }}">
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">邮箱</label>
                    <input type="email" name="email" class="form-control" value="{{ customer.email|default('') }}">
                </div>
            </div>
        </div>
    </div>
    
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">备注</h5>
        </div>
        <div class="card-body">
            <textarea name="notes" class="form-control" rows="4">{{ customer.notes|default('') }}</textarea>
        </div>
    </div>
    
    <div class="text-end">
        <a href="{{ url('nodes:node_list', node_type.slug) }}" class="btn btn-secondary">取消</a>
        <button type="submit" class="btn btn-primary">保存</button>
    </div>
</form>
{% endblock %}
```

---

## 六、数据结构

### 6.1 节点类型存储（node_types 表）

```json
{
  "id": 1,
  "name": "客户信息",
  "slug": "customer",
  "description": "记录客户基本信息",
  "icon": "bi-people",
  "fields_config": [
    {"field_type": "string", "name": "customer_name", "label": "客户名称", "required": true, "unique": true},
    {"field_type": "string", "name": "customer_code", "label": "客户代码", "required": false, "unique": true},
    {"field_type": "entity_reference", "name": "customer_type", "label": "客户类型", "required": false, "reference_type": "taxonomy"},
    {"field_type": "string", "name": "enterprise_name", "label": "企业名称", "required": false},
    {"field_type": "telephone", "name": "phone1", "label": "电话1", "required": false},
    {"field_type": "email", "name": "email1", "label": "邮箱1", "required": false},
    {"field_type": "telephone", "name": "phone2", "label": "电话2", "required": false},
    {"field_type": "email", "name": "email2", "label": "邮箱2", "required": false},
    {"field_type": "string", "name": "country", "label": "国家", "required": false},
    {"field_type": "string", "name": "province", "label": "省份/城市", "required": false},
    {"field_type": "string", "name": "address", "label": "详细地址", "required": false},
    {"field_type": "string", "name": "postal_code", "label": "邮政编码", "required": false},
    {"field_type": "string", "name": "industry", "label": "所属行业", "required": false},
    {"field_type": "entity_reference", "name": "enterprise_type", "label": "企业性质", "required": false, "reference_type": "taxonomy"},
    {"field_type": "decimal", "name": "registered_capital", "label": "注册资本", "required": false},
    {"field_type": "entity_reference", "name": "customer_level", "label": "客户等级", "required": false, "reference_type": "taxonomy"},
    {"field_type": "decimal", "name": "credit_limit", "label": "信用额度", "required": false},
    {"field_type": "link", "name": "website", "label": "网站", "required": false},
    {"field_type": "string_long", "name": "notes", "label": "备注", "required": false}
  ],
  "is_active": true,
  "created_at": "2026-03-16 10:00:00",
  "updated_at": "2026-03-16 10:00:00"
}
```

### 6.2 节点主表存储（nodes 表）

```json
{
  "id": 1,
  "node_type_id": 1,
  "created_by_id": 1,
  "updated_by_id": 1,
  "created_at": "2026-03-16 10:00:00",
  "updated_at": "2026-03-16 10:00:00"
}
```

### 6.3 客户字段表存储（customer_fields 表）

```json
{
  "id": 1,
  "node_id": 1,
  
  "customer_name": "ABC科技有限公司",
  "customer_code": "CUST001",
  "customer_type_id": 1,
  "enterprise_name": "ABC集团",
  
  "phone1": "13800138000",
  "email1": "contact@abc.com",
  "phone2": "010-12345678",
  "email2": "info@abc.com",
  
  "country": "中国",
  "province": "北京市",
  "address": "朝阳区建国路88号",
  "postal_code": "100022",
  
  "industry": "软件开发",
  "enterprise_type_id": 3,
  "registered_capital": "10000000.00",
  
  "customer_level_id": 1,
  "credit_limit": "500000.00",
  "website": "https://www.abc.com",
  "notes": "重要客户，长期合作",
  
  "created_at": "2026-03-16 10:00:00",
  "updated_at": "2026-03-16 10:00:00"
}
```

---

## 七、界面预览

### 7.1 客户列表页

```
客户信息
┌─────────────────────────────────────────────────────────────────────┐
│ [+ 新建]                                                            │
├─────────────────────────────────────────────────────────────────────┤
│ [搜索...                              ] [搜索]                      │
├─────────────────────────────────────────────────────────────────────┤
│ 客户名称       │ 企业名称     │ 电话1        │ 邮箱1           │ 操作 │
│────────────────┼──────────────┼──────────────┼─────────────────┼──────│
│ ABC科技       │ ABC集团     │ 13800138000 │ a@abc.com      │查看编辑删除│
│ XYZ公司       │ XYZ有限    │ 13900139000 │ b@xyz.com      │查看编辑删除│
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 新建客户表单

```
新建客户信息
┌─────────────────────────────────────────────────────────────────────┐
│ 基本信息                                                              │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 客户名称 *    [________________________]                        │ │
│ │ 客户代码      [________________________]                        │ │
│ │ 客户类型      [选择...]                                         │ │
│ │ 企业名称      [________________________]                        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ 联系方式1                                                            │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 电话          [________________________]                        │ │
│ │ 邮箱          [________________________]                        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ 联系方式2（可选）                                                    │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 电话          [________________________]                        │ │
│ │ 邮箱          [________________________]                        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ 地址信息                                                              │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 国家          [________________________]                        │ │
│ │ 省份/城市     [________________________]                        │ │
│ │ 详细地址      [________________________]                        │ │
│ │ 邮政编码      [________________________]                        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ 企业信息（可选）                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 所属行业      [________________________]                        │ │
│ │ 企业性质      [选择...]                                         │ │
│ │ 注册资本      [________________________]                        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ 其他                                                                  │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 客户等级      [选择...]                                         │ │
│ │ 信用额度      [________________________]                        │ │
│ │ 网站          [________________________]                        │ │
│ │ 备注          [                                                ]│ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│                          [取消] [保存]                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.3 客户详情页

```
ABC科技有限公司
┌─────────────────────────────────────────────────────────────────────┐
│ [编辑] [返回列表]                                                   │
├─────────────────────────────────────────────────────────────────────┤
│ 基本信息                                                             │
│   客户名称     ABC科技有限公司                                      │
│   客户代码     CUST001                                             │
│   客户类型     VIP客户                                             │
│   企业名称     ABC集团                                             │
│                                                                      │
│ 联系方式1                                                           │
│   电话         13800138000                                          │
│   邮箱         contact@abc.com                                     │
│                                                                      │
│ 联系方式2                                                           │
│   电话         010-12345678                                        │
│   邮箱         info@abc.com                                        │
│                                                                      │
│ 地址信息                                                             │
│   国家         中国                                                 │
│   省份/城市   北京市                                               │
│   详细地址    朝阳区建国路88号                                     │
│   邮政编码    100022                                              │
│                                                                      │
│ 企业信息                                                             │
│   所属行业    软件开发                                              │
│   企业性质    民营企业                                              │
│   注册资本    10,000,000.00                                       │
│                                                                      │
│ 其他                                                                 │
│   客户等级    A级(重点)                                            │
│   信用额度    500,000.00                                          │
│   网站        https://www.abc.com                                 │
│   备注        重要客户，长期合作                                   │
│                                                                      │
│ 创建时间    2026-03-16 10:00                                       │
│ 更新时间    2026-03-16 10:00                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 八、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-16 | 初始版本，基于 Django 项目架构 |
| 1.1 | 2026-03-16 | 扩展客户字段至20个，包含企业信息、联系方式多组等 |
