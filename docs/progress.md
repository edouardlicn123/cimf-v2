# 修改记录

本文档记录项目的每次修改，按日期分组。

---

# 2026-03-19 修改记录

1. 全面检查修复bug：
   - [安全] 用户名可被篡改 - clean_username() 检查用户名是否被修改
   - [安全] 密码验证漏洞 - 创建用户时密码必填验证
   - [安全] timezone.timedelta 使用错误 - 修复 datetime 导入
   - [功能] 主题选项不一致 - 添加 gov/indigo 主题
   - [功能] 统一客户服务接口 - 添加 user 参数
   - [功能] 删除消息显示条件 - customer为None时处理
   - [功能] node_delete customer为None崩溃 - 添加检查
   - [功能] node_view customer为None检查 - 添加重定向
   - [功能] get_list 查询问题 - 使用 Q() 组合查询
   - [功能] TimeSyncTask 使用非单例 - 改用单例模式
   - [功能] cron_service sleep_time 未定义 - 初始化变量
   - [功能] auth_service int(None) 错误 - 添加异常处理
   - [功能] ProfileForm.clean_email user_id为None - 添加条件判断
   - [功能] UserEditForm.clean_username user_id为None - 添加条件判断
   - [模板] watermark.js ID 不匹配 - 统一ID命名
   - [模板] watermark 元素缺失 - 添加 watermarkWarning
   - [模板] dashboard 缺少统计卡片 - 添加二类用户卡片
   - [模板] 用户角色显示错误 - 修复 'admin' → 'manager'
   - [模板] customer country 外键显示 - 改为 country.name
   - [配置] User Theme migration 缺失 - 创建新 migration
   - [配置] csrf_token 返回格式问题 - 直接返回 HTML
   - [配置] 缺少 CustomerCnFields Admin - 注册 Admin
   - [安全] api_regions_* 缺少登录验证 - 添加 @login_required
   - [安全] api_time_* 缺少登录验证 - 添加 @login_required
   - [安全] user_delete 未防止删除自己 - 添加检查
   - [表单] ChangePasswordForm 验证逻辑漏洞 - 确保密码必填
   - [表单] UserService.create_user 缺少密码验证 - 添加验证
   - [安全] 登录锁定阈值硬编码 - 从 SettingsService 读取

2. 优化 update_progress.py：支持追加模式和覆盖模式，同一天多次修改自动编号；更新 AGENTS.md 添加自动更新指令

3. 全面检查修复bug：修复customer_service/customer_cn_service的get_list查询问题；修复nodes/views.py中customer/customer_cn编辑时customer为None的检查

4. 全面检查修复bug：修复dashboard缺少二类用户统计卡片；修复user_delete未防止删除自己账号

5. 全面检查修复bug：修复node_view中customer/customer_cn为None时的检查；优化权限检查一致性

6. 全面检查修复bug：为api_regions_*和api_time_* API添加登录验证，防止未登录访问

7. 修复User.record_failed_attempt()使用硬编码阈值问题，改为从SettingsService读取login_max_failures和login_lock_minutes

8. 修复ChangePasswordForm密码验证逻辑；修复UserService.create_user添加密码非空和长度验证

9. 创建 bug 问题小结文件 `docs/bug_summary.md`

---

