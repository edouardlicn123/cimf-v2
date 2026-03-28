# 仙芙CIMF

<img src="./static/cimf.png" alt="Logo" width="50%">

企业级内部管理系统，AI开发。

> CIMF = Corporate Internal Management Framework，企业内部管理框架。

灵感来自 Drupal，通过 node、field、taxonomy 等功能实现 CRM 等系统的管理功能。

---

## 功能特点

- 🔐 **角色权限体系** - 经理/组长/员工三级权限管理，可精细控制节点操作权限
- 📊 **模块化节点系统** - 插件式模块架构，支持动态加载/卸载
- 📝 **24种自定义字段类型** - 文本、数字、布尔、文件、图片、邮箱、电话、日期、地理位置、颜色、身份识别、隐私脱敏等
- 🗂️ **词汇表管理** - 预置分类（国家、客户类型、行业、企业性质、客户等级等）
- 🗺️ **中国行政区划** - 省市县三级联动字段，支持级联选择
- 💧 **水印保护** - 网页动态水印 + 导出文件水印
- 📥 **数据导入导出** - 支持 CSV/Excel 格式，可自定义字段和过滤条件
- ⏰ **定时任务系统** - 可扩展的 Cron 任务（时间同步、缓存清理）
- 🧪 **完整测试覆盖** - 核心模块单元测试和集成测试
- 🏠 **首页快捷入口** - 3×2 卡片布局，支持拖拽自定义

---

## 目前已有模块

| 模块 | 类型 | 说明 |
|------|------|------|
| 客户信息（海外） | node | 海外客户信息管理，支持 20+ 字段，含 LinkedIn |
| 客户信息（国内） | node | 国内客户信息管理，支持省市县联动、微信/钉钉 |
| 时钟 | system | 时钟/日历展示，仪表盘快捷卡片 |

---

## 字段类型系统

项目提供 24 种自定义字段类型，可灵活配置：

| 类别 | 字段类型 |
|------|----------|
| 文本 | `string`, `string_long`, `text`, `text_long`, `text_with_summary` |
| 数值 | `boolean`, `integer`, `decimal`, `float` |
| 媒体 | `file`, `image` |
| 联系 | `link`, `email`, `telephone` |
| 时间 | `datetime`, `timestamp` |
| 特殊 | `geolocation`, `color`, `ai_tags`, `identity`, `masked`, `biometric`, `address`, `gis`, `entity_reference` |
| 中国 | `region_select` (省市区联动) |

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3.12 / Django 6.0 |
| 数据库 | SQLite |
| 模板 | Jinja2 |
| 测试 | Django TestCase |

---

## 快速开始

```bash
./run.sh
```

选择「1. 启动服务」默认运行在 http://localhost:8000  
默认账号：`admin` / `admin123`

---

## 项目结构

