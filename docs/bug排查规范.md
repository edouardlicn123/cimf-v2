# Bug 排查规范

> 系统性 Bug 排查方法论、检查清单和修复规范。

---

## 一、核心原则

### 1.1 防御性编程

```python
# ❌ 危险：假设对象不为 None
customer = get_customer()
customer.delete()  # customer 是 None 怎么办？

# ✅ 安全：防御性检查
customer = get_customer()
if not customer:
    return error
customer.delete()
```

### 1.2 信任但验证

- 即使前端已做验证，后端仍需验证
- 即使表单已验证，视图仍需检查
- 即使 API 已认证，每个端点仍需验证

---

## 二、检查阶段

### 阶段一：服务层检查（高优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| `.first()` 返回值 | `if result is None:` | 高 |
| `.get()` 异常 | `try: ... except:` | 高 |
| 外键访问 | `obj.foreign_key.name` | 高 |
| 整数字段搜索 | `filter(id__icontains=s)` | 高 |

```bash
# 检查所有 .first() 调用
grep -rn "\.first()" nodes/services/ core/services/
```

**常见问题：**
```python
# ❌ 整数字段不支持 __icontains
queryset.filter(id__icontains=search)

# ✅ 先转换为整数
try:
    node_id = int(search)
    queryset.filter(id=node_id)
except ValueError:
    pass

# ❌ 链式 filter 是 AND，不是 OR
queryset.filter(name__icontains=s)
queryset.filter(code__icontains=s)  # 实际是 AND

# ✅ 使用 Q 对象
queryset.filter(Q(name__icontains=s) | Q(code__icontains=s))
```

---

### 阶段二：表单验证检查（中优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| clean_* 方法 | 必填验证 | 高 |
| clean() 方法 | 交叉验证 | 高 |
| user_id 排除 | `exclude(id=user_id)` | 中 |
| 密码验证 | 非空 + 长度（≥10） | 高 |

```bash
# 检查所有 clean 方法
grep -rn "def clean" core/forms/ nodes/forms.py

# 检查 exclude 调用
grep -rn "exclude.*id" core/forms/
```

**常见问题：**
```python
# ❌ 都为空时跳过验证
def clean(self):
    if new_password and confirm_password:
        if new_password != confirm_password:
            raise ValidationError(...)

# ✅ 新密码必填
def clean(self):
    if not new_password:
        raise ValidationError('密码不能为空')
    if new_password != confirm_password:
        raise ValidationError(...)

# ❌ user_id 为 None 时 exclude 失败
def clean_username(self):
    User.objects.filter(username=username).exclude(id=self.user_id)

# ✅ 先检查 user_id
def clean_username(self):
    if self.user_id:
        User.objects.filter(username=username).exclude(id=self.user_id).exists()
    else:
        User.objects.filter(username=username).exists()
```

---

### 阶段三：API 安全检查（高优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| @login_required | 装饰器存在 | 高 |
| @require_GET/POST | 装饰器存在 | 中 |
| 参数验证 | `if not param:` | 中 |
| 权限检查 | `can_access_admin()` | 中 |

```bash
# 列出所有 API 函数
grep -rn "^def api_\|^def .*_api" core/views.py nodes/views.py

# 检查登录验证
grep -B1 "def api_" core/views.py | grep "@login_required"
```

**常见问题：**
```python
# ❌ 缺少登录验证
def api_regions_provinces(request):
    return JsonResponse(...)

# ✅ 添加 @login_required
@login_required
def api_regions_provinces(request):
    return JsonResponse(...)

# ❌ 重复装饰器
@login_required
@require_POST
@login_required  # 重复
def api_regions_import(request):

# ✅ 移除重复
@login_required
@require_POST
def api_regions_import(request):
```

---

### 阶段四：模板一致性检查（中优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| 外键显示 | `obj.foreign_key.name` | 高 |
| date() 过滤器 | `{{ x\|date() if x else '-' }}` | 高 |
| csrf_token | `{{ csrf_token }}` | 高 |

```bash
# 检查外键显示
grep -rn "\.name|default" templates/nodes/

# 检查 csrf_token 调用
grep -rn "csrf_token()" templates/

# 检查 date + default 错误用法
grep -rn "date.*|default" templates/
```

**常见问题：**
```html
<!-- ❌ 外键直接显示 -->
{{ customer.country }}

<!-- ✅ 显示名称 -->
{{ customer.country.name if customer.country else '-' }}

<!-- ❌ date() 不能用 |default -->
{{ user.last_login_at|date('Y-m-d')|default('-') }}

<!-- ✅ 使用三元表达式 -->
{{ user.last_login_at|date('Y-m-d') if user.last_login_at else '-' }}

<!-- ❌ SafeString 不可调用 -->
{{ csrf_token() }}

<!-- ✅ 直接使用 -->
{{ csrf_token }}
```

---

## 三、修复优先级

| 优先级 | 类型 | 说明 |
|--------|------|------|
| 🔴 P0 | 安全漏洞 | 认证绕过、权限提升、数据泄露 |
| 🟠 P1 | 功能崩溃 | 导致 500 错误、数据丢失 |
| 🟡 P2 | 功能异常 | 功能可用但结果错误 |
| 🟢 P3 | 体验问题 | UI/UX 优化 |

---

## 四、验证清单

每次修复后必须验证：

```bash
./venv/bin/python manage.py check
./venv/bin/python manage.py test
```

---

## 五、预防措施

### 5.1 Bug 易错点同步到开发规范

**重要原则：发现的 Bug 如果有可能在日后开发中复现，必须写入开发规范。**

每次完成 Bug 修复后，问自己：
- 这个 Bug 是否可能在新功能中再次出现？
- 其他开发者是否会犯同样的错误？

如果答案是"可能"，则在 `docs/开发规范.md` 的"常见 Bug 易错点"章节中添加记录。

### 5.2 Code Review 检查清单

```
□ 是否有新的 API？是否添加 @login_required？
□ 是否有对象查询？是否处理 None 情况？
□ 是否有表单修改？是否验证必填字段？
□ 是否有配置修改？是否同步模型/表单/模板？
□ 是否有权限修改？是否测试边界情况？
```

---

## 六、潜在 Bug 风险区域

| 区域 | 风险 | 原因 |
|------|------|------|
| **nodes/services/*.py** | 🔴 高 | Optional 返回未检查 |
| **core/forms/*.py** | 🔴 高 | clean_* 方法易出错 |
| **API 端点** | 🔴 高 | 可能缺少认证 |
| **templates/** | 🟡 中 | 外键直接显示 |
| **views.py** | 🟡 中 | 大文件容易遗漏 |
| **static/js/** | 🟢 低 | 与后端不同步 |

---

## 七、Bug 统计（30个已修复）

| 类型 | 数量 | 主要问题 |
|------|------|----------|
| 安全类 | 8 | 用户名篡改、密码验证、API认证缺失 |
| 功能类 | 13 | None 检查缺失、查询逻辑错误 |
| 模板类 | 3 | 外键显示错误、ID不匹配 |
| 配置类 | 3 | choices 不一致、migration 缺失 |
| 表单类 | 2 | clean() 验证不完整 |
| 权限类 | 1 | 自删漏洞 |

---

*文档创建：2026-03-19*
*版本：1.2*