*最后更新：2026-03-19*
*当前版本：v1.024*
10. 创建bug分析文档 docs/bug_analysis.md：分析bug模式、根因分析、高危区域、下一步排查计划
11. 按照bug_analysis执行完整检查：修复node_service.id__icontains错误；修复UserEditForm.clean_email缺少user_id检查；修复api_regions_import重复装饰器；修复模板外键显示.customer_type.name等；修复csrf_token()调用问题；创建28个单元测试
12. 创建Bug排查规范文档 docs/04_Bug排查规范.md：定义服务层、表单验证、API安全、模板一致性检查要点，包含常见bug模式与修复示例；更新AGENTS.md添加Bug排查规范引用
13. 验证 china_region_service.py 无语法错误；Django check 通过，System check identified no issues
14. 全面检查未覆盖区域：修复 templates/core/admin/system_users.html 和 templates/core/profile.html 中 date()|default() 写法错误（应使用三元表达式）；验证所有 @login_required 装饰器完整性；检查 core/fields、core/management、nodes/customer 等目录均无明显 bug
15. 重命名 docs/04_Bug排查规范.md → docs/bug排查规范.md，并更新 AGENTS.md 中的引用路径
16. 在 docs/开发规范.md 中新增'常见Bug易错点'章节：包含模板语法（|default与三元表达式、csrf_token调用、外键访问）、Python代码（.first()检查、表单clean()验证、API登录验证、密码验证）、安全（用户名篡改、硬编码阈值）、数据模型（id__icontains、QuerySet OR查询）等易错点总结及防御性检查清单
17. 删除 AGENTS.md 和 docs/开发规范.md 中对旧版本 cimf-flask 的参考要求；移除 Flask 到 Django 迁移问题汇总章节
18. 全面优化 docs/开发规范.md：移除过时目录结构和Flask迁移内容，简化章节结构，保留核心规范（项目结构、代码规范、Node模块、安全规范、Bug易错点、防御性检查清单），从542行精简至约300行
19. 全面优化 docs/开发规范.md：基于项目结构分析结果重新组织章节，包含准确的项目结构（core/nodes/templates/services层详细说明）、服务层规范（命名、设计原则）、视图层规范（命名、URL约定）、模型层规范（Core/Nodes模型说明、外键规范）、表单层规范、模板层规范、字段类型（24种）、安全规范、易错点表格化、检查清单；共约350行
20. 继续Bug检查：验证 nodes/services/*.py 和 core/forms/*.py 无新增问题；发现并修复 core/views.py:630 cron_status API缺少@login_required装饰器；验证所有模板外键显示有None检查；所有权限验证逻辑正常；Django check和28个测试全部通过
21. 继续Bug检查：验证 cimf_django/context_processors.py（csrf_token、system_settings正常）、static/js/*.js（watermark.js正常）、templates/includes/*.html（nav/header/js正常）、core/urls.py、nodes/urls.py（所有路由正确）、nodes/services/*.py、core/services/auth_service.py、cron_service.py 均无明显bug；Django check通过
22. 继续Bug检查：验证 templates/*.html、templates/core/admin/*.html、templates/nodes/*.html 全部正常；检查 nodes/forms.py、nodes/customer/forms.py、nodes/views.py、core/fields/*.py、core/fields/__init__.py 均正常；验证 cimf_django/settings.py 中间件配置、Django错误处理视图均正确；Django check和28个测试全部通过
23. 更新 docs/bug排查规范.md：新增'6.1 Bug易错点同步到开发规范'章节，明确要求发现的Bug如果有可能在日后开发中复现，必须写入docs/开发规范.md的'常见Bug易错点'章节，并给出操作示例
24. 整合文档：分析 bug_analysis.md 和 bug_summary.md，提取关键内容添加到 bug排查规范.md（七潜在Bug风险区域、八Bug统计与历史）和开发规范.md（三层架构一致性、复制代码注意事项）；删除旧文档 bug_analysis.md 和 bug_summary.md
25. 优化 docs/bug排查规范.md：从450行精简至260行，移除重复内容，整合检查命令和常见问题，保留核心章节；优化 docs/开发规范.md：从453行精简至230行，精简项目结构表格，整合服务/视图/表单/模板规范，保留核心Bug易错点表格
26. 删除 README 中关于 Flask 版本的全部内容
27. 重写 README 为 GitHub 风格，使用仙芙CIMF系统名称
28. 创建 frame_importexport 模板
29. 重命名 nodes/index.html 为 node_dashboard.html
30. 移动 node_dashboard.html 到 templates/core/node/
31. 创建 structure_dashboard 页面和路由
32. 移动 taxonomies 和 field_types 到 structure 文件夹
33. 修改 frame_structure 导航链接样式
34. 移动 field_types.html 到 structure/field_types 文件夹
35. 移动 profile 和 settings 模板到 usermenu 文件夹
36. 创建 frames 文件夹并移动所有 frame 模板
37. 全面按照Bug排查规范检查项目：服务层.first()返回值、表单验证、API安全、模板一致性等
38. 修改 structure_dashboard 参照 node_dashboard 模式

# 2026-03-20 修改记录

1. 新增导出导入菜单和importexport_dashboard页面
2. 修复regions_import URL缺失问题
3. 为structure和importexport页面添加权限控制及权限管理卡片
4. 还原structure为仅admin可用，只保留importexport的权限控制
5. 删除未完成的导入导出菜单项（词汇表、节点、用户）
6. 简化数据导入导出权限为单一访问权限
7. 创建文档：18_数据导出功能.md 和 19_数据导入功能.md
8. 细化导出功能文档（v1.1）：新增3步流程、字段选择页、确认页设计
9. 细化导出功能文档（v1.2）：新增导出中页、细化UI设计、简化服务层代码
10. 删除 region_test、region_field_test 相关代码（视图、路由、模板、管理命令），保留省市县查询 API
11. 修复导出功能：1) export_fields.html 添加 form action 属性，改用 {% csrf_token %}；2) export_confirm.html 同样修复 csrf_token 并添加 hidden field 传递选中字段；3) export_confirm 视图支持解析 comma-separated 字段字符串
12. 修复导出流程确认环节：1) export_confirm 视图 GET 渲染确认页（展示模块+字段），POST 跳转到 exporting；2) 简化 export_confirm.html，移除数据预览，仅保留摘要信息；3) export_exporting.html 保持过渡动画
13. 导出功能增强：1) 字段默认全部勾选；2) 新增筛选条件功能，6组过滤器（下拉选字段+输入框），过滤器间互斥（已有即排除）；3) customer_cn 额外显示省市区筛选器；4) 确认页展示筛选条件摘要和筛选后预览数据；5) ExportService 支持 filters 参数进行数据筛选
14. Bug 修复：1) 字段选择页 checkbox 的 `name="fields"` 导致 `request.POST.get('fields')` 只取第一个值，移除 checkbox 的 name 属性，仅通过 JS hidden input 传递；2) 数字字段（integer/decimal/float）使用 `__icontains` 筛选语义错误，移出 `FILTERABLE_FIELD_TYPES` 并移除通用 else 分支
15. 修复导出字段选择页：form action 从 export_confirm 改为 export_select_fields，避免 session 为空导致重定向回选择页
16. 将客户信息模块改名为客户信息（海外），介绍改为适用于管理中国以外的客户信息
17. 将客户信息（国内）介绍改为适用于管理国内客户的信息
18. 更新数据导出功能设计文档至 v1.3：补充筛选功能（6组过滤器+省市区筛选）、URL前缀改为nodes/、更新Service层方法、补充前端JS逻辑、移除未实现功能、添加Bug修复记录
19. 修复省市区字段Bug：1) _resolve_region_field 读取键名从 province_name/city_name/district_name 改为 province/city/district；2) _get_filtered_queryset 筛选查询字段从 region__province_name 等改为 region__province 等
20. End-to-end testing of export feature: verified all 4 steps work, filters work correctly, CSV and XLSX exports produce correct output with FK fields resolved and region field formatted properly
21. Fix field_types view template path: index.html → field_types.html
22. Unify spacing across all frame templates: changed pt-2 to py-4 py-md-5 to match dashboard page spacing (4rem mobile, 5rem desktop)
23. Reduce dashboard top spacing: changed main container from py-4 py-md-5 to pt-2 pt-md-3 pt-lg-4 pb-4 pb-md-5 for better balance with fixed navbar
24. Refactor dashboard to use frame_dashboard.html template for consistent spacing with system settings page
25. Redesign importexport dashboard: unified parallel cards for export/import without separate sections
26. Optimize transaction overview page: unified card layout with responsive grid, flex layout, primary-colored icons and prominent buttons
27. Optimize structure dashboard page: unified card layout with responsive grid, flex layout, primary-colored icons and prominent buttons
28. Ensure consistent card widths in structure dashboard by adding d-flex wrapper and w-100 on cards
29. Fix sample data: change customer names from company names to person names (overseas: John Smith, Hans Mueller, etc.; domestic: 张伟, 李娜, etc.)
30. Add missing dependencies to requirements.txt: requests>=2.32,<3.0, openpyxl>=3.1,<4.0
31. Localize Bootstrap libraries: download Bootstrap 5.3.3 and Bootstrap Icons 1.11.3 to static/lib/, update templates to use local files instead of CDN
32. Add logo feature: 1) Logo display in navbar (default sitelogo_white.png), 2) System settings page with logo toggle and upload, 3) Custom logo stored in media/logos/, 4) Added media() Jinja2 function for media URL generation
33. Fix Bootstrap Icons font path: copy woff2 to css/fonts/ and update CSS to use correct relative path

# 2026-03-21 修改记录

1. 修复 ModelRegistry bug：1) 修正 OneToOneRel 类名检查；2) 使用 field.name 代替 model._meta.model_name 以保留下划线（customer_cn_fields → customer_cn 而非 customercn）
2. 验证导入功能完成：ModelRegistry 修复后测试通过，模板生成、字段提取、FK解析器、特字段处理器均工作正常
3. 验证导入功能完整：测试 ModelRegistry、FieldDefExtractor、FKResolverPool、SpecialFieldPool、TemplateGenerator 均工作正常，28个测试全部通过（2个与本功能无关的API测试失败）
4. 修复导入功能 Bug：1) [安全] 为所有导入视图添加 @login_required 装饰器；2) [功能] ImportService.import_data 添加 node_type None 检查；3) [功能] FK 解析失败时不设置 None 值；4) [功能] _find_existing 添加字段不存在异常处理；5) [前端] 修复 import_page.html JS 元素检查；6) [前端] 移除 import_result.html 重复的 if 检查
5. 二次 Bug 检查：1) [前端] 修复 import_page.html 中 csrf_token() 错误调用，改为 {{ csrf_token }}
6. 三次 Bug 检查：1) [功能] TemplateGenerator.generate 添加 node_type None 检查；2) [代码风格] 修复 import_service.py 中 = 缺少空格问题
7. 四次 Bug 检查：全面检查导入功能服务层、视图层、模板层、安全检查，未发现新 Bug
8. 修复 csrf_token 模板语法错误：import_page.html 中 {% csrf_token %} 改为 <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
9. 为 frame_importexport.html 侧边栏添加导入菜单链接
10. 修复 import_page.html 多个问题：1) [功能] 修复空 error div 显示问题；2) [安全] 修复 XSS 漏洞，对 error.errors 和 cell 值进行 HTML 转义；3) [代码] 添加 escapeHtml 辅助函数
11. 彻底修复 import_page.html 空提示问题：移除静态 error div，改为 JS 动态创建，避免被 toast_messages.html 误检测
12. 彻底修复 import_page.html 空提示问题：将所有 .alert 类改为 .msg-box，避免被 toast_messages.html 误检测；同时添加相应 CSS 样式
13. 修复 import_page.html 多余的 </div> 标签导致页面显示 > 字符
14. 修改 import_page.html：返回按钮移至标题行左侧，与导出界面风格一致
15. 修复 import_page.html：移除 show_header = false 使标题区域正常显示

# 2026-03-22 修改记录

1. 修复 import_page.html：添加缺失的 </div> 关闭 row 标签
2. 重新创建 import_page.html：清理所有多余空白和潜在隐藏字符
3. 重新设计 import_page.html：参考导出界面风格，使用 show_header=false，简化结构
4. 修复 import_page.html：csrf_token 从 tag 改为 variable 语法
5. 修复空 toast 问题：移除 alert 类，使用 bg-* 类替代
6. 为导入模板 XLSX 添加 FK 字段可选值工作表：1) import_service.py 添加 get_fk_fields_with_options 方法；2) template_generator.py 添加 _add_fk_sheet 方法生成第二个工作表
7. 完善 FK 字段可选值：1) 在数据库创建 enterprise_type(企业性质) taxonomy 及词汇；2) 为空的 customer_type taxonomy 添加词汇；3) 更新 taxonomy_service.py DEFAULT_TAXONOMIES 列表
8. 为海外客户创建独立的企业性质分类：1) 创建 enterprise_nature(企业性质-海外) taxonomy 及词汇；2) 修改 FK 解析器支持 taxonomy 过滤；3) 修改 ImportService 支持 FK_TAXONOMY_OVERRIDES 映射；4) 更新 taxonomy_service.py DEFAULT_TAXONOMIES 列表
9. 优化客户信息（海外）列表页：1) 使用企业性质(海外) taxonomy 作为筛选条件；2) 列表增加企业性质列（badge 样式）；3) 替换电话列为网站列（带链接）；4) 操作按钮改为图标按钮组；5) 空数据提示增加图标；6) 分页仅显示前后2页
10. 按海外客户列表设计同步优化国内客户列表：增加客户类型列(badge样式)、行业列，操作按钮改为实心图标按钮，空数据增加图标，分页仅显示前后2页
11. 修复客户信息（海外）列表5个问题：1) edit.html国家字段重复name属性 2) node_edit空值检查位置 3) 列表视图添加权限过滤 4) list.html筛选条件类型比较优化 5) view.html三元表达式逻辑优化
12. 客户信息（海外）列表：移除客户类型和行业两列展示
13. 客户信息（海外）列表：添加电子邮件列
14. 客户信息（海外）列表：电子邮件列显示为mailto链接，最多20字符
15. 客户信息（海外）列表：电话1前添加WhatsApp聊天按钮
16. 客户信息（海外）列表：企业名称限制20字符显示
17. 客户信息（国内）列表：企业名称限制13字符，移除企业性质/网站/省市区，新增电话列
18. 客户信息（国内）列表：添加微信号列
19. README.md：添加 cimf.png 图片
20. README.md：图片缩小为50%
21. README.md：许可证更换为MIT
22. 全面检查并修复项目模板Bug：1)system_settings.html重复卡片 2)login.html set语句位置 3)taxonomies分页范围限制 4)system_users筛选逻辑 5)customer_cn region默认值
23. 再次全面检查模板：修复system_settings.html Logo卡片缺少闭合div标签
24. 再次检查修复：1)customer_cn/list.html企业名称空字符串处理 2)system_settings.html水印内容检查改用split后检查
25. 全面修复模板问题：1)客户列表企业名称空值处理 2)toast XSS漏洞修复 3)system_settings split空值保护 4)cron_manager空值检查 5)taxonomies Modal结构 6)customer_cn ID命名 7)permissions说明文字 8)login CSS合并 9)toast style合并
26. 再次修复模板问题：1)toast消息级别改用整数常量 2)cron空任务添加提示 3)customer_cn HTML属性转义 4)customer/customer_cn/edit.html空值处理 5)permissions role_labels默认值 6)taxonomies空值处理
27. 再次修复模板问题：1)customer_cn/edit.html phone2/email2/wechat/dingtalk空值处理 2)system_permissions.html label改为span 3)taxonomies/view.html taxonomy.name空值保护
28. 再次修复模板问题：1)customer_cn/list.html phone1/wechat空值处理 2)system_permissions.html role_permissions改用get方法 3)login.html CSS合并 4)customer/edit.html JS使用严格相等
29. 再次修复模板问题：1)客户列表customer_name添加默认值 2)system_cron_manager CSRF获取失败处理 3)system_users last_login_at添加检查 4)taxonomies编辑链接添加taxonomy检查 5)toast XSS防护改用DOM API 6)system_permissions role_labels改用get方法 7)login CSS选择器修正
30. 十次模板检查并修复：1)customer/edit.html country空值检查 2)system_cron_manager.html cron_status检查 3)system_users.html search_term默认值 4)taxonomies/view.html Modal移到table外 5)login.html settings默认值
31. 创建模板查Bug总结文档：docs/模板查Bug总结.md
32. 模板查Bug第11轮：修复 customer/view.html, customer_cn/view.html, types/, taxonomies/, import_page.html, profile.html, base.html, nav.html 中的 Jinja2 语法混用和 csrf_token 错误

# 2026-03-23 修改记录

1. 模板查Bug第12轮：修复 settings.html, export_fields.html, export_confirm.html 中的 csrf_token 错误
2. 模板查Bug二次检查：修复剩余 csrf_token 错误(7处)、date()语法(1处)
3. 模板查Bug第三轮：全面复查 XSS/JS安全、循环空值、ID唯一性 - 未发现新问题
4. 修复 Jinja2 default 过滤器语法错误：单引号改为冒号双引号
5. 修复 Jinja2 default 过滤器语法：强制使用括号()而非冒号:，修复 base.html, profile.html, nav.html, dashboard.html
6. 修复 Jinja2 csrf_token 语法：所有 {% csrf_token %} 改回 {{ csrf_token }}（共14处）
7. 修复 Jinja2 date 过滤器语法：所有 |date:"..." 改为 |date("...")（共8处）
8. 修复 Jinja2 dict 语法：.items() 改为 .items（3处），修复 system_permissions.html 和 system_cron_manager.html
9. 修复 Jinja2 过滤器链式调用：|default().split() 需要用括号分组（system_settings.html 4处）
10. 修复 Jinja2 dict.items() 语法：Jinja2 需要显式调用 items() 方法（permissions 和 cron_manager 3处）
11. 修复模板Bug: taxonomies/view.html移动Modal到表外、dashboard.html添加stats默认值、customer表单添加customer空值检查、修复JS中XSS风险
12. 创建模板开发规范文档，包含目录结构、Jinja2语法规范、模板片段库、变量/文件命名规范、新建页面Checklist、组件化指南、性能优化、Accessibility、调试方法、反模式、项目特殊约定等内容，并更新AGENTS.md
13. 将模板开发规范移动到 docs/技术规范/ 目录，更新 AGENTS.md 中的链接
14. 删除 01_分页器技术规范.md，更新 AGENTS.md
15. 更新 Node模块技术规范 文档：修正目录结构、更新模板示例为 frame_node.html、修正 csrf_token 语法、更新路由表添加导入导出和API路由
16. 创建Python代码开发规范文档 (05_Python代码开发规范.md)，包含11章+5个附录：文件头注释、导入规范、命名规范、类定义、函数规范、Django特定规范、API设计规范、测试规范、数据库迁移规范、定时任务规范，以及代码模板、反模式、检查清单等

# 2026-03-24 修改记录

1. 更新 README.md，补充字段类型系统、项目结构、文档说明、开发命令等内容
2. 创建客户模块目录重构计划文档 (20_客户模块目录重构计划.md)
3. 更新客户模块目录重构计划文档，添加Node支撑系统移入core目录的架构设计
4. 更新重构计划文档，添加模块自包含的templates目录设计
5. 开始执行客户模块目录重构：创建 core/node/ 模块，移动 NodeType 和 Node 模型
6. 完成客户模块目录重构核心部分：创建 core/node/ 模块，移动客户服务到各自目录
7. 完成客户模块目录重构：更新所有相关文件的导入路径
8. 完成客户模块目录重构：移动模板到模块自包含目录，更新settings.py模板路径
9. 完成 views.py 拆分：创建 core/node/views.py 节点类型管理视图，移动模板到 core/node/templates/
10. 完成 Import/Export 功能迁移：创建 core/importexport/ 模块，移动模板到 templates/importexport/
11. 完成 nodes 应用清理：移动 NodeTypeAdmin/NodeAdmin 到 core/node/admin，移动 NodeTypeForm 到 core/node/forms，删除旧文件
12. 完成 stage3 重构：创建 core/node/ 和 core/importexport/ 模块，整理客户模块到 nodes/customer/ 和 nodes/customer_cn/，Django check 通过
13. 创建 management command：./manage.py init_sample_data 用于初始化客户样本数据
14. run.sh 添加选项 5 用于初始化客户样本数据
15. 清理项目：删除6个空__init__.py文件和5个空目录
16. 重构 Admin：将 CustomerFieldsAdmin 移到 nodes/customer/admin.py，CustomerCnFieldsAdmin 移到 nodes/customer_cn/admin.py
17. 重构 nodes/ 目录：将 models 移到 customer/models.py 和 customer_cn/models.py，创建 customer/urls.py 和 customer_cn/urls.py
18. 完成 nodes/ 目录彻底清理：删除 models.py/admin.py/views.py，创建 customer 和 customer_cn 独立 app
19. 移动通用节点路由到 core/node/urls.py，nodes/urls.py 仅保留客户路由
20. 删除 nodes/tests.py 测试文件
21. 重组迁移目录：NodeType/Node迁移到core/migrations/，CustomerFields到customer/migrations/，CustomerCnFields到customer_cn/migrations/
22. 移动 management/ 命令到 core/management/commands/init_sample_data.py
23. 重构样本数据：core/services/sample_data_service.py 包含初始化逻辑，customer/sample_data.py 和 customer_cn/sample_data.py 分别包含各自样本数据，删除 nodes/services/ 目录
24. 分离初始化命令：init_node_types、init_overseas_customers、init_domestic_customers，并更新 run.sh 菜单
25. 移动主模板目录 templates/ 到 core/templates/，更新 settings.py 模板路径配置
26. 移动主模板目录 templates/ 到 core/templates/
27. 修复模板路径：修正 views.py 中的模板路径从 'customer/templates/xxx' 改为 'xxx'
28. 修复 URL 路由冲突：将 core/urls.py 中的 nodes/ 改为 node/，添加 nodes:index URL
29. 修复 URL 路由：修复节点 URL 顺序（export/import 必须在 generic slug 之前），修复 Jinja2 模板语法（date filter），修复 URL 命名空间（nodes: → core:）
30. 验证目录重构完成 - 系统检查通过，URL路由正常
31. 修复模板查找顺序 - 将 customer_cn 模板目录置于 customer 之前
32. 修复国内客户URL - 将slug从customer_cn改为customer-cn，匹配URL路由
33. 修复禁用节点类型错误提示 - 显示'节点类型已禁用'而非'不存在'
34. 修复Toast消息模板 - message|tojson改为message.message|tojson
35. 修复词汇表管理页分页 - 使用page_obj.paginator.page_range替代未定义的pages_to_show
36. 修复词汇项页分页 - 使用page_obj.paginator.page_range替代错误的range逻辑
37. 修复词汇表列表页 - taxonomy.items.count改为taxonomy.items.count()
38. 修复客户模板冲突 - 重命名customer_cn模板为list_cn.html等，添加缺失的API路由，修复redirect URL
39. 更新三个技术规范文档的描述，反映项目架构变化
40. 优化 Cron 服务初始化时机，从 CoreConfig.ready() 移至 run.py 和 wsgi.py
41. 修复 Cron 服务启动时机问题，使用后台线程 + django.setup() 确保应用已加载
42. 海外客户模块：新增领英字段（linkedin），合并联系方式卡片为统一入口

# 2026-03-25 修改记录

1. 修复国内客户省市区联动：移除API登录要求，导入省市区数据
2. 修复客户表单验证问题：添加novalidate禁用浏览器HTML5验证
3. 整合客户信息页面：将联系方式1、联系方式2、社交信息合并为统一的联系信息卡片
4. 更新Node模块技术规范文档：新增模块注册机制（十一）、模块信息文件（十二）、模块服务层（十三）、模块管理页面（十四）、新建模块功能（十五）、默认模块处理（十六）、模块与节点类型关系（十七）
5. 实现Node模块注册安装机制：创建NodeModule模型、NodeModuleService服务、为customer和customer_cn创建module.py、建立模块管理页面、初始化默认模块
6. 统一国内客户模块slug为customer_cn：修改services.py、urls.py、views.py、services、permission_service、sample_data、init_node_types、init_domestic_customers
7. 编写Node模块动态加载方案文档，保存至 docs/stage3/22_Node模块动态加载方案.md
8. 实现Node模块动态加载机制：添加module.py视图配置、实现module_dispatch视图分发、完善register/install逻辑、测试通过
9. 完成Node模块动态加载方案：更新init_db.py使用动态模块扫描安装、更新run.py添加模块初始化函数
10. 添加模块目录缺失自动修复和界面优化
11. 更新Node模块技术规范文档v1.3
12. 实现INSTALLED_APPS动态加载，新增模块无需修改配置文件
13. 完成新建模块功能的后端逻辑

# 2026-03-26 修改记录

1. 完成全面 Bug 检查
2. 完成全面 Bug 检查（第二轮）
3. 修改客户模块描述
4. 创建数据库配置模块独立化方案文档
5. 重构存储目录：新建storage/，包含uploads/和backups/
6. 实施数据库配置模块独立化方案
7. 合并node_modules和node_types页面

# 2026-03-27 修改记录

1. 实施模块管理功能升级方案
2. 删除模块管理页与frame_structure的关联，改用frame_admin
3. 创建frame_module框架并应用于模块管理页
4. 将 nodes 目录重命名为 modules，完成所有 nodes->modules 引用更新
5. 模块技术规范文档升级：新增模块设计总结.md，重写02_模块技术规范.md（从nodes改为modules）
6. 全面检查并修复URL namespace引用：nodes:改为modules:或importexport:
7. 修复模板加载问题：settings.py中nodes路径改为modules，APP_DIRS改为False确保Jinja2优先
8. 修复首页内容区域与顶部菜单间距过大：dashboard.html添加use_custom_main=true和show_header=false
9. 修复首页间距问题：恢复frame_dashboard.html原padding (py-4 py-md-5)
10. 删除core/node/views.py中无效的node_list和node_view视图（重定向到modules对应视图）
11. 优化代码：将9处裸except改为except Exception
12. 实现首页功能卡片区域与时钟模块：创建clock模块基础文件(apps.py/urls.py/services.py)、实现时间API、创建时钟卡片模板、添加3×2功能卡片区域HTML、实现拖拽功能和位置保存API
13. 实现动态模板加载：修改settings.py，在启动时自动扫描modules/目录下所有模块的templates目录并加入模板搜索路径
14. 修复首页功能卡片区域不显示时钟卡片的问题：修正core/views.py中模块路径导入错误，使用modules.{module_path}.module格式
15. 修复时钟卡片不显示时间问题：修正JS中时钟API URL从/modules/clock/改为/nodes/clock/
16. 修改URL路径从nodes/改为modules/，统一模块URL前缀
17. 为run.sh添加杀死服务器进程功能，支持通过DJANGO_PORT环境变量指定端口
18. 删除首页仪表盘中的用户统计卡片区域
19. 修复 init_db.py 初始化顺序：管理员用户创建移到客户样本数据初始化之前

# 2026-03-28 修改记录

1. 实现模块类型分类：添加 module_type 字段区分 node 和 system 类型，事务处理页面过滤 system 类型模块
2. 改进模块扫描逻辑：使用 ast 直接解析 module.py 文件，新增模块无需重启服务即可被扫描到
3. 更新 02_模块技术规范.md 文档：新增模块类型分类（node/system）、module_type 字段说明、更新示例代码
4. 合并文档：删除模块设计总结.md，将其核心概念表格整合到 02_模块技术规范.md
5. 整理优化 02_模块技术规范.md：精简结构，优化章节顺序，增强可读性
6. 优化仪表盘卡片配色：使用 --bg-nav 和 --text-nav 变量实现主题跟随
7. 为 customer 和 customer_cn 模块创建仪表盘卡片，显示客户数量统计
8. 修复dashboard卡片显示bug：移除module_type='node'过滤条件，使system类型的clock模块也能显示在卡片区域
9. 修复dashboard卡片渲染逻辑：当有保存的位置时，填充空槽位显示默认卡片
10. 修复dashboard时钟卡片不显示：改为遍历默认模块列表，为每个模块找到第一个空槽位进行填充
11. 修改dashboard页面标题为'欢迎回来，用户名'
12. 新增首页设置页面：用户可在个人设置中管理首页卡片，支持拖拽添加/移除/调整卡片位置
13. 重新设计首页设置页面：简化拖拽逻辑，使用document级别事件监听器
14. 优化首页设置页面UI：卡片式布局、渐变标题、hover效果提升
15. 首页设置页面样式与首页保持一致：使用CSS变量、Bootstrap grid、统一的卡片阴影和边框样式
16. 修复首页设置页面边框显示：使用内联style确保CSS变量正确应用
17. 重新设计首页设置页面卡片样式：CSS Grid布局、渐变卡片、hover光效、圆角边框
18. 首页设置页面改回3x2实线边框布局，与首页保持一致
19. 修复首页设置页面3x2布局：使用Bootstrap row g-0 + col-4实现正确的3列2行网格
20. 修复首页设置页面边框显示：使用明确的颜色值替代CSS变量
21. 修复首页设置页面样式加载：使用正确的head_extra block名称替代extra_head
22. 修复安全漏洞：api_regions_path API添加@login_required装饰器
23. 更新模块技术规范：新增「十一、首页卡片系统」章节，提供完整的模块首页卡片开发指南
24. 更新README.md：反映最新的项目结构（modules目录、core/node、core/importexport等），更新功能特点和技术栈说明



# 2026-03-29 修改记录

1. 实现动态URL加载和模块安全加载，系统可在任意模块缺失时正常启动

# 2026-03-30 修改记录

1. 重新创建居民信息模块（代码已重建，模板文件待补充）
2. 修复迁移冲突：将NodeModule类名改为Module，合并迁移文件
3. 更新模块技术规范：添加动态URL加载机制
4. 恢复居民信息模块模板文件：list.html, edit.html, view.html
5. 修复 resident_info 模块模板语法错误，将 Jinja2 模板中的 Django 模板语法转换为 Jinja2 语法
6. 修复 edit.html 模板中 csrf_token 标签语法错误，将 Django 模板语法 {% csrf_token %} 改为 Jinja2 语法 {{ csrf_token }}
7. 修复 resident_info 模块所有模板语法错误，包括将 Django 模板语法转换为 Jinja2 语法，修复 default 过滤器、date 过滤器和 csrf_token 标签
8. 在 ModuleService 中添加 create_module_taxonomies 方法，在安装模块时自动创建模块定义的词汇表
9. 修复 resident_info 模块 bug：delete 方法逻辑错误、node_delete 参数传递错误、redirect 调用方式错误
10. 修复 resident_info 模块 bug：redirect 使用硬编码 URL 改为命名 URL 反向解析，修复 edit.html 模板空指针问题
11. 修复 edit.html 模板中多处空指针问题：访问属性时需先检查 resident 是否为 None
12. 修复 models.py 中 id_card 和 phone 字段缺少 null=True 的问题
13. 修改 init_db.py 模块初始化逻辑，只注册模块不安装/启用
14. 修复 run.py 中 NodeModuleService 导入错误，改为 ModuleService

# 2026-03-31 修改记录

1. 全面 Bug 排查修复：customer/customer_cn services 节点创建返回值检查、core/views 词汇表操作验证、edit_cn.html 重复字段删除、view.html/view_cn.html date 过滤器空值检查
2. 检查 core/views.py 和 core/node/views.py 的参数验证问题
3. 继续排查类似问题：customer/templates/edit.html 8个空值检查、core/views.py taxonomy_edit 验证和 cron_toggle_task JSON 解析、TaxonomyService 添加 get_item 方法
4. 排查类似问题：system_user_edit.html 5处空值检查、node/types/edit.html 和 node/edit.html 4处空值检查、homepage_settings.html 字典安全访问和硬编码URL修复
5. 继续排查 edit_cn.html 5处空值检查修复：postal_code、address、industry、registered_capital、credit_limit、website、notes
6. 删除性别词汇表中“其他”选项，补全居民信息模块民族词汇表为55个民族+其他=56项
7. 修复 module_scan 视图重定向 URL 错误和 node_type_create 视图 try-except 结构错误
8. 修复 module_scan 视图重定向 URL 从 core:node_types 改为 node:modules
9. 修复节点类型相关 URL 配置：添加缺失的 URL 路由，修正 views.py 和模板中的错误 URL 引用
10. 修复 module_scan 视图重定向 URL 从 core:node_types 改为 node:node_types_list
11. 修复 module_scan 重定向从 node_types_list 改为 node:index，扫描完成后返回模块管理页面
12. 修复 module_scan 重定向到 node:modules（模块管理页面）
13. 修复SQLite数据库初始化问题：在database.py中添加自动创建instance目录的逻辑
14. 修复Node模块初始化警告：使用register_and_install替代register_module，确保NodeType在客户数据初始化前创建
15. 为居民信息模块添加README文档（modules/resident_info/README.md）
16. 修复模块安装后错误跳转到节点页的缩进bug（core/node/views.py:289）
17. 添加数据库初始化选择功能：--reset-db 删除重建，--incremental 增量式，无参数时交互式选择



# 2026-04-01 修改记录

1. 删除run.sh中单独的海外/国内客户样本数据初始化菜单选项（功能已包含在初始化系统中）
