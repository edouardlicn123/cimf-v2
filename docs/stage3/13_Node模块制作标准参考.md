# Node 模块制作标准参考

本文档提供创建新 Node 节点类型的通用标准指引，基于当前 Django 项目架构。

---

## 一、概述

Node 系统是一个灵活的节点类型管理框架，允许通过管理界面创建各种业务节点类型，每个节点类型可以配置不同的字段。

### 1.1 目录结构规范

根据 AGENTS.md 中的规范，Node 模块的目录结构如下：

```
nodes/                           # 节点应用
├── models.py                    # 节点模型（NodeType, Node, {Node}Fields）
├── views.py                    # 视图函数
├── urls.py                      # URL 路由配置
├── forms.py                     # 表单定义
├── admin.py                     # Django Admin 配置
├── apps.py                      # 应用配置
└── services/                    # 服务层
    ├── __init__.py
    ├── node_type_service.py    # 节点类型服务
    ├── node_service.py          # 节点主表服务
    └── {node_slug}_service.py   # 节点专用服务

templates/
├── nodes/                       # 节点模板
│   ├── index.html               # 事务总览
│   ├── types/                   # 节点类型管理
│   │   ├── index.html
│   │   └── edit.html
│   ├── field_types.html         # 字段类型列表
│   └── {node_slug}/             # 节点专用模板（如 customer/）
│       ├── list.html
│       ├── view.html
│       └── edit.html
└── core/
    └── frame_node.html          # 框架模板
```

### 1.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 节点类型机器名 | 小写字母和下划线 | `customer`, `project`, `order` |
| 目录名 | 与机器名一致 | `customer/` |
| 类名 | PascalCase | `CustomerService`, `CustomerForm` |
| 表名 | `{node_slug}_fields` | `customer_fields` |
| URL | `/nodes/{slug}/` | `/nodes/customer/` |

### 1.3 路由设计

| 路径 | 函数 | 说明 |
|------|------|------|
| `/nodes/` | `nodes:index` | 事务总览 |
| `/nodes/types/` | `nodes:node_types` | 节点类型管理 |
| `/nodes/types/create/` | `nodes:node_type_create` | 创建节点类型 |
| `/nodes/types/<id>/edit/` | `nodes:node_type_edit` | 编辑节点类型 |
| `/nodes/types/<id>/delete/` | `nodes:node_type_delete` | 删除节点类型 |
| `/nodes/field-types/` | `nodes:field_types` | 字段类型列表 |
| `/nodes/<slug>/` | `nodes:node_list` | 节点列表 |
| `/nodes/<slug>/create/` | `nodes:node_create` | 创建节点 |
| `/nodes/<slug>/<id>/` | `nodes:node_view` | 查看节点 |
| `/nodes/<slug>/<id>/edit/` | `nodes:node_edit` | 编辑节点 |
| `/nodes/<slug>/<id>/delete/` | `nodes:node_delete` | 删除节点 |

> **注意**：URL 中的 `<slug>` 是节点类型的标识符，`<id>` 是节点的主键（Node.id）。

---

## 二、系统预定义字段类型

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

**重要**：
- 系统字段类型位于 `core/fields/`
- 如需创建自定义字段类型，请参考 `core/fields/base.py` 中的 `BaseField` 基类

---

## 三、核心模块实现

### 3.1 模型层

