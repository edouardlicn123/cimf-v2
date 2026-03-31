# -*- coding: utf-8 -*-
"""
数据库配置模块

根据 config.env 配置返回 Django DATABASES 格式的数据库配置
支持 SQLite 和 MySQL 两种数据库
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_database_config():
    """
    根据配置获取数据库配置
    
    读取 config.env 中的 DB_TYPE、DB_NAME、DB_USER 等配置
    返回 Django DATABASES 格式的配置字典
    
    Returns:
        dict: Django DATABASES 配置
    """
    
    config_path = BASE_DIR / 'config.env'
    db_config = _load_config(config_path)
    
    db_type = db_config.get('DB_TYPE', 'sqlite').lower().strip()
    
    if db_type == 'mysql':
        return _get_mysql_config(db_config)
    else:
        return _get_sqlite_config()


def _load_config(config_path: Path) -> dict:
    """
    读取配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        dict: 配置字典
    """
    config = {}
    
    if not config_path.exists():
        return config
    
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config


def _get_sqlite_config() -> dict:
    """获取 SQLite 配置"""
    db_path = BASE_DIR / 'instance' / 'django.db'
    # 确保 instance 目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': db_path,
    }


def _get_mysql_config(config: dict) -> dict:
    """获取 MySQL 配置"""
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config.get('DB_NAME', 'cimf'),
        'USER': config.get('DB_USER', 'root'),
        'PASSWORD': config.get('DB_PASSWORD', ''),
        'HOST': config.get('DB_HOST', 'localhost'),
        'PORT': config.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }