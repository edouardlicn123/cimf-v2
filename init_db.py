#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
文件：init_db.py
路径：/home/edo/cimf-v2/init_db.py
================================================================================

功能说明：
    Django 数据库初始化脚本，类似 Flask 的 init_schema.py
    
    主要功能：
    1. 创建所有缺失的表（Django migrate）
    2. 可选：重置系统设置为默认值
    3. 可选：创建/重置默认管理员用户
    4. 可选：初始化词汇表数据
    5. 可选：初始化节点类型
    
用法：
    python init_db.py                    # 仅创建表
    python init_db.py --with-data        # 创建表 + 初始数据
    python init_db.py --with-data --force  # 强制重置 admin 用户
    python init_db.py --dry-run          # 模拟执行
    
环境变量：
    ADMIN_USERNAME: 管理员用户名 (默认: admin)
    ADMIN_NICKNAME: 管理员昵称 (默认: 系统管理员)
    ADMIN_PASSWORD: 管理员密码 (默认: admin123)
    ADMIN_EMAIL: 管理员邮箱 (默认: admin@example.com)
    ADMIN_THEME: 主题偏好 (默认: default)
    ALLOW_SEED_PROD: 允许在生产环境执行 (默认: false)

版本：
    - 1.0: 从 Flask init_schema.py 迁移

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
        "white": "\033[97m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"


def _validate_and_fix_installed_apps(settings):
    """
    验证 INSTALLED_APPS 中的模块状态
    
    注意：由于 settings.py 已使用动态扫描，此函数仅输出已加载的模块信息
    """
    loaded_node_modules = [app for app in settings.INSTALLED_APPS if app.startswith('modules.')]
    print(colored(f"  已加载 Node 模块: {', '.join(loaded_node_modules) if loaded_node_modules else '无'}", "cyan"))