#### 3.1.1 节点类型模型

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
```

#### 3.1.2 节点主表模型

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

#### 3.1.3 节点类型独立字段表

每个节点类型必须创建自己的字段模型。

**字段设计规范**：

1. **必须字段**：所有节点必须有 `node` 字段（OneToOneField 关联 Node）
2. **时间字段**：必须包含 `created_at` 和 `updated_at`
3. **字段分组建议**：
   - 基本信息：名称、代码、类型等
   - 联系方式：电话、邮箱等（可设置多个）
   - 地址信息：国家、省份、城市、地址、邮编
   - 企业信息：行业、性质、规模等
   - 其他：备注、等级等

**常用字段类型对照**：

| 业务需求 | 推荐字段类型 | 说明 |
|----------|--------------|------|
| 短文本 | CharField | 名称、代码等 |
| 长文本 | TextField | 备注、描述 |
| 邮箱 | EmailField | 带验证的邮箱 |
| 电话 | CharField | 电话号码 |
| 数字 | DecimalField | 金额、数量 |
| 是/否 | BooleanField | 开关状态 |
| 日期时间 | DateTimeField | 创建/更新时间 |
| 单选分类 | ForeignKey(TaxonomyItem) | 关联词汇表 |
| 多选分类 | ManyToManyField(TaxonomyItem) | 关联词汇表 |
| URL链接 | URLField | 网站链接 |

**模型模板**：

```python
# nodes/models.py
class {Node}Fields(models.Model):
    """{节点名称}字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='{node_slug}_fields',
        verbose_name='关联节点'
    )
    
    # ===== 基本信息 =====
    name = models.CharField(max_length=200, unique=True, verbose_name='名称')
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='代码')
    node_type = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='{node_slug}_by_type',
        verbose_name='类型'
    )
    
    # ===== 联系方式 =====
    phone1 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话1')
    email1 = models.EmailField(blank=True, null=True, verbose_name='邮箱1')
    phone2 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话2')
    email2 = models.EmailField(blank=True, null=True, verbose_name='邮箱2')
    
    # ===== 地址信息 =====
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='国家')
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='省份')
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='城市')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='邮编')
    
    # ===== 企业信息 =====
    industry = models.CharField(max_length=50, blank=True, null=True, verbose_name='行业')
    enterprise_type = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='{node_slug}_by_etype',
        verbose_name='企业性质'
    )
    registered_capital = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='注册资本')
    
    # ===== 其他 =====
    level = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='{node_slug}_by_level',
        verbose_name='等级'
    )
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='信用额度')
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name='网站')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    
    # ===== 时间戳 =====
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = '{node_slug}_fields'
        verbose_name = '{节点名称}'
        verbose_name_plural = '{节点名称}'
    
    def __str__(self):
        return self.name
```

### 3.2 服务层

#### 3.2.1 节点类型服务

`nodes/services/node_type_service.py` 已实现以下方法：

| 方法 | 说明 |
|------|------|
| `get_all()` | 获取所有已启用的节点类型 |
| `get_all_including_inactive()` | 获取所有节点类型（含禁用的） |
| `get_by_id(id)` | 根据 ID 获取 |
| `get_by_slug(slug)` | 根据 slug 获取 |
| `get_by_slug_including_inactive(slug)` | 获取（含禁用） |
| `create(data)` | 创建 |
| `update(id, data)` | 更新 |
| `delete(id)` | 删除（软删除） |
| `enable(id)` | 启用 |
| `disable(id)` | 禁用 |
| `get_node_count(id)` | 获取节点数量 |
| `init_default_node_types()` | 初始化预置节点类型 |

#### 3.2.2 节点服务

```python
# nodes/services/node_service.py
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

#### 3.2.3 节点专用服务

```python
# nodes/services/{node_slug}_service.py
class {Node}Service:
    """{节点名称}管理服务"""
    
    NODE_TYPE_SLUG = '{node_slug}'
    
    @staticmethod
    def get_node_type():
        return NodeTypeService.get_by_slug({Node}Service.NODE_TYPE_SLUG)
    
    @staticmethod
    def get_list(search: Optional[str] = None) -> List[{Node}Fields]:
        """获取列表"""
        queryset = {Node}Fields.objects.all()
        
        if search:
            # 添加搜索条件
            queryset = queryset.filter(
                Q(field1__icontains=search) |
                Q(field2__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(id: int) -> Optional[{Node}Fields]:
        """根据 ID 获取"""
        return {Node}Fields.objects.filter(id=id).first()
    
    @staticmethod
    def get_by_node_id(node_id: int) -> Optional[{Node}Fields]:
        """根据节点 ID 获取"""
        return {Node}Fields.objects.filter(node_id=node_id).first()
    
    @staticmethod
    def create(user, data: Dict[str, Any]) -> {Node}Fields:
        """创建{节点名称}"""
        node = NodeService.create({Node}Service.NODE_TYPE_SLUG, user, {})
        
        {node} = {Node}Fields.objects.create(
            node=node,
            # 字段映射...
        )
        
        return {node}
    
    @staticmethod
    def update(id: int, data: Dict[str, Any]) -> Optional[{Node}Fields]:
        """更新{节点名称}"""
        {node} = {Node}Fields.objects.filter(id=id).first()
        if not {node}:
            return None
        
        for key, value in data.items():
            if hasattr({node}, key) and key != 'id' and key != 'node':
                setattr({node}, key, value)
        
        {node}.save()
        return {node}
    
    @staticmethod
    def delete(id: int) -> bool:
        """删除{节点名称}"""
        {node} = {Node}Fields.objects.filter(id=id).first()
        if {node}:
            node = {node}.node
            {node}.delete()
            if node:
                node.delete()
            return True
        return False
```

### 3.3 视图层

节点视图采用通用路由设计，根据 `node_type_slug` 区分不同节点类型：

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
    
    # 根据节点类型分发到不同的服务
    if node_type_slug == '{node_slug}':
        items = {Node}Service.get_list(search if search else None)
        return render(request, 'nodes/{node_slug}/list.html', {
            'node_type': node_type,
            'node_types': node_types,
            'items': items,
            'search': search,
            'active_section': node_type_slug,
        })
    
    # 其他节点类型...


@login_required
def node_create(request, node_type_slug: str):
    """创建节点"""
    # 类似实现...


@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """查看节点"""
    # 类似实现...


@login_required
def node_edit(request, node_type_slug: str, node_id: int):
    """编辑节点"""
    # 类似实现...


@login_required
def node_delete(request, node_type_slug: str, node_id: int):
    """删除节点"""
    # 类似实现...
```

### 3.4 URL 配置

```python
# nodes/urls.py
from django.urls import path
from . import views

app_name = 'nodes'

urlpatterns = [
    # 节点类型管理
    path('types/', views.node_types, name='node_types'),
    path('type/create/', views.node_type_create, name='node_type_create'),
    path('type/<int:node_type_id>/edit/', views.node_type_edit, name='node_type_edit'),
    path('type/<int:node_type_id>/delete/', views.node_type_delete, name='node_type_delete'),
    
    # 字段类型
    path('field-types/', views.field_types, name='field_types'),
    path('api/field-types/', views.field_types_api, name='field_types_api'),
    
    # 节点 CRUD（通用路由）
    path('', views.nodes_index, name='index'),
    path('<slug:node_type_slug>/', views.node_list, name='node_list'),
    path('<slug:node_type_slug>/create/', views.node_create, name='node_create'),
    path('<slug:node_type_slug>/<int:node_id>/', views.node_view, name='node_view'),
    path('<slug:node_type_slug>/<int:node_id>/edit/', views.node_edit, name='node_edit'),
    path('<slug:node_type_slug>/<int:node_id>/delete/', views.node_delete, name='node_delete'),
]
```

### 3.5 模板层

#### 3.5.1 框架模板

`templates/core/frame_node.html` 是节点管理的基础框架：

```html
{% extends "base.html" %}

{% block content %}
<div class="d-flex flex-column" style="min-height: 100vh;">
  <div class="d-flex flex-grow-1">
    <!-- 左侧导航栏 -->
    <nav class="admin-sidebar ...">
      <ul class="nav flex-column mb-auto">
        <li class="nav-item">
          <a class="nav-link ... {% if active_section == 'dashboard' %}active{% endif %}" 
             href="{{ url('nodes:index') }}">
            <i class="bi bi-grid me-2 fs-6"></i>
            事务总览
          </a>
        </li>
        
        <!-- 动态加载已启用的节点入口 -->
        {% for nt in node_types %}
        <li class="nav-item">
          <a class="nav-link ... {% if active_section == nt.slug %}active{% endif %}" 
             href="{{ url('nodes:node_list', nt.slug) }}">
            <i class="bi {{ nt.icon|default('bi-folder') }} me-2 fs-6"></i>
            {{ nt.name }}
          </a>
        </li>
        {% endfor %}
      </ul>
    </nav>
    
    <!-- 右侧主内容区 -->
    <div class="flex-grow-1 overflow-auto px-4 pt-2">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h1 class="h2 mb-0">{% block admin_title %}{% endblock %}</h1>
        <div>{% block admin_title_buttons %}{% endblock %}</div>
      </div>
      
      <div class="pb-4">
        {% block admin_content %}{% endblock %}
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

#### 3.5.2 节点列表模板

```html
<!-- templates/nodes/{node_slug}/list.html -->
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
                            <th>字段1</th>
                            <th>字段2</th>
                            <th>字段3</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            <td>{{ item.field1 }}</td>
                            <td>{{ item.field2|default('-') }}</td>
                            <td>{{ item.field3|default('-') }}</td>
                            <td>{{ item.created_at|date('Y-m-d H:i') }}</td>
                            <td>
                                <a href="{{ url('nodes:node_view', node_type.slug, item.node_id) }}" class="btn btn-sm btn-outline-primary">查看</a>
                                <a href="{{ url('nodes:node_edit', node_type.slug, item.node_id) }}" class="btn btn-sm btn-outline-secondary">编辑</a>
                                <a href="{{ url('nodes:node_delete', node_type.slug, item.node_id) }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定删除?')">删除</a>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="5" class="text-center text-muted">暂无数据</td>
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

#### 3.5.3 节点详情模板

```html
<!-- templates/nodes/{node_slug}/view.html -->
{% extends "core/frame_node.html" %}

{% set show_nav = true %}
{% set show_header = false %}

{% block admin_title %}
  {{ item.field1 }}
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
                <label class="form-label text-muted">字段1</label>
                <p class="mb-0">{{ item.field1 }}</p>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label text-muted">字段2</label>
                <p class="mb-0">{{ item.field2|default('-') }}</p>
            </div>
            <!-- 更多字段... -->
        </div>
    </div>
</div>
{% endblock %}
```

#### 3.5.4 节点编辑模板

```html
<!-- templates/nodes/{node_slug}/edit.html -->
{% extends "core/frame_node.html" %}

{% set show_nav = true %}
{% set show_header = false %}

{% block admin_title %}
  {% if item %}编辑{% else %}新建{% endif %}{{ node_type.name }}
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
                <label class="form-label">字段1 *</label>
                <input type="text" name="field1" class="form-control" value="{{ item.field1|default('') }}" required>
            </div>
            <div class="mb-3">
                <label class="form-label">字段2</label>
                <input type="text" name="field2" class="form-control" value="{{ item.field2|default('') }}">
            </div>
            <!-- 更多字段... -->
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

## 四、创建新节点类型步骤

### 步骤 1：设计字段

在创建模型前，先设计字段分组：

| 分组 | 示例字段 |
|------|----------|
| 基本信息 | name, code, type |
| 联系方式 | phone1/2, email1/2 |
| 地址信息 | country, province, city, address, postal_code |
| 企业信息 | industry, enterprise_type, registered_capital |
| 其他 | level, credit_limit, website, notes |

### 步骤 2：创建字段模型

在 `nodes/models.py` 中添加节点字段模型：

```python
class {Node}Fields(models.Model):
    """{节点名称}字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='{node_slug}_fields',
        verbose_name='关联节点'
    )
    
    # 基本信息
    name = models.CharField(max_length=200, unique=True, verbose_name='名称')
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='代码')
    node_type = models.ForeignKey('core.TaxonomyItem', ...)
    
    # 联系方式
    phone1 = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话1')
    email1 = models.EmailField(blank=True, null=True, verbose_name='邮箱1')
    
    # 地址信息
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='国家')
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='省份')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='邮编')
    
    # 其他
    level = models.ForeignKey('core.TaxonomyItem', ...)
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = '{node_slug}_fields'
```

### 步骤 2：创建服务文件

创建 `nodes/services/{node_slug}_service.py`：

```python
# -*- coding: utf-8 -*-
"""
{节点名称}服务
"""

