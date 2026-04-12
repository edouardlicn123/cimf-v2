#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
文件：init_db.py
路径：/home/edo/cimf/init_db.py
================================================================================

功能说明：
    Django 数据库初始化脚本
    
    初始化阶段：
    【阶段1】数据库结构 - 执行 Django migrations（仅核心模块）
    【阶段2】系统配置 - 设置、权限、词汇表
    【阶段3】用户管理 - 创建管理员
    【阶段4】业务模块 - 扫描并注册模块（不安装，不创建表）
    
    注意：
    - 模块的安装（包括建表、初始化样本数据）在用户手动安装模块时执行
    - 使用 ./run.sh → 5 → 3 进入模块管理页面手动安装
    
用法：
    python init_db.py                         # 仅创建核心表
    python init_db.py --with-data            # 创建表 + 初始数据
    python init_db.py --with-data --force    # 强制重置 admin 用户
    python init_db.py --with-data --reset-db # 删除数据库后重新初始化
    python init_db.py --with-data --incremental # 增量式初始化
    python init_db.py --dry-run              # 模拟执行
    python init_db.py --skip-migrate         # 跳过 migrations（外部已执行时使用）
    
环境变量：
    ADMIN_USERNAME: 管理员用户名 (默认: admin)
    ADMIN_NICKNAME: 管理员昵称 (默认: 系统管理员)
    ADMIN_PASSWORD: 管理员密码 (默认: admin123)
    ADMIN_EMAIL: 管理员邮箱 (默认: admin@example.com)
    ADMIN_THEME: 主题偏好 (默认: default)
    ALLOW_SEED_PROD: 允许在生产环境执行 (默认: false)

版本：
    - 3.0: 重构为系统初始化与模块初始化分离

依赖：
    - Django 6.0+
"""

import os
import sys
import argparse
from datetime import datetime


def colored(text: str, color: str = "white") -> str:
    """终端颜色辅助函数"""
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "white": "\033[97m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"


def print_section(title: str):
    """打印阶段标题"""
    print()
    bold_cyan = f"\033[1m\033[96m【{title}】\033[0m"
    print(bold_cyan)
    print(colored("=" * 60, "cyan"))


def print_step(step_num: str, description: str):
    """打印步骤"""
    print(colored(f"  {step_num}. {description}", "blue"))


def _init_system_config_parallel(dry_run: bool) -> dict:
    """初始化系统配置（串行执行，SQLite 不支持并发）"""
    
    results = {
        'settings': {'count': 0, 'success': False, 'error': None},
        'permissions': {'success': False, 'error': None},
        'taxonomies': {'count': 0, 'success': False, 'error': None},
        'templates': {'count': 0, 'success': False, 'error': None},
    }
    
    if dry_run:
        return results
    
    # SQLite 不支持并发写入，改用串行执行
    try:
        from core.services import SettingsService
        results['settings'] = {'count': SettingsService.reset_to_default(), 'success': True}
    except Exception as e:
        results['settings'] = {'error': str(e)}
    
    try:
        from core.services import PermissionService
        PermissionService.init_default_role_permissions()
        results['permissions'] = {'success': True}
    except Exception as e:
        results['permissions'] = {'error': str(e)}
    
    try:
        from core.services.taxonomy_service import TaxonomyService
        results['taxonomies'] = {'count': TaxonomyService.init_default_taxonomies(), 'success': True}
    except Exception as e:
        results['taxonomies'] = {'error': str(e)}
    
    try:
        from core.smtp.services.template_service import TemplateService
        results['templates'] = {'count': TemplateService.init_default_templates(), 'success': True}
    except Exception as e:
        results['templates'] = {'error': str(e)}
    
    return results
    
    return results


def _init_modules_parallel(dry_run: bool) -> dict:
    """并行扫描并安装业务模块"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from core.node.services import ModuleService
    
    results = {'installed': 0, 'skipped': 0, 'success': False}
    
    if dry_run:
        results['message'] = '[模拟] 将串行注册模块'
        return results
    
    all_modules = ModuleService.scan_modules()
    
    pending_modules = [
        m for m in all_modules
        if not (m.get('is_registered') and m.get('is_installed'))
    ]
    
    results['skipped'] = len(all_modules) - len(pending_modules)
    
    if not pending_modules:
        results['success'] = True
        return results
    
    # SQLite 不支持并发写入，改用串行执行
    for m in pending_modules:
        try:
            ModuleService.register_and_install(m)
            results['installed'] += 1
        except Exception as e:
            results['error'] = str(e)
    
    results['success'] = True
    return results


