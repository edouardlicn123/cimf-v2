# core/urls 路由与模块化规范

> 文档版本：1.1  
> 创建日期：2026-04-07  
> 最后更新：2026-05-03

---

## 一、概述

### 1.1 模块定位

URL 路由层负责将 HTTP 请求映射到对应的视图函数，是请求入口的第一层分发。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **RESTful** | 使用语义化的 URL 路径 |
| **命名规范** | 使用 `name='...'` 为每个路由命名，便于 `{% url %}` 标签调用 |
| **分组管理** | 按功能模块分组，使用前缀区分 |
| **路径前缀** | 管理后台使用 `/system/`，API 使用 `/api/` |

---

## 二、路由分布

### 2.1 主路由文件

| 文件 | 路由数量 | 功能 |
|------|----------|------|
| `core/urls.py` | ~30 | 核心应用路由（认证、管理后台、词汇表、API） |
| `core/node/urls.py` | ~15 | 节点系统路由 |
| `core/smtp/urls.py` | ~5 | 邮件系统路由 |
| `core/importexport/urls.py` | ~13 | 导入导出路由 |
| `core/marketplace/urls.py` | ~2 | 模块市场路由 |
| `modules/urls.py` | 动态 | 模块动态路由（从数据库加载） |

### 2.2 根 URL 配置

在 `cimf_django/urls.py` 中 include 所有子路由：

```python
from django.urls import path, include
from core.importexport.urls import urlpatterns_all as importexport_urls

urlpatterns = [
    # Core 应用路由
    path('', include('core.urls', namespace='core')),
    
    # Node 应用路由
    path('node/', include('core.node.urls', namespace='node')),
    
    # SMTP 应用路由
    path('smtp/', include('core.smtp.urls')),
    
    # 导入导出路由（统一使用 importexport 命名空间）
    path('importexport/', include((importexport_urls, 'importexport'), namespace='importexport')),
    
    # 模块动态路由
    path('modules/', include('modules.urls')),
]
```

---

## 三、core/urls.py 路由清单

### 3.1 认证路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `accounts/login/` | login_view | login | 用户登录 |
| `accounts/logout/` | logout_view | logout | 用户登出 |

### 3.2 管理后台路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `system/` | admin_dashboard | admin_dashboard | 管理后台仪表盘 |
| `system/users/` | system_users | system_users | 用户列表 |
| `system/user/create/` | user_create | user_create | 创建用户 |
| `system/user/<int:user_id>/edit/` | user_edit | user_edit | 编辑用户 |
| `system/user/<int:user_id>/delete/` | user_delete | user_delete | 删除用户 |
| `system/settings/` | system_settings | system_settings | 系统设置 |
| `system/permissions/` | system_permissions | system_permissions | 权限管理 |
| `system/cron/` | cron_manager | cron_manager | 定时任务管理 |
| `system/permission-check/` | permission_check | permission_check | 权限检查 |

### 3.3 邮件配置路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `system/smtp/` | smtp_config | smtp_config | SMTP 配置 |
| `system/smtp/test/` | smtp_test | smtp_test | 测试邮件 |
| `system/smtp/history/` | smtp_history | smtp_history | 发送历史 |
| `system/smtp/cleanup/` | smtp_cleanup_logs | smtp_cleanup_logs | 清理日志 |

### 3.4 Cron API 路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `api/cron/status/` | cron_status | cron_status | 任务状态 |
| `api/cron/run/<str:task_name>/` | cron_run_task | cron_run_task | 执行任务 |
| `api/cron/toggle/<str:task_name>/` | cron_toggle_task | cron_toggle_task | 切换任务 |

### 3.5 词汇表路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `taxonomies/` | taxonomies | taxonomies | 词汇表列表 |
| `taxonomy/create/` | taxonomy_create | taxonomy_create | 创建词汇表 |
| `taxonomy/<int:taxonomy_id>/` | taxonomy_view | taxonomy_view | 查看词汇表 |
| `taxonomy/<int:taxonomy_id>/edit/` | taxonomy_edit | taxonomy_edit | 编辑词汇表 |
| `taxonomy/<int:taxonomy_id>/delete/` | taxonomy_delete | taxonomy_delete | 删除词汇表 |
| `taxonomy/<int:taxonomy_id>/item/create/` | taxonomy_item_create | taxonomy_item_create | 创建词汇项 |
| `taxonomy/<int:taxonomy_id>/item/<int:item_id>/edit/` | taxonomy_item_update | taxonomy_item_update | 编辑词汇项 |
| `taxonomy/<int:taxonomy_id>/item/<int:item_id>/delete/` | taxonomy_item_delete | taxonomy_item_delete | 删除词汇项 |

### 3.6 内容结构路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `structure/` | structure_dashboard | structure_dashboard | 内容结构仪表盘 |

