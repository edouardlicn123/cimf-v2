# 仙芙CIMF

<img src="./static/cimf.png" alt="Logo" width="50%">

企业级内部管理系统，AI开发。

> CIMF = Corporate Internal Management Framework，企业内部管理框架。

灵感来自Drupal，通过node、field、taxnomy等功能实现CRM等系统的管理功能。

---

## 功能特点

- 🔐 **角色权限体系** - 经理/组长/员工三级权限管理，可精细控制节点操作权限
- 📊 **可扩展的节点系统** - 如客户管理、会员管理、居民信息管理、项目管理等
- 📝 **24种自定义字段类型** - 文本、数字、布尔、文件、图片、邮箱、电话、日期、地理位置、颜色、身份识别、隐私脱敏等
- 🗂️ **词汇表管理** - 37个预置分类（国家、客户类型、行业、企业性质、客户等级等）
- 🗺️ **中国行政区划** - 省市县三级联动字段，支持级联选择
- 💧 **水印保护** - 网页动态水印 + 导出文件水印
- 📥 **数据导入导出** - 支持 CSV/Excel 格式，可自定义字段和过滤条件
- ⏰ **定时任务系统** - 可扩展的 Cron 任务（时间同步、缓存清理）
- 🧪 **完整测试覆盖** - 核心模块单元测试和集成测试

---

## 目前已有模块

| 模块 | 说明 |
|------|------|
| 客户管理（海外） | 海外客户信息管理，支持 20+ 字段 |
| 客户管理（国内） | 国内客户信息管理，支持省市县联动、微信/钉钉联系方式 |

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
├── cimf_django/              # Django 项目配置
│   ├── settings.py           # 主配置文件
│   ├── urls.py               # 根 URL 配置
│   ├── jinja2.py             # Jinja2 模板引擎配置
│   └── context_processors.py # 模板上下文处理器
│
├── core/                     # 核心应用
│   ├── models.py             # User, Taxonomy, ChinaRegion, SystemSetting
│   ├── views.py              # 认证、仪表盘、管理页面
│   ├── urls.py               # 核心 URL 路由
│   ├── forms.py              # 登录表单等
│   ├── admin.py              # Django Admin 配置
│   ├── services/            # 核心服务层
│   │   ├── auth_service.py           # 认证服务
│   │   ├── permission_service.py    # 权限服务
│   │   ├── user_service.py          # 用户服务
│   │   ├── settings_service.py      # 系统设置服务
│   │   ├── taxonomy_service.py      # 词汇表服务
│   │   ├── china_region_service.py  # 行政区划服务
│   │   ├── cron_service.py          # 定时任务服务
│   │   └── tasks/                    # 定时任务实现
│   └── fields/              # 自定义字段类型 (24种)
│       ├── base.py
│       ├── string.py
│       ├── text.py
│       ├── integer.py
│       ├── boolean.py
│       ├── file.py
│       ├── image.py
│       ├── email.py
│       ├── telephone.py
│       ├── datetime.py
│       ├── region_select.py   # 省市区联动
│       └── ... (其他字段类型)
│
├── nodes/                    # 节点应用
│   ├── models.py             # NodeType, Node, CustomerFields, CustomerCnFields
│   ├── views.py             # 节点 CRUD、导入导出视图
│   ├── urls.py               # 节点 URL 路由
│   ├── forms.py             # 通用表单
│   ├── admin.py             # Django Admin 配置
│   ├── services/            # 节点服务层
│   │   ├── node_type_service.py
│   │   ├── node_service.py
│   │   ├── customer_service.py      # 海外客户服务
│   │   ├── customer_cn_service.py   # 国内客户服务
│   │   ├── export_service.py        # 导出服务
│   │   ├── import_service.py        # 导入服务
│   │   └── template_generator.py   # 导入模板生成
│   └── customer/
│       └── forms.py          # 客户专用表单
│
├── templates/                # Jinja2 模板
│   ├── core/                # 核心模板
│   │   ├── frames/          # 页面框架 (frame_*)
│   │   ├── admin/           # 管理页面
│   │   └── structure/       # 结构页面 (taxonomies, importexport)
│   └── nodes/               # 节点模板
│       ├── types/           # 节点类型管理
│       ├── customer/        # 海外客户
│       └── customer_cn/     # 国内客户
│
├── static/                   # 静态资源 (CSS, JS, 图片)
├── docs/                    # 开发文档
│   ├── 技术规范/            # 技术规范文档
│   │   ├── 02_Node模块技术规范.md
│   │   ├── 03_省市县联动字段技术规范.md
│   │   ├── 04_模板开发规范.md
│   │   └── 05_Python代码开发规范.md
│   ├── 开发规范.md
│   ├── bug排查规范.md
│   └── progress.md
│
├── venv/                    # Python 虚拟环境
├── run.sh                   # 项目启动脚本
├── manage.py                # Django 管理脚本
└── README.md
```

---

## 文档说明

项目提供完整的技术文档：

| 文档 | 说明 |
|------|------|
| [技术规范/04_模板开发规范.md](./docs/技术规范/04_模板开发规范.md) | Jinja2 模板开发规范，包含语法差异、片段库、命名规范、反模式 |
| [技术规范/05_Python代码开发规范.md](./docs/技术规范/05_Python代码开发规范.md) | Python 代码开发规范，包含 Model/Service/View 规范、测试、迁移、定时任务 |
| [技术规范/02_Node模块技术规范.md](./docs/技术规范/02_Node模块技术规范.md) | Node 节点类型系统的实现指南 |
| [技术规范/03_省市县联动字段技术规范.md](./docs/技术规范/03_省市县联动字段技术规范.md) | 省市县三级联动字段的设计与使用 |
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