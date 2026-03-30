# -*- coding: utf-8 -*-
"""
居民信息服务
"""

from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ResidentInfoFields
from core.node.services import NodeService

User = get_user_model()


class ResidentInfoService:
    """居民信息管理服务"""
    
    @staticmethod
    def get_list(search: Optional[str] = None, resident_type_id: Optional[int] = None,
                grid_id: Optional[int] = None, user=None) -> List[ResidentInfoFields]:
        """获取居民列表"""
        queryset = ResidentInfoFields.objects.select_related(
            'node', 'relation', 'gender', 'grid', 'resident_type', 
            'key_category', 'nation', 'political_status', 
            'marital_status', 'education', 'health_status'
        )
        
        if user and not user.is_admin:
            queryset = queryset.filter(node__created_by=user)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(id_card__icontains=search) |
                Q(phone__icontains=search)
            )
        
        if resident_type_id:
            queryset = queryset.filter(resident_type_id=resident_type_id)
        
        if grid_id:
            queryset = queryset.filter(grid_id=grid_id)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(resident_id: int) -> Optional[ResidentInfoFields]:
        return ResidentInfoFields.objects.filter(id=resident_id).first()
    
    @staticmethod
    def get_by_node_id(node_id: int) -> Optional[ResidentInfoFields]:
        return ResidentInfoFields.objects.filter(node_id=node_id).first()
    
    @staticmethod
    def create(user, data: Dict[str, Any]) -> ResidentInfoFields:
        node = NodeService.create('resident_info', user, {})
        
        resident = ResidentInfoFields.objects.create(
            node=node,
            name=data.get('name', ''),
            relation_id=data.get('relation_id'),
            id_card=data.get('id_card'),
            gender_id=data.get('gender_id'),
            birth_date=data.get('birth_date'),
            phone=data.get('phone'),
            current_community=data.get('current_community'),
            current_door=data.get('current_door'),
            grid_id=data.get('grid_id'),
            resident_type_id=data.get('resident_type_id'),
            is_key_person=data.get('is_key_person', False),
            key_category_id=data.get('key_category_id'),
            registered_community=data.get('registered_community'),
            registered_address=data.get('registered_address'),
            registered_region=data.get('registered_region'),
            household_number=data.get('household_number'),
            is_separated=data.get('is_separated', False),
            actual_residence=data.get('actual_residence'),
            is_moved_out=data.get('is_moved_out', False),
            move_out_date=data.get('move_out_date'),
            move_to_place=data.get('move_to_place'),
            is_deceased=data.get('is_deceased', False),
            death_date=data.get('death_date'),
            nation_id=data.get('nation_id'),
            political_status_id=data.get('political_status_id'),
            marital_status_id=data.get('marital_status_id'),
            education_id=data.get('education_id'),
            work_status=data.get('work_status'),
            health_status_id=data.get('health_status_id'),
            notes=data.get('notes'),
        )
        
        return resident
    
    @staticmethod
    def update(resident_id: int, user, data: Dict[str, Any]) -> Optional[ResidentInfoFields]:
        resident = ResidentInfoFields.objects.filter(id=resident_id).first()
        if not resident:
            return None
        
        NodeService.update(resident.node_id, user, {})
        
        update_fields = [
            'name', 'relation_id', 'id_card', 'gender_id', 'birth_date', 'phone',
            'current_community', 'current_door', 'grid_id',
            'resident_type_id', 'is_key_person', 'key_category_id',
            'registered_community', 'registered_address', 'registered_region', 'household_number',
            'is_separated', 'actual_residence',
            'is_moved_out', 'move_out_date', 'move_to_place',
            'is_deceased', 'death_date',
            'nation_id', 'political_status_id', 'marital_status_id', 'education_id', 
            'work_status', 'health_status_id', 'notes'
        ]
        
        for field in update_fields:
            if field in data:
                setattr(resident, field, data[field])
        
        resident.save()
        return resident
    
    @staticmethod
    def delete(resident_id: int) -> bool:
        resident = ResidentInfoFields.objects.filter(id=resident_id).first()
        if resident:
            node = resident.node
            resident.delete()
            if node:
                node.delete()
            return True
        return False
    
    @staticmethod
    def get_count() -> int:
        return ResidentInfoFields.objects.count()
    
    @staticmethod
    def get_recent_count(days: int = 7) -> int:
        from django.utils import timezone
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        return ResidentInfoFields.objects.filter(created_at__gte=start_date).count()