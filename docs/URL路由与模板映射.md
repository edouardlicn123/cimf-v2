# URL 路由与模板映射

> 生成日期：2026-05-03  
> 数据来源：core/urls.py, core/node/urls.py, modules/urls.py, core/importexport/urls.py, cimf_django/urls.py, core/views/*, core/node/views.py, core/importexport/views.py

---

## 一、个人中心

| 路径 | URL Name | 模板 |
|------|----------|------|
| `user/profile/` | `core:profile_view` | `usermenu/profile.html` |
| `user/settings/` | `core:profile_settings` | `usermenu/settings.html` |
| `user/functioncards/` | `core:homepage_settings` | `usermenu/homepage_settings.html` |
| `user/navcards/` | `core:navigation_settings` | `nav_cards/settings.html` |

## 二、模块管理

| 路径 | URL Name | 模板 |
|------|----------|------|
| `/node/` | `node:index` | `node/node_dashboard.html` |
| `/node/types/` | `node:node_types_list` | `node/node_types_list.html` |
| `/node/modules/` | `node:modules` | `node/modules.html` |
| `modules/manage/` | `core:modules_manage` | `node/modules.html` |

## 三、字段类型

| 路径 | URL Name | 模板 |
|------|----------|------|
| `modules/field-types/` | `modules:field_types` | `node/field_types.html` |

---

## 附录：其他路由分类（供参考）

### 认证

| 路径 | URL Name | 模板 |
|------|----------|------|
| `accounts/login/` | `core:login` | `auth/login.html` |
| `accounts/logout/` | `core:logout` | （仅跳转） |

### 管理后台

| 路径 | URL Name | 模板 |
|------|----------|------|
| `system/` | `core:admin_dashboard` | `admin/dashboard.html` |
| `system/users/` | `core:system_users` | `admin/system_users.html` |
| `system/user/create/` | `core:user_create` | `admin/system_user_edit.html` |
| `system/user/<id>/edit/` | `core:user_edit` | `admin/system_user_edit.html` |
| `system/settings/` | `core:system_settings` | `admin/system_settings.html` |
| `system/permissions/` | `core:system_permissions` | `admin/system_permissions.html` |
| `system/cron/` | `core:cron_manager` | `admin/system_cron_manager.html` |
| `system/permission-check/` | `core:permission_check` | `admin/permission_check.html` |
| `system/smtp/` | `core:smtp_config` | `smtp/config.html` |
| `system/smtp/history/` | `core:smtp_history` | `smtp/history.html` |
| `system/logs/` | `core:logs_index` | `admin/logs.html` |
| `system/logs/<type>/` | `core:logs_view` | `admin/logs.html` |

### 仪表盘/首页/工具

| 路径 | URL Name | 模板 |
|------|----------|------|
| `/` | `core:dashboard` | `indexdashboard.html` |
| `tools/` | `core:tools_index` | `tools/tools_dashboard.html` |
| `structure/` | `core:structure_dashboard` | `structure/structure_dashboard.html` |

### 词汇表

| 路径 | URL Name | 模板 |
|------|----------|------|
| `taxonomies/` | `core:taxonomies` | `structure/taxonomies/index.html` |
| `taxonomy/<id>/` | `core:taxonomy_view` | `structure/taxonomies/view.html` |
| `taxonomy/<id>/edit/` | `core:taxonomy_edit` | `structure/taxonomies/edit.html` |
| `taxonomy/create/` | `core:taxonomy_create` | `structure/taxonomies/edit.html` |

### 导入导出

| 路径 | URL Name | 模板 |
|------|----------|------|
| `importexport/` | `importexport:importexport_dashboard` | `importexport/importexport_dashboard.html` |
| `importexport/export/` | `importexport:export_list` | `importexport/export.html` |
| `importexport/export/<slug>/` | `importexport:export_select_fields` | `importexport/export_fields.html` |
| `importexport/export/<slug>/confirm/` | `importexport:export_confirm` | `importexport/export_confirm.html` |
| `importexport/export/<slug>/exporting/` | `importexport:export_exporting` | `importexport/export_exporting.html` |
| `importexport/import/` | `importexport:import_list` | `importexport/import.html` |
| `importexport/import/<slug>/` | `importexport:import_page` | `importexport/import_page.html` |
| `importexport/import/<slug>/template/` | `importexport:download_template` | （文件下载） |
| `importexport/import/<slug>/upload/` | `importexport:upload_preview` | `importexport/import_page.html` |
| `importexport/import/<slug>/do/` | `importexport:do_import` | `importexport/import_result.html` |
| `importexport/import/<slug>/errors/` | `importexport:download_errors` | （文件下载） |

### 模块市场

| 路径 | URL Name | 模板 |
|------|----------|------|
| `market/` | `market:index` | `marketplace/index.html` |

### 动态模块路由

| 模块 | 路径 | URL Name | 模板 |
|------|------|----------|------|
| customer | `modules/customer/` | `customer:list` | `list.html` |
| customer | `modules/customer/create/` | `customer:create` | `edit.html` |
| customer | `modules/customer/<id>/` | `customer:view` | `view.html` |
| customer | `modules/customer/<id>/edit/` | `customer:edit` | `edit.html` |
| calc | `modules/calc/` | `calc:calc` | `calc/calc.html` |

### 节点 CRUD

| 路径 | URL Name | 模板 |
|------|----------|------|
| `/node/<slug>/create/` | `node:node_create` | `node/node_edit.html` |
| `/node/<slug>/<id>/` | `node:node_view` | （动态分发） |
| `/node/<slug>/<id>/edit/` | `node:node_edit` | （动态分发） |
| `/node/<slug>/` | `node:module_page` | （动态分发） |

### 错误页面

| 状态 | 模板 |
|------|------|
| 400 | `errors/400.html` |
| 403 | `errors/403.html` |
| 404 | `errors/404.html` |
| 500 | `errors/500.html` |