from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from nodes.models import Node, {Node}Fields
from nodes.services import NodeService, NodeTypeService

User = get_user_model()


class {Node}Service:
    """{节点名称}管理服务"""
    
    NODE_TYPE_SLUG = '{node_slug}'
    
    # 实现 CRUD 方法（参考 3.2.3 节）
```

### 步骤 3：更新服务入口

`nodes/services/__init__.py`：

```python
from .node_type_service import NodeTypeService
from .node_service import NodeService
from .{node_slug}_service import {Node}Service
```

### 步骤 4：更新视图

在 `nodes/views.py` 中添加节点类型的视图处理：

```python
# 参考 3.3 节实现
```

### 步骤 5：创建模板

创建以下模板文件：
- `templates/nodes/{node_slug}/list.html`
- `templates/nodes/{node_slug}/view.html`
- `templates/nodes/{node_slug}/edit.html`

### 步骤 6：创建数据库表

```bash
python manage.py makemigrations nodes
python manage.py migrate nodes
```

### 步骤 7：启用节点类型

1. 访问 `/nodes/types/`
2. 找到对应的节点类型，点击"启用"按钮

---

## 五、动态加载机制

系统支持在节点类型启用/禁用时自动更新以下位置的显示：

### 5.1 节点数据传递

在每个节点视图函数中，通过 `NodeTypeService.get_all()` 获取已启用的节点类型并传递到模板：

```python
# nodes/views.py
@login_required
def nodes_index(request):
    """节点首页 - 显示所有节点类型"""
    node_types = NodeTypeService.get_all()
    return render(request, 'nodes/index.html', {
        'node_types': node_types,
        'active_section': 'dashboard',
    })
