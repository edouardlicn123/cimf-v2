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

### 阶段一：Django 系统检查（基础必做）

| 检查项 | 命令 | 说明 |
|--------|------|------|
| Django 系统检查 | `./venv/bin/python manage.py check` | 检查配置错误 |
| Migration 状态 | `./venv/bin/python manage.py showmigrations` | 检查迁移完整性 |
| Migration 顺序 | `./venv/bin/python manage.py showmigrations --plan` | 检查迁移执行顺序 |

**执行流程：**
```bash
# 1. 系统检查
./venv/bin/python manage.py check

# 2. Migration 状态
./venv/bin/python manage.py showmigrations

# 3. 检查是否有未应用的迁移
./venv/bin/python manage.py showmigrations --plan | grep "^\[ \]"
```

---

### 阶段二：服务层检查（高优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| `.first()` 返回值 | `if result is None:` | 高 |
| `.get()` 异常 | `try: ... except:` | 高 |
| 外键访问 | `obj.foreign_key.name` | 高 |
| 整数字段搜索 | `filter(id__icontains=s)` | 高 |

**检查命令：**
```bash
# 检查所有 .first() 调用（高危）
grep -rn "\.first()" core/ modules/

# 检查 .first().属性 链式调用（直接访问属性）
grep -rn "\.first()\." core/ modules/

# 检查嵌套 filter
grep -rn "filter(.*filter(" core/ modules/

# 检查整数字段的 __icontains
grep -rn "__icontains=" core/ modules/
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

# ❌ .first() 返回 None 时访问属性
node = Node.objects.filter(...).first()
print(node.id)  # AttributeError!

# ✅ 使用可选链或显式检查
node = Node.objects.filter(...).first()
if node:
    print(node.id)
```

---

### 阶段三：API 安全检查（高优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| @login_required | 装饰器存在 | 高 |
| @require_GET/POST | 装饰器存在 | 中 |
| 重复装饰器 | `@login_required @login_required` | 高 |
| 参数验证 | `if not param:` | 中 |
| 权限检查 | `can_access_admin()` | 中 |

**检查命令：**
```bash
# 列出所有 API 函数
grep -rn "^def api_" core/ modules/

# 检查 API 是否有 @login_required
grep -B2 "def api_" core/views.py | grep "@login_required"

# 检查重复装饰器
grep -rn "@login_required.*@login_required" core/ modules/

# 检查 @require 装饰器
grep -rn "@require_" core/ modules/
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
@login_required  # 重复！
def api_regions_import(request):

# ✅ 移除重复
@login_required
@require_POST
def api_regions_import(request):

# ❌ 参数未验证
def api_get_user(request, user_id):
    user = User.objects.get(id=user_id)  # user_id 可能是无效的

# ✅ 参数验证
def api_get_user(request, user_id):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': '无效的用户ID'}, status=400)
    user = User.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({'error': '用户不存在'}, status=404)
    return JsonResponse({'user': user.username})
```

---

### 阶段四：表单验证检查（中优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| clean_* 方法 | 必填验证 | 高 |
| clean() 方法 | 交叉验证 | 高 |
| user_id 排除 | `exclude(id=user_id)` | 中 |
| 密码验证 | 非空 + 长度（≥10） | 高 |

**检查命令：**
```bash
# 检查所有 clean 方法
grep -rn "def clean" core/forms/ modules/*/forms.py

# 检查 exclude 调用
grep -rn "exclude" core/forms/ modules/*/forms.py

# 检查必填字段
grep -rn "required=True" core/forms/ modules/*/forms.py
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
    query = User.objects.filter(username=username)
    if self.user_id:
        query = query.exclude(id=self.user_id)
    if query.exists():
        raise ValidationError('用户名已存在')
```

---

### 阶段五：模板一致性检查（中优先级）

