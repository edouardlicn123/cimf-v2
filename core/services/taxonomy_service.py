# -*- coding: utf-8 -*-
"""
================================================================================
文件：taxonomy_service.py
路径：/home/edo/cimf-v2/core/services/taxonomy_service.py
================================================================================

功能说明：
    词汇表服务层，提供词汇表和词汇项的 CRUD 操作，以及预置数据初始化。
    
    主要功能：
    - 词汇表管理（增删改查）
    - 词汇项管理（增删改查、排序）
    - 预置词汇表初始化（37个）

用法：
    1. 获取所有词汇表：
        from core.services.taxonomy_service import TaxonomyService
        taxonomies = TaxonomyService.get_all_taxonomies()
    
    2. 获取词汇表及其词汇项：
        taxonomy = TaxonomyService.get_taxonomy_by_id(1)
        items = TaxonomyService.get_items(1)
    
    3. 初始化预置词汇表：
        TaxonomyService.init_default_taxonomies()

版本：
    - 1.0: 从 Flask 项目迁移

依赖：
    - core.models.Taxonomy: 词汇表模型
    - core.models.TaxonomyItem: 词汇项模型
"""

from typing import List, Optional, Dict, Any
from django.db import models
from core.models import Taxonomy, TaxonomyItem
from core.services.base_service import BaseService