### 3.7 导入导出路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `importexport/` | importexport_dashboard | `importexport:importexport_dashboard` | 导入导出仪表盘 |
| `importexport/export/` | export_list | `importexport:export_list` | 导出列表 |
| `importexport/export/<slug:node_type_slug>/` | export_select_fields | `importexport:export_select_fields` | 选择导出字段 |
| `importexport/export/<slug:node_type_slug>/confirm/` | export_confirm | `importexport:export_confirm` | 确认导出 |
| `importexport/export/<slug:node_type_slug>/exporting/` | export_exporting | `importexport:export_exporting` | 导出中页面 |
| `importexport/export/<slug:node_type_slug>/do/` | do_export | `importexport:do_export` | 执行导出 |
| `importexport/import/` | import_list | `importexport:import_list` | 导入列表 |
| `importexport/import/<slug:node_type_slug>/` | import_page | `importexport:import_page` | 导入页面 |
| `importexport/import/<slug:node_type_slug>/template/` | download_template | `importexport:download_template` | 下载模板 |
| `importexport/import/<slug:node_type_slug>/upload/` | upload_preview | `importexport:upload_preview` | 上传预览 |
| `importexport/import/<slug:node_type_slug>/do/` | do_import | `importexport:do_import` | 执行导入 |
| `importexport/import/<slug:node_type_slug>/errors/` | download_errors | `importexport:download_errors` | 下载错误 |

### 3.8 个人中心路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `/` (空路径) | dashboard | dashboard | 仪表盘 |
| `user/profile/` | profile_view | profile_view | 个人资料 |
| `user/settings/` | profile_settings | profile_settings | 个人设置 |
| `user/functioncards/` | homepage_settings | homepage_settings | 首页设置 |
| `user/navcards/` | navigation_settings | navigation_settings | 导航卡片设置 |
| `api/user/nav-cards/` | api_nav_cards | api_nav_cards | 导航卡片 |
| `api/user/nav-cards/save/` | api_nav_cards_save | api_nav_cards_save | 保存导航 |

### 3.9 时间 API 路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `api/time/current/` | api_time_current | api_time_current | 当前时间 |
| `api/time/test/` | api_time_test | api_time_test | 测试时间同步 |
| `api/time/status/` | api_time_status | api_time_status | 同步状态 |

### 3.10 行政区划 API 路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `api/regions/provinces/` | api_regions_provinces | api_regions_provinces | 省份列表 |
| `api/regions/cities/` | api_regions_cities | api_regions_cities | 城市列表 |
| `api/regions/districts/` | api_regions_districts | api_regions_districts | 区县列表 |
| `api/regions/search/` | api_regions_search | api_regions_search | 搜索 |
| `api/regions/path/` | api_regions_path | api_regions_path | 完整路径 |
| `api/regions/stats/` | api_regions_stats | api_regions_stats | 统计 |

### 3.11 用户功能 API 路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `api/user/dashboard/cards/` | api_dashboard_cards | api_dashboard_cards | 仪表盘卡片 |
| `api/user/dashboard/cards/save/` | api_dashboard_cards_save | api_dashboard_cards_save | 保存卡片 |
| `api/user/nav-cards/` | api_nav_cards | api_nav_cards | 导航卡片 |
| `api/user/nav-cards/save/` | api_nav_cards_save | api_nav_cards_save | 保存导航 |

---

## 四、URL 命名规范

### 4.1 命名空间

在 `urls.py` 中定义 `app_name`：

```python
# core/urls.py
app_name = 'core'
```

### 4.2 模板中使用

```html
<!-- 跳转链接 -->
<a href="{% url 'core:system_users' %}">用户管理</a>

<!-- 表单提交 -->
<form action="{% url 'core:user_create' %}" method="post">

<!-- 命名空间嵌套 -->
<a href="{% url 'core:taxonomy_view' taxonomy.id %}">
```

### 4.3 视图中使用

```python
from django.urls import reverse

# 重定向
return redirect('core:system_users')

# 反向解析
url = reverse('core:taxonomy_view', args=[taxonomy_id])
```

---

## 五、路径分组规范

### 5.1 前缀约定

| 前缀 | 用途 | 示例 |
|------|------|------|
| `/system/` | 管理后台 | `/system/users/`, `/system/settings/` |
| `/api/` | API 接口 | `/api/time/current/`, `/api/regions/provinces/` |
| `/importexport/` | 导入导出 | `/importexport/export/`, `/importexport/import/` |
| `/taxonomy/` | 词汇表 | `/taxonomy/create/`, `/taxonomy/1/edit/` |
| `/user/` | 个人中心 | `/user/profile/`, `/user/settings/` |
| `/modules/manage/` | 模块管理 | `/modules/manage/` |

### 5.2 路径层级

```
/system/              → 管理后台根
  ├── users/          → 用户管理
  ├── user/create/    → 创建用户
  ├── user/<id>/edit/ → 编辑用户
  ├── settings/        → 系统设置
  ├── permissions/     → 权限管理
  └── smtp/            → 邮件配置
```

---

## 六、动态路由

### 6.1 模块动态加载

`modules/urls.py` 支持动态注册模块路由：

```python
# 动态添加模块路由
for module in installed_modules:
    if hasattr(module, 'urlpatterns'):
        urlpatterns += module.urlpatterns
```

### 6.2 节点动态路由

`core/node/urls.py` 支持动态节点类型路由：

```python
# 节点列表动态路由
path('<str:node_type_slug>/', node_list, name='node_list'),
path('<str:node_type_slug>/create/', node_create, name='node_create'),
path('<str:node_type_slug>/<int:node_id>/', node_view, name='node_view'),
```

---

## 七、错误处理配置

### 7.1 全局错误处理器

在 `cimf_django/urls.py` 中配置：

```python
handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
```

### 7.2 错误视图

| 状态码 | 视图函数 | 说明 |
|--------|----------|------|
| 400 | error_400 | Bad Request |
| 403 | error_403 | Permission Denied |
| 404 | error_404 | Not Found |
| 500 | error_500 | Internal Server Error |

---

## 八、待补充

- [ ] 添加路由测试规范
- [ ] 补充 API 版本管理建议