| 检查项 | 代码模式 | 风险 |
|--------|----------|------|
| 外键显示 | `obj.foreign_key.name` | 高 |
| Jinja2 语法 | `{{ x\|date() }}` | 高 |
| csrf_token | `{{ csrf_token }}` | 高 |

**检查命令：**
```bash
# 检查 POST 表单
grep -rn 'method="post"' templates/

# 检查 csrf_token
grep -rn "csrf_token" templates/

# 检查 Jinja2 date 语法（Jinja2 不支持 date:"format"）
grep -rn 'date:"' templates/

# 检查外键直接显示
grep -rn "\.country\|\.city\|\.region" templates/
```

**常见问题：**
```html
<!-- ❌ 外键直接显示（可能为 None） -->
{{ customer.country }}

<!-- ✅ 显示名称 -->
{{ customer.country.name if customer.country else '-' }}

<!-- ❌ Jinja2 不支持 Django 模板语法 -->
{{ user.last_login_at|date("Y-m-d") }}

<!-- ✅ 使用 strftime -->
{{ user.last_login_at.strftime('%Y-%m-%d') if user.last_login_at else '-' }}

<!-- ❌ SafeString 不可调用 -->
{{ csrf_token() }}

<!-- ✅ 直接使用 -->
{{ csrf_token }}

<!-- ❌ 未处理 None 的 date -->
{{ log.created_at|date("Y-m-d") }}

<!-- ✅ 使用三元表达式 -->
{{ log.created_at.strftime('%Y-%m-%d') if log.created_at else '-' }}
```

---

### 阶段六：配置完整性检查（中优先级）

新增模块时需检查配置项的完整性。

| 检查项 | 说明 |
|--------|------|
| settings_service.py | DEFAULT_SETTINGS 是否包含所有新配置项 |
| 表单字段 | form.py 是否包含对应字段 |
| 服务层读取 | service.py 是否读取新配置 |
| 模板显示 | HTML 是否显示配置值 |
| 默认值 | 是否设置合理的默认值 |

**检查命令：**
```bash
# 检查配置项定义
grep -n "smtp_" core/services/settings_service.py

# 检查表单字段
grep -n "smtp" core/smtp/forms.py

# 检查服务层读取
grep -n "smtp" core/smtp/services/
```

---

## 三、检查命令速查表

### 3.1 系统级检查

```bash
# Django 系统检查
./venv/bin/python manage.py check

# Migration 状态
./venv/bin/python manage.py showmigrations

# Migration 执行计划
./venv/bin/python manage.py showmigrations --plan

# 测试运行
./venv/bin/python manage.py test
```

### 3.2 服务层检查

```bash
# .first() 调用
grep -rn "\.first()" core/ modules/

# .first().属性 链式调用（高危）
grep -rn "\.first()\." core/ modules/

# 嵌套 filter
grep -rn "filter(.*filter(" core/ modules/

# 整数字段的 __icontains
grep -rn "__icontains=" core/ modules/

# .get() 异常处理
grep -rn "\.objects\.get(" core/ modules/
```

### 3.3 API 安全检查

```bash
# 所有 API 函数
grep -rn "^def api_" core/ modules/

# @login_required 装饰器
grep -rn "@login_required" core/ modules/

# 重复装饰器
grep -rn "@login_required.*@login_required" core/ modules/

# @require 装饰器
grep -rn "@require_" core/ modules/
```

### 3.4 表单检查

```bash
# clean 方法
grep -rn "def clean" core/forms/ modules/*/forms.py

# exclude 调用
grep -rn "exclude" core/forms/ modules/*/forms.py

# 必填字段
grep -rn "required=True" core/forms/ modules/*/forms.py
```

### 3.5 模板检查

```bash
# POST 表单
grep -rn 'method="post"' templates/

# csrf_token
grep -rn "csrf_token" templates/

# Jinja2 date 语法错误
grep -rn 'date:"' templates/

# 外键显示
grep -rn "\.country\|\.city\|\.region\|\.type\|\.level" templates/
```

---