```

### 5.2 侧边栏动态加载

`templates/core/frame_node.html` 自动加载已启用的节点入口：

```html
{% for nt in node_types %}
<li class="nav-item">
  <a class="nav-link ... {% if active_section == nt.slug %}active{% endif %}" 
     href="{{ url('nodes:node_list', nt.slug) }}">
    <i class="bi {{ nt.icon|default('bi-folder') }} me-2 fs-6"></i>
    {{ nt.name }}
  </a>
</li>
{% endfor %}
```

### 5.3 事务总览 Dashboard

`templates/nodes/index.html` 自动加载节点卡片：

```html
{% for nt in node_types %}
<div class="col-md-6 col-lg-4">
  <div class="card h-100">
    <div class="card-body">
      <h5 class="card-title">
        <i class="bi {{ nt.icon|default('bi-folder') }} me-2"></i>
        {{ nt.name }}
      </h5>
      <p class="card-text text-muted small">
        {{ nt.description|default('暂无描述') }}
      </p>
      <a href="{{ url('nodes:node_list', nt.slug) }}" class="btn btn-outline-primary btn-sm">
        管理
      </a>
    </div>
  </div>
</div>
{% endfor %}
```

---

## 六、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-16 | 初始版本，基于 Django 项目架构 |
| 1.1 | 2026-03-16 | 添加字段设计规范，包含分组建议和常用字段类型对照 |
