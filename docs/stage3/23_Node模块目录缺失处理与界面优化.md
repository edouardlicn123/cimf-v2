# Node 模块目录缺失处理与界面优化

## 背景

在 Node 模块动态加载系统中，存在以下两个问题需要解决：

1. **模块目录缺失处理**：当模块目录被意外删除，但 `INSTALLED_APPS` 中仍有该模块时，Django 会启动失败
2. **模块管理页面优化**：页面未显示模块目录是否存在的信息

## 问题分析

### 问题1：模块目录缺失

当前 `cimf_django/settings.py` 中的 INSTALLED_APPS 包含硬编码的模块：

```python
INSTALLED_APPS = [
    ...
    'nodes.customer',
    'nodes.customer_cn',
]
```

如果用户删除了 `nodes/customer/` 目录但未从 INSTALLED_APPS 中移除，Django 启动时会抛出 `ModuleNotFoundError: No module named 'nodes.customer'`，导致系统无法启动。

### 问题2：模块管理页面

当前模板 `core/node/templates/modules/index.html` 显示的状态：
- 未安装
- 已安装
- 已启用

但未考虑模块目录不存在的情况。

## 解决方案

### 解决方案1：自动修复 INSTALLED_APPS

在 Django 启动前（`django.setup()` 之前）执行以下逻辑：

1. 扫描 `nodes/` 目录，获取实际存在的模块目录列表
2. 读取 `settings.INSTALLED_APPS`，找出 `nodes.xxx` 格式的条目
3. 对比两者，移除目录不存在的模块条目
4. 输出警告信息

### 解决方案2：增加 path_exists 属性

在 NodeModule 模型中添加 `path_exists` 属性，检查模块目录是否真实存在。

### 解决方案3：界面显示优化

在模块管理页面中：
- 增加"不存在"状态显示
- 目录缺失时禁用操作按钮
- 增加描述、作者等信息展示

## 实施步骤

### 步骤1：创建自动修复函数

文件：`run.py`

```python
def validate_and_fix_installed_apps():
    """验证并自动修复 INSTALLED_APPS 中的缺失模块"""
    # 在 django.setup() 之前调用
```

### 步骤2：在 main() 中调用

文件：`run.py`

在 `main()` 函数开头调用 `validate_and_fix_installed_apps()`

### 步骤3：在 init_db.py 中添加相同逻辑

文件：`init_db.py`

### 步骤4：添加 path_exists 属性

文件：`core/node/models.py`

```python
@property
def path_exists(self):
    """检查模块目录是否存在"""
    module_path = os.path.join(NodeModuleService.MODULES_DIR, self.path)
    return os.path.isdir(module_path)
```

### 步骤5：更新模板

文件：`core/node/templates/modules/index.html`

- 增加"不存在"状态判断
- 目录缺失时禁用操作按钮

## 影响范围

| 文件 | 变更类型 |
|------|----------|
| run.py | 修改 |
| init_db.py | 修改 |
| core/node/models.py | 修改 |
| core/node/templates/modules/index.html | 修改 |

## 测试场景

1. 删除 `nodes/customer/` 目录后启动系统 - 应自动跳过该模块并显示警告
2. 恢复目录后重新启动 - 应正常加载
3. 模块管理页面应显示目录不存在状态