def ask_reset_mode(db_path: str) -> bool:
    """
    交互式询问用户初始化模式
    
    Args:
        db_path: 数据库路径描述
        
    Returns:
        bool: True 表示删除重建，False 表示增量式
    """
    print(colored(f"检测到已存在的数据库: {db_path}", "yellow"))
    print(colored("请选择初始化模式：", "cyan"))
    print(colored("  [1] 删除原有数据库并重新初始化（会丢失所有数据）", "white"))
    print(colored("  [2] 增量式初始化（保留现有数据，仅更新结构）", "white"))
    
    while True:
        try:
            choice = input(colored("请选择 (1/2): ", "cyan")).strip()
            if choice == '1':
                return True
            elif choice == '2':
                return False
            else:
                print(colored("无效选择，请输入 1 或 2", "red"))
        except (KeyboardInterrupt, EOFError):
            print(colored("\n用户取消操作", "yellow"))
            sys.exit(0)


def _has_pending_migrations() -> bool:
    """检查是否有待执行的迁移"""
    from django.core.management import call_command
    from io import StringIO
    
    out = StringIO()
    call_command('showmigrations', '--plan', stdout=out)
    lines = out.getvalue().strip().split('\n')
    return any(line.startswith('[ ]') for line in lines)


def init_database(with_data: bool = False, force: bool = False, dry_run: bool = False,
                  reset_db: bool = False, incremental: bool = False, skip_migrate: bool = False):
    """
    初始化数据库核心逻辑
    
    Args:
        with_data: 是否初始化初始数据
        force: 是否强制重置管理员用户
        dry_run: 是否模拟执行
        reset_db: 是否删除数据库后重建
        incremental: 是否增量式初始化
        skip_migrate: 是否跳过 migrations（外部已执行时使用）
    """
    banner = f"\033[1m\033[96m{'='*60}\033[0m"
    print(banner)
    print(colored(f"CIMF 管理系统 - 数据库初始化工具", "cyan"))
    print(colored(f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})", "cyan"))
    print(banner)
    print(colored(f"当前环境: {os.environ.get('DJANGO_ENV', 'development')}", "cyan"))

    if dry_run:
        print(colored("【DRY-RUN 模式】仅模拟执行，不会修改数据库", "yellow"))
        print(colored("=" * 60, "cyan"))

    # 导入数据库工具
    from cimf_django.database import database_exists, drop_database, get_database_config
    
    # 检查数据库是否存在
    db_exists = database_exists()
    db_config = get_database_config()
    db_path = str(db_config.get('NAME', 'unknown'))
    
    # 处理数据库删除逻辑
    if db_exists:
        if reset_db:
            print(colored("检测到已存在的数据库", "yellow"))
            print(colored("【删除重建模式】正在删除原有数据库...", "yellow"))
            if not dry_run:
                drop_database()
                print(colored("数据库已删除，将重新创建", "green"))
            else:
                print(colored(f"[模拟] 将删除数据库: {db_path}", "yellow"))
        elif incremental:
            print(colored("检测到已存在的数据库", "yellow"))
            print(colored("【增量式模式】保留现有数据，仅更新结构", "cyan"))
        else:
            should_reset = ask_reset_mode(db_path)
            if should_reset:
                print(colored("【删除重建模式】正在删除原有数据库...", "yellow"))
                if not dry_run:
                    drop_database()
                    print(colored("数据库已删除，将重新创建", "green"))
                else:
                    print(colored(f"[模拟] 将删除数据库: {db_path}", "yellow"))
            else:
                print(colored("【增量式模式】保留现有数据，仅更新结构", "cyan"))
    else:
        print(colored("未检测到数据库文件，将执行全新初始化...", "cyan"))

    print(colored("=" * 60, "cyan"))

    # 设置 Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cimf_django.settings')
    
    import django
    django.setup()

    from django.conf import settings
    from django.db import connection
    
    print(colored(f"数据库: {settings.DATABASES['default']['NAME']}", "cyan"))
    print(colored("=" * 60, "cyan"))

    # ===== 【阶段1】数据库结构 =====
    print_section("阶段1：数据库结构")
    print_step("1.1", "执行 Django migrations")
    
    if skip_migrate:
        print(colored("    ⊘ 跳过（由外部脚本执行）", "yellow"))
    elif incremental and db_exists:
        if not dry_run:
            if not _has_pending_migrations():
                print(colored("    ⊘ 无待执行迁移，跳过", "green"))
            else:
                from django.core.management import execute_from_command_line
                execute_from_command_line(['manage.py', 'migrate', '--noinput'])
                print(colored("    ✓ migrations 执行完成", "green"))
        else:
            print(colored("    [模拟] 将检查并执行 pending migrations", "yellow"))
    elif not dry_run:
        from django.core.management import execute_from_command_line
        try:
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            print(colored("    ✓ migrations 执行完成", "green"))
        except Exception as e:
            print(colored(f"    ✗ migrations 执行失败: {str(e)}", "red"))
            sys.exit(1)
    else:
        print(colored("    [模拟] 将执行 python manage.py migrate --noinput", "yellow"))

    if not with_data:
        print(colored("\n未指定 --with-data，跳过初始数据插入", "yellow"))
        print(colored("=" * 60, "cyan"))
        return

    # ===== 【阶段2】系统配置 =====
    print_section("阶段2：系统配置")
    
    print_step("2.1-2.4", "初始化系统配置（设置、权限、词汇表、邮件模板）")
    
    try:
        if not dry_run:
            config_results = _init_system_config_parallel(dry_run=False)
            
            if config_results.get('settings', {}).get('success'):
                count = config_results.get('settings', {}).get('count', 0)
                print(colored(f"    ✓ 系统设置默认值已重置/插入，共 {count} 项", "green"))
            
            if config_results.get('permissions', {}).get('success'):
                print(colored("    ✓ 角色权限初始化完成", "green"))
            
            if config_results.get('taxonomies', {}).get('success'):
                count = config_results.get('taxonomies', {}).get('count', 0)
                print(colored(f"    ✓ 词汇表数据初始化完成，共创建 {count} 个词汇表", "green"))
            
            if config_results.get('templates', {}).get('success'):
                count = config_results.get('templates', {}).get('count', 0)
                print(colored(f"    ✓ 邮件模板初始化完成，共创建 {count} 个模板", "green"))
            
            errors = [f"{k}: {v.get('error')}" for k, v in config_results.items() if v.get('error')]
            if errors:
                print(colored(f"    ⚠ 部分任务执行异常: {'; '.join(errors)}", "yellow"))
        else:
            result = _init_system_config_parallel(dry_run=True)
            print(colored(f"    {result.get('message', '[模拟]')}", "yellow"))
    except Exception as e:
        print(colored(f"    ✗ 系统配置初始化失败: {str(e)}", "red"))
        if not dry_run:
            sys.exit(1)
    
    from core.models import User, SystemSetting, Taxonomy
    from core.services import SettingsService, PermissionService, UserRole

    # ===== 【阶段3】用户管理 =====
    print_section("阶段3：用户管理")
    
    print_step("3.1", "创建管理员用户")
    
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_nickname = os.environ.get('ADMIN_NICKNAME', '系统管理员')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_theme = os.environ.get('ADMIN_THEME', 'default')
    admin_notifications = os.environ.get('ADMIN_NOTIFICATIONS', 'true').lower() in ('true', '1', 'yes', 'on')
    admin_language = os.environ.get('ADMIN_PREFERRED_LANGUAGE', 'zh')

    env = os.environ.get('DJANGO_ENV', 'development')

    if env == 'production' and not os.environ.get('ALLOW_SEED_PROD'):
        print(colored("【生产环境安全限制】禁止自动插入初始数据！", "red"))
        print(colored("如需强制执行，请设置环境变量 ALLOW_SEED_PROD=1 （极度不推荐）"))
        sys.exit(1)

    if env == 'production':
        if len(admin_password) < 10:
            print(colored("错误：管理员密码长度不足 10 位！请通过环境变量 ADMIN_PASSWORD 设置更强密码", "red"))
            sys.exit(1)

    existing_admin = User.objects.filter(username=admin_username).first()

    if existing_admin and not force:
        print(colored(f"    - 管理员 '{admin_username}' 已存在，跳过创建", "yellow"))
        if force:
            print(colored(f"    (使用 --force 可强制重置)", "yellow"))
    else:
        if existing_admin and force:
            print(colored(f"    - 强制删除旧管理员 '{admin_username}' ...", "yellow"))
            if not dry_run:
                existing_admin.delete()

        if not dry_run:
            DEFAULT_NAV_CARDS = [
                {"id": "default-1", "name": "必应搜索", "url": "https://www.bing.com", "bg_color": "#3584e4", "position": 1},
                {"id": "default-2", "name": "豆包", "url": "https://www.doubao.com", "bg_color": "#2ec27e", "position": 2},
                {"id": "default-3", "name": "千问", "url": "https://tongyi.aliyun.com", "bg_color": "#9141ac", "position": 3},
                {"id": "default-4", "name": "百度地图", "url": "https://map.baidu.com", "bg_color": "#2932e1", "position": 4},
                {"id": "default-5", "name": "哔哩哔哩", "url": "https://www.bilibili.com", "bg_color": "#00a1d6", "position": 5},
                {"id": "default-6", "name": "36氪", "url": "https://36kr.com", "bg_color": "#f85959", "position": 6},
            ]
            admin = User.objects.create_user(
                username=admin_username,
                nickname=admin_nickname,
                email=admin_email,
                role=UserRole.MANAGER,
                is_admin=True,
                is_active=True,
                theme=admin_theme,
                notifications_enabled=admin_notifications,
                preferred_language=admin_language,
                navigation_cards=DEFAULT_NAV_CARDS,
            )
            admin.set_password(admin_password)
            admin.save()

            print(colored("    ✓ 管理员用户创建成功", "green"))
            print(f"      用户名: {admin_username}")
            print(f"      昵称: {admin_nickname}")
            print(f"      密码: {admin_password} （生产环境请立即修改！）")
            print(colored("    ⚠ 请登录后立即修改密码！", "yellow"))
        else:
            print(colored(f"    [模拟] 将创建管理员用户: {admin_username}", "yellow"))

    # ===== 【阶段4】业务模块 =====
    print_section("阶段4：业务模块")
    
    print_step("4.1", "扫描并安装业务模块")
    try:
        if not dry_run:
            module_results = _init_modules_parallel(dry_run=False)
            
            msg = "    ✓ 业务模块扫描安装完成"
            if module_results.get('installed', 0) > 0:
                msg += f"，已安装 {module_results.get('installed')} 个"
            if module_results.get('skipped', 0) > 0:
                msg += f"，跳过 {module_results.get('skipped')} 个已安装模块"
            print(colored(msg, "green"))
            
            if module_results.get('error'):
                print(colored(f"    ⚠ 部分模块异常: {module_results.get('error')}", "yellow"))
        else:
            result = _init_modules_parallel(dry_run=True)
            print(colored(f"    {result.get('message', '[模拟]')}", "yellow"))
    except Exception as e:
        print(colored(f"    ✗ 业务模块初始化失败: {str(e)}", "red"))

    # ===== 完成 =====
    print()
    print(colored(f"{'='*60}", "green"))
    print(colored("✓ 所有初始化完成！", "green"))
    print(colored(f"{'='*60}", "green"))
    
    if with_data:
        print(colored("\n下一步建议：", "cyan"))
        print("  1. 启动服务: ./run.sh")
        print("  2. 访问 /auth/login 登录后台")
        print("  3. 强烈建议生产环境修改管理员密码")


