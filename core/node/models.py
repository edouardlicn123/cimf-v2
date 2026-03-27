# -*- coding: utf-8 -*-
"""
================================================================================
文件：models.py
路径：/home/edo/cimf-v2/core/node/models.py
================================================================================

功能说明：
    Node 节点系统模型，包含节点类型和节点主表
    
    主要模型：
    - NodeType: 节点类型
    - Node: 节点主表

版本：
    - 1.0: 从 nodes/models.py 迁移

依赖：
    - django.db: 数据模型
    - django.conf.settings: 用户模型
"""

import os

from django.db import models
from django.conf import settings
from django.conf import settings


class NodeType(models.Model):
    """
    节点类型模型
    
    定义节点的结构，包括名称、标识符、字段配置等
    """
    
    name = models.CharField(max_length=100, verbose_name='节点类型名称')
    slug = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='标识符')
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name='描述')
    icon = models.CharField(max_length=50, default='bi-folder', verbose_name='图标')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    fields_config = models.JSONField(default=list, verbose_name='字段配置')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'node_types'
        verbose_name = '节点类型'
        verbose_name_plural = '节点类型'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_node_count(self):
        return self.nodes.count()


class Node(models.Model):
    """
    节点主表
    
    所有节点类型的公共字段，包含创建人、更新时间等
    """
    
    node_type = models.ForeignKey(
        NodeType,
        on_delete=models.CASCADE,
        related_name='nodes',
        verbose_name='节点类型'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_nodes',
        verbose_name='创建人'
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_nodes',
        verbose_name='更新人'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'nodes'
        verbose_name = '节点'
        verbose_name_plural = '节点'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Node {self.id} ({self.node_type.slug})'


class NodeModule(models.Model):
    """Node 模块注册表"""
    
    module_id = models.CharField(max_length=50, unique=True, verbose_name='模块ID')
    name = models.CharField(max_length=100, verbose_name='模块名称')
    version = models.CharField(max_length=20, verbose_name='版本号')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    path = models.CharField(max_length=200, verbose_name='模块路径')
    
    is_installed = models.BooleanField(default=False, verbose_name='是否已安装')
    is_active = models.BooleanField(default=False, verbose_name='是否启用')
    is_system = models.BooleanField(default=False, verbose_name='是否系统默认模块')
    
    installed_at = models.DateTimeField(null=True, blank=True, verbose_name='安装时间')
    activated_at = models.DateTimeField(null=True, blank=True, verbose_name='启用时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'node_modules'
        verbose_name = 'Node模块'
        verbose_name_plural = 'Node模块'
        ordering = ['name']
    
    @property
    def path_exists(self) -> bool:
        """检查模块目录是否存在"""
        if not self.path:
            return False
        module_path = os.path.join(settings.BASE_DIR, 'modules', self.path)
        return os.path.isdir(module_path)
    
    def __str__(self):
        return f"{self.name} ({self.module_id})"