```
cimf-v2/
├── cimf_django/                  # Django 项目配置
│   ├── settings.py                # 主配置文件
│   ├── urls.py                    # 根 URL 配置
│   ├── jinja2.py                  # Jinja2 模板引擎配置
│   └── context_processors.py      # 模板上下文处理器
│
├── core/                         # 核心应用
│   ├── models.py                 # User, Taxonomy, ChinaRegion, SystemSetting
│   ├── views.py                  # 认证、仪表盘、管理页面
│   ├── urls.py                   # 核心 URL 路由
│   ├── forms/                    # 表单定义
│   │   ├── auth_forms.py         # 登录表单
│   │   ├── admin_forms.py        # 用户管理表单
│   │   └── settings_forms.py    # 系统设置表单
│   ├── admin.py                  # Django Admin 配置
│   ├── services/                 # 核心服务层
│   │   ├── auth_service.py       # 认证服务
│   │   ├── permission_service.py # 权限服务
│   │   ├── user_service.py       # 用户服务
│   │   ├── settings_service.py   # 系统设置服务
│   │   ├── taxonomy_service.py   # 词汇表服务
│   │   ├── china_region_service.py   # 行政区划服务
│   │   ├── cron_service.py       # 定时任务服务
│   │   ├── time_service.py       # 时间服务
│   │   ├── export_service.py     # 导出服务
│   │   └── import_service.py     # 导入服务
│   ├── node/                     # 节点核心系统
│   │   ├── models.py             # NodeType, Node, NodeModule
│   │   ├── services.py           # 节点类型服务、节点服务
│   │   └── views.py              # 节点管理视图
│   ├── importexport/             # 导入导出功能
│   │   ├── views.py              # 导入导出视图
│   │   └── services.py           # 导入导出服务
│   ├── fields/                   # 自定义字段类型 (24种)
│   │   ├── base.py
│   │   ├── string.py
│   │   ├── region_select.py      # 省市区联动
│   │   └── ... (其他字段类型)
│   └── templates/                # Jinja2 模板
│       ├── core/                 # 核心模板
│       │   ├── frames/           # 页面框架
│       │   ├── admin/            # 管理页面
│       │   ├── structure/        # 结构页面
│       │   ├── node/             # 节点模板
│       │   ├── importexport/     # 导入导出模板
│       │   └── usermenu/         # 用户菜单
│       └── includes/              # 模板片段
│
├── modules/                      # 业务模块 (plugins)
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py
│   ├── customer/                 # 客户（海外）模块
│   │   ├── module.py             # 模块信息
│   │   ├── models.py             # CustomerFields
│   │   ├── services.py           # 客户服务
│   │   ├── views.py              # 客户视图
│   │   ├── urls.py               # 客户路由
│   │   ├── forms.py              # 客户表单
│   │   └── templates/
│   ├── customer_cn/              # 客户（国内）模块
│   │   └── ...
│   └── clock/                    # 时钟模块
│       ├── module.py
│       ├── services.py
│       ├── views.py
│       └── templates/
│
├── static/                      # 静态资源 (CSS, JS, 图片)
├── docs/                        # 开发文档
│   ├── 技术规范/
│   │   ├── 02_模块技术规范.md
│   │   ├── 03_省市县联动字段技术规范.md
│   │   ├── 04_模板开发规范.md
│   │   └── 05_Python代码开发规范.md
│   ├── 开发规范.md
│   ├── bug排查规范.md
│   └── progress.md
│
├── run.sh                       # 项目启动脚本
├── manage.py                    # Django 管理脚本
├── init_db.py                   # 数据库初始化脚本
├── update_progress.py           # 进度更新脚本
└── README.md
```

---

## 文档说明

| 文档 | 说明 |
|------|------|
| [技术规范/02_模块技术规范.md](./docs/技术规范/02_模块技术规范.md) | 模块系统实现指南，包含首页卡片开发 |
| [技术规范/04_模板开发规范.md](./docs/技术规范/04_模板开发规范.md) | Jinja2 模板开发规范 |
| [技术规范/05_Python代码开发规范.md](./docs/技术规范/05_Python代码开发规范.md) | Python 代码开发规范 |
| [技术规范/03_省市县联动字段技术规范.md](./docs/技术规范/03_省市县联动字段技术规范.md) | 省市县三级联动字段设计 |
| [开发规范.md](./docs/开发规范.md) | 项目开发通用规范 |
| [bug排查规范.md](./docs/bug排查规范.md) | Bug 排查检查清单 |

---

## 开发命令

```bash
# 启动服务
./run.sh

# 运行测试
./venv/bin/python manage.py test

# 创建迁移
./venv/bin/python manage.py makemigrations

# 执行迁移
./venv/bin/python manage.py migrate

# Django 系统检查
./venv/bin/python manage.py check

# 创建超级用户
./venv/bin/python manage.py createsuperuser
```

---

## 许可证

MIT License

Copyright (c) 2024-2026 Xianfu CIMF

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