## 四、修复优先级

| 优先级 | 类型 | 说明 |
|--------|------|------|
| 🔴 P0 | 安全漏洞 | 认证绕过、权限提升、数据泄露 |
| 🟠 P1 | 功能崩溃 | 导致 500 错误、数据丢失 |
| 🟡 P2 | 功能异常 | 功能可用但结果错误 |
| 🟢 P3 | 体验问题 | UI/UX 优化 |

---

## 五、验证清单

每次修复后必须验证：

```bash
# Django 系统检查
./venv/bin/python manage.py check

# 功能测试（如果有测试用例）
./venv/bin/python manage.py test

# 手动功能验证
# 1. 访问相关页面
# 2. 提交表单
# 3. 检查日志
```

---

## 六、预防措施

### 6.1 Bug 易错点同步到开发规范

**重要原则：发现的 Bug 如果有可能在日后开发中复现，必须写入开发规范。**

每次完成 Bug 修复后，问自己：
- 这个 Bug 是否可能在新功能中再次出现？
- 其他开发者是否会犯同样的错误？

如果答案是"可能"，则在 `docs/开发规范.md` 的"常见 Bug 易错点"章节中添加记录。

### 6.2 Code Review 检查清单

```
□ 是否有新的 API？是否添加 @login_required？
□ 是否有对象查询？是否处理 None 情况？
□ 是否有表单修改？是否验证必填字段？
□ 是否有配置修改？是否同步模型/表单/模板/视图？
□ 是否有权限修改？是否测试边界情况？
□ 是否有新增模板？是否包含 csrf_token？
□ 是否修改了 Jinja2 模板？是否使用正确的语法？
□ 是否有新增设置项？是否同步到所有相关文件？
□ 新功能是否测试了未登录访问？（应重定向或返回401）
□ 运行 `./venv/bin/python manage.py check` 是否有 CIMF_W001 警告？
□ POST 表单是否使用 `{% include "includes/csrf.html" %}`？
```

---

## 七、潜在 Bug 风险区域