def init_database(with_data: bool = False, force: bool = False, dry_run: bool = False):
    """
    初始化数据库核心逻辑：
    1. 创建所有缺失的表（Django migrate）
    2. 可选：重置系统设置默认值
    3. 可选：创建/重置默认管理员用户
    4. 可选：初始化词汇表数据
    """
    print(colored(f"CIMF 管理系统 - 数据库初始化工具 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})", "cyan"))
    print(colored(f"当前环境: {os.environ.get('DJANGO_ENV', 'development')}", "cyan"))
    print("-" * 80)

    if dry_run:
        print(colored("【DRY-RUN 模式】仅模拟执行，不会修改数据库", "yellow"))
        print("-" * 80)

    # 设置 Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cimf_django.settings')
    
    # 导入 Django
    import django
    django.setup()

    from django.conf import settings
    from django.db import connection
    
    # 验证并修复 INSTALLED_APPS
    _validate_and_fix_installed_apps(settings)
    
    from core.models import User, SystemSetting, Taxonomy
    from core.services import SettingsService, PermissionService, UserRole

    print(colored(f"数据库: {settings.DATABASES['default']['NAME']}", "cyan"))
    print("-" * 80)

    # 步骤 1: 执行 Django 迁移
    print(colored("步骤 1: 执行 Django migrations ...", "yellow"))
    
    if not dry_run:
        from django.core.management import execute_from_command_line
        try:
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            print(colored("Migrations 执行完成", "green"))
        except Exception as e:
            print(colored(f"Migrations 执行失败: {str(e)}", "red"))
            sys.exit(1)
    else:
        print(colored("[模拟] 将执行 python manage.py migrate --noinput", "yellow"))

    if not with_data:
        print(colored("未指定 --with-data，跳过初始数据插入", "yellow"))
        print("-" * 80)
        return

    # 步骤 2: 初始化系统设置
    print(colored("\n步骤 2.1: 初始化系统设置默认值...", "blue"))
    
    try:
        if not dry_run:
            reset_count = SettingsService.reset_to_default()
            print(colored(f"  系统设置默认值已重置/插入，共 {reset_count} 项", "green"))
        else:
            print(colored("[模拟] 将调用 SettingsService.reset_to_default()", "yellow"))
    except Exception as e:
        print(colored(f"  系统设置初始化失败: {str(e)}", "red"))
        if not dry_run:
            sys.exit(1)

    # 步骤 3: 初始化角色权限
    print(colored("\n步骤 2.2: 初始化角色默认权限...", "blue"))
    
    try:
        if not dry_run:
            PermissionService.init_default_role_permissions()
            print(colored("  角色权限初始化完成", "green"))
        else:
            print(colored("[模拟] 将调用 PermissionService.init_default_role_permissions()", "yellow"))
    except Exception as e:
        print(colored(f"  角色权限初始化失败: {str(e)}", "red"))

    # 步骤 4: 初始化词汇表数据
    print(colored("\n步骤 2.3: 初始化词汇表数据...", "blue"))
    
    try:
        if not dry_run:
            from core.services.taxonomy_service import TaxonomyService
            created_count = TaxonomyService.init_default_taxonomies()
            print(colored(f"  词汇表数据初始化完成，共创建 {created_count} 个词汇表", "green"))
        else:
            print(colored("[模拟] 将调用 TaxonomyService.init_default_taxonomies()", "yellow"))
    except Exception as e:
        print(colored(f"  词汇表数据初始化失败: {str(e)}", "red"))

    # 步骤 5: 初始化节点类型数据（已废弃，使用动态模块系统）
    print(colored("\n步骤 2.4: 初始化节点类型数据...", "blue"))
    print(colored("  已移至动态模块系统，跳过", "yellow"))
    
    # 步骤 5.1: 初始化 Node 模块（列表加载 + 安装）
    print(colored("\n步骤 2.4.1: 初始化 Node 模块...", "blue"))
    
    try:
        if not dry_run:
            from core.node.services import NodeModuleService
            
            modules = NodeModuleService.scan_modules()
            installed_count = 0
            
            for m in modules:
                module = NodeModuleService.register_module(m)
                if NodeModuleService.install_module(m['id']):
                    NodeModuleService.enable_module(m['id'])
                    installed_count += 1
            
            print(colored(f"  Node 模块初始化完成: {installed_count} 个模块", "green"))
        else:
            print(colored("[模拟] 将扫描 modules/ 目录并安装模块", "yellow"))
    except Exception as e:
        print(colored(f"  Node 模块初始化失败: {str(e)}", "red"))
    
    # 步骤 6: 初始化海外客户样本数据
    print(colored("\n步骤 2.5: 初始化海外客户样本数据...", "blue"))
    
    try:
        if not dry_run:
            from django.core.management import call_command
            from io import StringIO
            out = StringIO()
            call_command('init_overseas_customers', stdout=out)
            print(colored(f"  海外客户样本数据初始化完成: {out.getvalue().strip().split('完成! ')[-1]}", "green"))
        else:
            print(colored("[模拟] 将调用 init_overseas_customers 命令", "yellow"))
    except Exception as e:
        print(colored(f"  海外客户样本数据初始化失败: {str(e)}", "red"))
    
    # 步骤 7: 初始化国内客户样本数据
    print(colored("\n步骤 2.6: 初始化国内客户样本数据...", "blue"))
    
    try:
        if not dry_run:
            from django.core.management import call_command
            from io import StringIO
            out = StringIO()
            call_command('init_domestic_customers', stdout=out)
            print(colored(f"  国内客户样本数据初始化完成: {out.getvalue().strip().split('完成! ')[-1]}", "green"))
        else:
            print(colored("[模拟] 将调用 init_domestic_customers 命令", "yellow"))
    except Exception as e:
        print(colored(f"  国内客户样本数据初始化失败: {str(e)}", "red"))

    # 步骤 5: 创建管理员用户
    print(colored("\n步骤 2.3: 初始化默认管理员用户...", "blue"))

    # 默认管理员配置（环境变量覆盖优先）
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_nickname = os.environ.get('ADMIN_NICKNAME', '系统管理员')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_theme = os.environ.get('ADMIN_THEME', 'default')
    admin_notifications = os.environ.get('ADMIN_NOTIFICATIONS', 'true').lower() in ('true', '1', 'yes', 'on')
    admin_language = os.environ.get('ADMIN_PREFERRED_LANGUAGE', 'zh')

    env = os.environ.get('DJANGO_ENV', 'development')

    # 生产环境安全限制
    if env == 'production' and not os.environ.get('ALLOW_SEED_PROD'):
        print(colored("【生产环境安全限制】禁止自动插入初始数据！", "red"))
        print("如需强制执行，请设置环境变量 ALLOW_SEED_PROD=1 （极度不推荐）")
        sys.exit(1)

    # 密码长度最低要求（仅生产环境强制检查）
    if env == 'production':
        if len(admin_password) < 10:
            print(colored("错误：管理员密码长度不足 10 位！请通过环境变量 ADMIN_PASSWORD 设置更强密码", "red"))
            sys.exit(1)

    existing_admin = User.objects.filter(username=admin_username).first()

    if existing_admin and not force:
        print(colored(f"管理员 '{admin_username}' 已存在，跳过创建（使用 --force 可强制重置）", "yellow"))
    else:
        if existing_admin and force:
            print(colored(f"强制删除旧管理员 '{admin_username}' ...", "yellow"))
            if not dry_run:
                existing_admin.delete()

        if not dry_run:
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
            )
            admin.set_password(admin_password)
            admin.save()

            print(colored("成功创建/重置默认管理员：", "green"))
            print(f"  用户名: {admin_username}")
            print(f"  昵称: {admin_nickname}")
            print(f"  密码: {admin_password} （生产环境请立即修改！）")
            print(f"  邮箱: {admin_email}")
            print(f"  角色: 管理员")
            print(colored("\n警告：请登录后立即修改密码！", "yellow"))
        else:
            print(colored(f"[模拟] 将创建管理员用户: {admin_username}", "yellow"))

    print(colored("\n所有初始化完成！", "green"))
    print("-" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="CIMF 数据库初始化脚本",
        epilog="生产环境请谨慎使用此脚本"
    )
    parser.add_argument("--with-data", action="store_true", 
                        help="创建表 + 插入/重置初始管理员 + 系统设置默认记录")
    parser.add_argument("--force", action="store_true", 
                        help="强制重置 admin 用户")
    parser.add_argument("--dry-run", action="store_true", 
                        help="模拟执行，不实际写入数据库")
    args = parser.parse_args()

    try:
        init_database(
            with_data=args.with_data,
            force=args.force,
            dry_run=args.dry_run
        )
        print(colored("\n初始化流程完成。", "green"))
        if args.with_data:
            print(colored("下一步建议：", "cyan"))
            print("  1. 启动服务: python run.py")
            print("  2. 登录后台访问 / 验证仪表盘")
            print("  3. 访问 /system/settings 验证设置表内容")
            print("  4. 强烈建议生产环境修改管理员密码")
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