def main():
    parser = argparse.ArgumentParser(
        description="CIMF 数据库初始化脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
初始化阶段：
  【阶段1】数据库结构 - 执行 Django migrations（仅核心模块）
  【阶段2】系统配置 - 设置、权限、词汇表
  【阶段3】用户管理 - 创建管理员
  【阶段4】业务模块 - 扫描并注册模块（不安装，不创建表）

  注意：模块安装需在模块管理页面手动执行

生产环境请谨慎使用此脚本
        """
    )
    parser.add_argument("--with-data", action="store_true", 
                        help="创建表 + 插入/重置初始管理员 + 系统设置默认记录")
    parser.add_argument("--force", action="store_true", 
                        help="强制重置 admin 用户")
    parser.add_argument("--dry-run", action="store_true", 
                        help="模拟执行，不实际写入数据库")
    parser.add_argument("--reset-db", action="store_true",
                        help="删除原有数据库后重新初始化（会丢失所有数据）")
    parser.add_argument("--incremental", action="store_true",
                        help="增量式初始化（保留现有数据，仅更新结构）")
    parser.add_argument("--skip-migrate", action="store_true",
                        help="跳过 migrations（外部已执行时使用）")
    
    global args
    args = parser.parse_args()

    if args.reset_db and args.incremental:
        print(colored("错误：--reset-db 和 --incremental 不能同时使用", "red"))
        sys.exit(1)

    try:
        init_database(
            with_data=args.with_data,
            force=args.force,
            dry_run=args.dry_run,
            reset_db=args.reset_db,
            incremental=args.incremental,
            skip_migrate=args.skip_migrate
        )
    except KeyboardInterrupt:
        print("\n用户取消操作。")
        sys.exit(0)
    except Exception as e:
        print(colored(f"初始化过程中发生未预期错误: {str(e)}", "red"), file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
