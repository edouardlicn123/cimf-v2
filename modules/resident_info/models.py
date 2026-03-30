# -*- coding: utf-8 -*-
"""
居民信息模型
"""

from django.db import models
from core.node.models import Node


class ResidentInfoFields(models.Model):
    """居民信息字段表"""
    
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='resident_info_fields',
        verbose_name='关联节点'
    )
    
    name = models.CharField(max_length=100, verbose_name='姓名')
    relation = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resident_relation_residents',
        verbose_name='与其他人员关系'
    )
    id_card = models.CharField(max_length=18, verbose_name='身份证号')
    gender = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gender_residents',
        verbose_name='性别'
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    phone = models.CharField(max_length=100, blank=True, verbose_name='联系电话')
    
    current_community = models.CharField(max_length=200, blank=True, verbose_name='现住小区/建筑')
    current_door = models.CharField(max_length=100, blank=True, verbose_name='门牌地址')
    grid = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grid_residents',
        verbose_name='所属网格'
    )
    
    resident_type = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resident_type_residents',
        verbose_name='人员类型'
    )
    is_key_person = models.BooleanField(default=False, verbose_name='是否重点人员')
    key_category = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='key_category_residents',
        verbose_name='重点类别'
    )
    
    registered_community = models.CharField(max_length=200, blank=True, verbose_name='户籍小区/建筑')
    registered_address = models.CharField(max_length=200, blank=True, verbose_name='户籍地址')
    registered_region = models.JSONField(blank=True, null=True, verbose_name='户籍地址省市区')
    household_number = models.CharField(max_length=50, blank=True, verbose_name='户编号')
    
    is_separated = models.BooleanField(default=False, verbose_name='是否人户分离')
    actual_residence = models.CharField(max_length=200, blank=True, verbose_name='实际居住地')
    
    is_moved_out = models.BooleanField(default=False, verbose_name='是否已迁出')
    move_out_date = models.DateField(null=True, blank=True, verbose_name='迁出日期')
    move_to_place = models.CharField(max_length=200, blank=True, verbose_name='迁往地')
    
    is_deceased = models.BooleanField(default=False, verbose_name='是否已死亡')
    death_date = models.DateField(null=True, blank=True, verbose_name='死亡日期')
    
    nation = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nation_residents',
        verbose_name='民族'
    )
    political_status = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='political_status_residents',
        verbose_name='政治面貌'
    )
    marital_status = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marital_status_residents',
        verbose_name='婚姻状况'
    )
    education = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='education_residents',
        verbose_name='文化程度'
    )
    work_status = models.CharField(max_length=50, blank=True, verbose_name='工作学习情况')
    health_status = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='health_status_residents',
        verbose_name='健康状况'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'resident_info_fields'
        verbose_name = '居民'
        verbose_name_plural = '居民'
    
    @property
    def creator(self):
        return self.node.created_by if hasattr(self, 'node') and self.node else None
    
    def __str__(self):
        return self.name