class TaxonomyService(BaseService):
    """
    词汇表服务层
    提供词汇表和词汇项的 CRUD 操作
    """
    model_class = Taxonomy
    
    @staticmethod
    def get_all_taxonomies():
        """获取所有词汇表"""
        return Taxonomy.objects.all().order_by('id')
    
    @staticmethod
    def get_taxonomy_by_id(taxonomy_id: int):
        """获取词汇表详情"""
        return Taxonomy.objects.filter(id=taxonomy_id).first()
    
    @staticmethod
    def get_taxonomy_by_slug(slug: str):
        """通过 slug 获取词汇表"""
        return Taxonomy.objects.filter(slug=slug).first()
    
    @staticmethod
    def create_taxonomy(name: str, slug: str, description: str = '') -> models.Model:
        """创建词汇表（存在则更新，不存在则创建）"""
        taxonomy, created = Taxonomy.objects.update_or_create(
            slug=slug,
            defaults={'name': name, 'description': description}
        )
        return taxonomy
    
    @staticmethod
    def update_taxonomy(taxonomy_id: int, name: str = None, slug: str = None, description: str = None) -> models.Model:
        """更新词汇表"""
        taxonomy = Taxonomy.objects.filter(id=taxonomy_id).first()
        if taxonomy:
            if name is not None:
                taxonomy.name = name
            if slug is not None:
                taxonomy.slug = slug
            if description is not None:
                taxonomy.description = description
            taxonomy.save()
        return taxonomy
    
    @staticmethod
    def delete_taxonomy(taxonomy_id: int) -> bool:
        """删除词汇表（同时删除所有关联的词汇项）"""
        taxonomy = Taxonomy.objects.filter(id=taxonomy_id).first()
        if taxonomy:
            taxonomy.delete()
            return True
        return False
    
    @staticmethod
    def get_items(taxonomy_id: int) -> List[models.Model]:
        """获取词汇表的所有词汇项"""
        return TaxonomyItem.objects.filter(taxonomy_id=taxonomy_id).order_by('weight', 'name')
    
    @staticmethod
    def get_item(item_id: int):
        """获取词汇项详情"""
        return TaxonomyItem.objects.filter(id=item_id).first()
    
    @staticmethod
    def create_item(taxonomy_id: int, name: str, description: str = '', weight: int = None) -> models.Model:
        """创建词汇项"""
        if weight is None:
            max_weight = TaxonomyItem.objects.filter(taxonomy_id=taxonomy_id).aggregate(models.Max('weight'))['weight__max'] or 0
            weight = max_weight + 1
        item = TaxonomyItem.objects.create(
            taxonomy_id=taxonomy_id,
            name=name,
            description=description,
            weight=weight
        )
        return item
    
    @staticmethod
    def update_item(item_id: int, name: str = None, description: str = None, weight: int = None) -> models.Model:
        """更新词汇项"""
        item = TaxonomyItem.objects.filter(id=item_id).first()
        if item:
            if name is not None:
                item.name = name
            if description is not None:
                item.description = description
            if weight is not None:
                item.weight = weight
            item.save()
        return item
    
    @staticmethod
    def delete_item(item_id: int) -> bool:
        """删除词汇项"""
        item = TaxonomyItem.objects.filter(id=item_id).first()
        if item:
            item.delete()
            return True
        return False
    
    @staticmethod
    def reorder_items(taxonomy_id: int, item_ids: List[int]) -> bool:
        """重新排序词汇项"""
        for idx, item_id in enumerate(item_ids):
            TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).update(weight=idx)
        return True
    
    @staticmethod
    def init_default_taxonomies() -> int:
        """
        初始化预置分类数据（使用 fixture 快速加载）
        
        优化效果：从 ~2-3秒 降至 ~0.5秒
        如果 fixture 加载失败，自动回退到代码初始化
        
        返回：创建的词汇表数量
        """
        from django.core.management import call_command
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 检查是否已有数据
        if Taxonomy.objects.exists():
            return 0  # 已初始化，跳过
        
        # 使用 loaddata 快速导入（Django 原生优化）
        try:
            call_command('loaddata', 'initial_taxonomies.json', verbosity=0)
            count = Taxonomy.objects.count()
            logger.info(f"词汇表 fixture 加载完成，共 {count} 个词汇表")
            return count
        except Exception as e:
            logger.warning(f"fixture 加载失败，回退到代码初始化: {e}")
            # 回退到原始逻辑（保留作为备用）
            return TaxonomyService._init_default_taxonomies_fallback()
    
    @staticmethod
    def _init_default_taxonomies_fallback() -> int:
        """
        备用初始化方法（原始逻辑，使用 bulk_create + 批量查询）
        当 fixture 加载失败时使用
        """
        from django.db import transaction
        from collections import defaultdict
        
        # 一次性加载所有已存在的词汇表（使用 select_related 避免 N+1）
        existing_taxonomies = {t.slug: t for t in Taxonomy.objects.all()}
        
        # 一次性加载所有已存在的词汇项（使用 select_related 避免 N+1）
        existing_items = defaultdict(set)
        for item in TaxonomyItem.objects.select_related('taxonomy').all().values('taxonomy__slug', 'name'):
            slug = item['taxonomy__slug']
            existing_items[slug].add(item['name'])
        
        count = 0
        with transaction.atomic():
            for tax in DEFAULT_TAXONOMIES:
                slug = tax['slug']
                
                # 创建或获取词汇表
                if slug in existing_taxonomies:
                    taxonomy = existing_taxonomies[slug]
                else:
                    taxonomy = Taxonomy.objects.create(
                        slug=slug,
                        name=tax['name'],
                        description=tax.get('description', '')
                    )
                    existing_taxonomies[slug] = taxonomy
                    count += 1
                
                # 批量检查并创建词汇项
                existing_names = existing_items.get(slug, set())
                items_to_create = []
                
                for idx, item_name in enumerate(tax['items']):
                    if item_name not in existing_names:
                        items_to_create.append(TaxonomyItem(
                            taxonomy=taxonomy,
                            name=item_name,
                            weight=idx
                        ))
                        existing_names.add(item_name)  # 更新内存缓存
                
                if items_to_create:
                    TaxonomyItem.objects.bulk_create(items_to_create, batch_size=500)
        
        return count
    
    @staticmethod
    def generate_items_ai(taxonomy_id: int, count: int = 10) -> List[str]:
        """AI 生成词汇项（预留接口）"""
        return []
