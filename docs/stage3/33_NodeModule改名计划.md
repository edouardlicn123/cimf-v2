# NodeModule 改名为 Module 计划

## 一、背景

随着模块系统概念的演进，`NodeModule` 这一历史遗留命名已不再适应当前架构：
- `NodeModule` 曾指代"模块注册表"
- 现在只有"模块（Module）"概念，通过 `module_type` 字段区分类型（node/system）

本次修改将 `NodeModule` 正式更名为 `Module`，与业务概念保持一致。

---

## 二、修改目标

| 原名称 | 新名称 | 说明 |
|--------|--------|------|
| `NodeModule` | `Module` | 模型类名 |
| `node_modules` | `modules` | 数据库表名 |
| `NodeModuleService` | `ModuleService` | 服务类名 |

---

## 三、涉及文件清单

### 3.1 核心模型层

| 文件 | 修改内容 |
|------|----------|
| `core/node/models.py` | 类名 `NodeModule` → `Module`，设置 `db_table='modules'` |

### 3.2 服务层

| 文件 | 修改内容 |
|------|----------|
| `core/node/services.py` | 类名 `NodeModuleService` → `ModuleService` |

### 3.3 视图层

| 文件 | 修改内容 |
|------|----------|
| `core/node/views.py` | 引用 `NodeModule` → `Module` |
| `core/views.py` | 引用 `NodeModule` → `Module` |

### 3.4 其他引用

| 文件 | 修改内容 |
|------|----------|
| `core/services/permission_service.py` | 引用 `NodeModule` → `Module` |
| `run.py` | 引用 `NodeModuleService` → `ModuleService` |
| `init_db.py` | 引用 `NodeModuleService` → `ModuleService` |

### 3.5 数据库迁移

| 文件 | 说明 |
|------|------|
| `core/migrations/` | 创建迁移修改表名（从 `node_modules` 到 `modules`） |

---

## 四、详细修改步骤

### 步骤 1：修改核心模型（core/node/models.py）

```python
# 原
class NodeModule(models.Model):
    class Meta:
        db_table = 'node_modules'

# 改为
class Module(models.Model):
    class Meta:
        db_table = 'modules'
```

### 步骤 2：修改服务层（core/node/services.py）

- 类名：`NodeModuleService` → `ModuleService`
- 所有方法内的 `NodeModule.objects` → `Module.objects`

### 步骤 3：更新视图层引用

- `core/node/views.py`：所有 `NodeModule` → `Module`
- `core/views.py`：所有 `NodeModule` → `Module`

### 步骤 4：更新其他引用

- `core/services/permission_service.py`
- `run.py`
- `init_db.py`

### 步骤 5：创建数据库迁移

使用 Django 迁移修改表名，或直接在 Meta 中设置 `db_table` 参数。

### 步骤 6：验证测试

- 启动服务验证模块扫描功能正常
- 验证模块安装/启用/禁用功能正常
- 验证权限管理页面正常显示

---

## 五、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 数据库表名变更 | 需要迁移数据 | 保留原表名，使用 `db_table='modules'` 参数 |
| 现有数据丢失 | 已安装的模块信息可能丢失 | 先备份数据库 |
| 引用遗漏 | 部分功能异常 | 全面搜索 `NodeModule` 关键词确认无遗漏 |

---

## 六、推荐实施策略

### 方案 A：保持表名（推荐）

不修改数据库表名，仅修改类名：

```python
class Module(models.Model):
    class Meta:
        db_table = 'node_modules'  # 保持原表名
```

**优点**：无需数据迁移，风险最低
**缺点**：类名与表名不完全对应

### 方案 B：修改表名

修改表名为 `modules`：

```python
class Module(models.Model):
    class Meta:
        db_table = 'modules'
```

然后创建迁移：
```bash
./venv/bin/python manage.py makemigrations core --name rename_nodemodule_to_module
```

**优点**：命名规范统一
**缺点**：需要数据迁移，较为复杂

---

## 七、相关文档

- [02_模块技术规范](../技术规范/02_模块技术规范.md)
- [30_模块管理功能升级方案](./30_模块管理功能升级方案.md)

---

---

## 实施状态

| 状态 | 日期 | 说明 |
|------|------|------|
| ✅ 已完成 | 2026-03-29 | 所有代码已更新，迁移已执行 |

---

*文档创建：2026-03-29*  
*最后更新：2026-03-29*