| 区域 | 风险 | 原因 |
|------|------|------|
| **core/services/*.py** | 🔴 高 | Optional 返回未检查 |
| **modules/*/services.py** | 🔴 高 | 业务逻辑复杂 |
| **core/forms/*.py** | 🔴 高 | clean_* 方法易出错 |
| **API 端点** | 🔴 高 | 可能缺少认证 |
| **templates/** | 🟡 中 | 外键直接显示、Jinja2 语法错误 |
| **views.py** | 🟡 中 | 大文件容易遗漏 |
| **static/js/** | 🟢 低 | 与后端不同步 |

---

## 八、新模块检查模板

开发新模块时，按以下清单逐项检查。

### 8.1 模型层检查

```python
# models.py
class NewModule(models.Model):
    """新模块模型"""
    
    # ✅ 必填检查：所有必要字段是否有 blank=False/null=False
    name = models.CharField(max_length=100)  # 必填
    
    # ✅ 外键检查：外键字段是否正确
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    
    # ✅ choices 检查：是否与表单/视图一致
    status = models.CharField(max_length=20, choices=[
        ('draft', '草稿'),
        ('published', '已发布'),
    ])
    
    # ✅ 时间戳：是否使用 auto_now_add/auto_now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'new_module'  # ✅ 表名是否唯一
```

**检查清单：**
- [ ] 所有必填字段已定义
- [ ] 外键关系正确（on_delete）
- [ ] choices 与表单/视图一致
- [ ] 有 __str__ 方法
- [ ] 有 Meta 类定义表名

### 8.2 服务层检查

```python
# services.py
class NewModuleService:
    """新模块服务"""
    
    @staticmethod
    def get_by_id(module_id: int) -> Optional['NewModule']:
        """✅ .first() 返回值必须检查"""
        return NewModule.objects.filter(id=module_id).first()
    
    @staticmethod
    def create(data: dict) -> NewModule:
        """✅ 创建时必填字段检查"""
        if not data.get('name'):
            raise ValueError('名称不能为空')
        return NewModule.objects.create(**data)
    
    @staticmethod
    def get_list(filters: dict) -> List[NewModule]:
        """✅ 使用 select_related 避免 N+1"""
        queryset = NewModule.objects.select_related('category')
        
        # ✅ 整数字段不直接用 __icontains
        if filters.get('category_id'):
            queryset = queryset.filter(category_id=filters['category_id'])
        
        # ✅ 使用 Q 对象进行 OR 查询
        if filters.get('search'):
            from django.db.models import Q
            search = f"%{filters['search']}%"
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
```

**检查清单：**
- [ ] `.first()` 返回值被检查
- [ ] `.get()` 有异常处理
- [ ] 外键访问前检查 None
- [ ] 整数字段不用 `__icontains`
- [ ] 列表查询使用 `select_related`
- [ ] 复杂查询使用 Q 对象

### 8.3 表单层检查

```python
# forms.py
class NewModuleForm(forms.ModelForm):
    """新模块表单"""
    
    class Meta:
        model = NewModule
        fields = ['name', 'category', 'status', 'description']
        # ✅ 字段与模型一致
    
    # ✅ 必填字段验证
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('名称不能为空')
        if len(name) < 2:
            raise forms.ValidationError('名称至少2个字符')
        return name.strip()
    
    # ✅ 交叉验证
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        category = cleaned_data.get('category')
        
        # ✅ 业务规则验证
        if status == 'published' and not category:
            raise forms.ValidationError('发布时必须选择分类')
        
        return cleaned_data
```

**检查清单：**
- [ ] clean_* 方法验证必填字段
- [ ] clean() 方法进行交叉验证
- [ ] 错误信息明确
- [ ] 字段与模型一致

### 8.4 视图层检查

```python
# views.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@login_required  # ✅ 必须有登录验证
@require_http_methods(["GET", "POST"])  # ✅ 限制 HTTP 方法
def new_module_list(request):
    """列表视图"""
    
    # ✅ 参数验证
    search = request.GET.get('search', '')
    category_id = request.GET.get('category')
    
    if category_id:
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            category_id = None
    
    # ✅ 权限检查（如果需要）
    if not request.user.is_admin:
        return JsonResponse({'error': '需要管理员权限'}, status=403)
    
    modules = NewModuleService.get_list({
        'search': search,
        'category_id': category_id,
    })
    
    return render(request, 'new_module/list.html', {
        'modules': modules,
    })

@login_required
@require_http_methods(["POST"])
def new_module_create(request):
    """创建视图"""
    form = NewModuleForm(request.POST)
    
    if not form.is_valid():  # ✅ 必须检查表单有效性
        return JsonResponse({'errors': form.errors}, status=400)
    
    try:
        module = NewModuleService.create(form.cleaned_data)
        return JsonResponse({'success': True, 'id': module.id})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
```

**检查清单：**
- [ ] 有 `@login_required` 装饰器
- [ ] 有 `@require_*` 限制 HTTP 方法
- [ ] 参数验证（GET/POST.get()）
- [ ] 权限检查（如果需要）
- [ ] 表单验证 `form.is_valid()`
- [ ] 异常处理

### 8.5 URL 配置检查

```python
# urls.py
urlpatterns = [
    # ✅ 命名规范：app:view_name
    path('new-module/', views.new_module_list, name='new_module_list'),
    path('new-module/create/', views.new_module_create, name='new_module_create'),
    # ✅ 使用命名空间
]
```

**检查清单：**
- [ ] URL 命名规范 `app:name`
- [ ] HTTP 方法与视图一致
- [ ] 参数格式正确

### 8.6 模板层检查

```html
<!-- templates/new_module/list.html -->

<!-- ✅ 表单必须包含 csrf_token -->
<form method="post">
    {{ csrf_token }}
    
    <!-- ✅ 外键显示检查 None -->
    <td>{{ module.category.name if module.category else '-' }}</td>
    
    <!-- ✅ 时间格式化使用 strftime -->
    <td>{{ module.created_at.strftime('%Y-%m-%d') if module.created_at else '-' }}</td>
    
    <!-- ✅ 布尔值显示 -->
    <td>{{ '是' if module.is_active else '否' }}</td>
    
    <!-- ✅ 默认值处理 -->
    <td>{{ module.description|default('无') }}</td>
</form>

<!-- ✅ 链接检查 -->
<a href="{{ url('app:new_module_detail', module.id) }}">查看</a>
```

**检查清单：**
- [ ] POST 表单包含 `{{ csrf_token }}`
- [ ] 外键显示检查 None
- [ ] 时间使用 `strftime()`
- [ ] 布尔值正确显示
- [ ] 默认值处理
- [ ] 链接格式正确

### 8.7 配置层检查

```python
# core/services/settings_service.py
DEFAULT_SETTINGS = {
    # ... 其他设置 ...
    
    # ✅ 新模块配置项
    'new_module_enabled': 'false',
    'new_module_page_size': '20',
    'new_module_allow_export': 'false',
}

# core/services/new_module_service.py
class NewModuleService:
    @classmethod
    def get_config(cls) -> dict:
        settings = SettingsService.get_all_settings()
        return {
            'enabled': settings.get('new_module_enabled', 'false') == 'true',
            'page_size': int(settings.get('new_module_page_size', '20')),
            'allow_export': settings.get('new_module_allow_export', 'false') == 'true',
        }
```

**检查清单：**
- [ ] DEFAULT_SETTINGS 包含所有配置项
- [ ] 表单包含对应字段
- [ ] 服务层读取配置
- [ ] 模板显示配置值
- [ ] 有合理的默认值

### 8.8 Migration 检查

```bash
# 创建迁移
./venv/bin/python manage.py makemigrations new_module

# 检查生成的迁移文件
# ✅ 确保：
# 1. 依赖正确（core.0001_initial）
# 2. 字段类型正确
# 3. 索引和外键正确
```

**检查清单：**
- [ ] 迁移依赖正确
- [ ] 字段类型与模型一致
- [ ] 有必要的索引
- [ ] 外键关系正确

### 8.9 新模块完整检查命令

```bash
# 1. 系统检查
./venv/bin/python manage.py check

# 2. Migration 检查
./venv/bin/python manage.py makemigrations --check
./venv/bin/python manage.py showmigrations | grep new_module

# 3. 服务层检查
grep -n "\.first()" core/services/new_module_service.py
grep -n "\.get(" core/services/new_module_service.py

# 4. 视图检查
grep -n "@login_required" core/views.py | grep new_module
grep -n "@require_" core/views.py | grep new_module

# 5. 表单检查
grep -n "def clean" core/forms/new_module_forms.py

# 6. 模板检查
grep -n "csrf_token" templates/core/new_module/
grep -n 'date:"' templates/core/new_module/

# 7. 配置检查
grep -n "new_module_" core/services/settings_service.py
```

---

## 九、Bug 统计（35个已修复）

| 类型 | 数量 | 主要问题 |
|------|------|----------|
| 安全类 | 9 | 用户名篡改、密码验证、API认证缺失、重复装饰器 |
| 功能类 | 14 | None 检查缺失、查询逻辑错误、重定向循环 |
| 模板类 | 4 | 外键显示错误、ID不匹配、Jinja2语法 |
| 配置类 | 3 | choices 不一致、migration 缺失、迁移顺序 |
| 表单类 | 3 | clean() 验证不完整、密码验证、依赖验证 |
| 权限类 | 1 | 自删漏洞 |
| 性能类 | 1 | N+1 查询优化 |

---

*文档创建：2026-03-19*
*最后更新：2026-04-05*
*版本：1.3*
