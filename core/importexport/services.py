# -*- coding: utf-8 -*-
"""
数据导入导出服务（向后兼容）

此文件已废弃，内容已迁移到 core/importexport/services/ 目录
保留此文件以保持向后兼容
"""

from core.importexport.services import ImportService, ExportService, TemplateGenerator

__all__ = ['ImportService', 'ExportService', 'TemplateGenerator']