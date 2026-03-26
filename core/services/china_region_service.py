# -*- coding: utf-8 -*-
"""
================================================================================
文件：china_region_service.py
路径：/home/edo/cimf-v2/core/services/china_region_service.py
================================================================================

功能说明：
    中国行政区划服务，提供省-市-县三级行政区划的数据管理和查询功能
    
    主要功能：
    - 从网络获取并导入行政区划数据
    - 查询省、市、县层级数据
    - 搜索行政区划
    - 获取完整路径

用法：
    1. 导入数据：
        result = ChinaRegionService.import_from_url()
    
    2. 获取省份列表：
        provinces = ChinaRegionService.get_provinces()
    
    3. 获取城市：
        cities = ChinaRegionService.get_cities('440000')
    
    4. 获取区县：
        districts = ChinaRegionService.get_districts('440100')
    
    5. 搜索：
        results = ChinaRegionService.search('深圳')
    
    6. 获取完整路径：
        path = ChinaRegionService.get_full_path('440305')

版本：
    - 1.0: 初始版本

依赖：
    - core.models.ChinaRegion: 行政区划模型
"""

from typing import List, Optional, Dict
import requests
from core.models import ChinaRegion


class ChinaRegionService:
    """中国行政区划服务"""
    
    DATA_SOURCE_URL = 'https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/pca-code.json'
    
    # ===== 数据导入 =====
    
    @staticmethod
    def import_from_url(url: str = None) -> Dict:
        """从网络获取并导入数据"""
        url = url or ChinaRegionService.DATA_SOURCE_URL
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            print(f"Fetched {len(data)} provinces from API")
            return ChinaRegionService._import_data(data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _import_data(data: List[Dict]) -> Dict:
        """解析并导入数据 - 使用 bulk_create 优化性能"""
        from django.db import transaction
        
        regions_to_create = []
        code_to_region = {}
        
        province_count = 0
        city_count = 0
        district_count = 0
        
        with transaction.atomic():
            ChinaRegion.objects.all().delete()
            
            for province_data in data:
                province_count += 1
                province = ChinaRegion(
                    code=province_data['code'],
                    name=province_data['name'],
                    level=1,
                    parent=None
                )
                regions_to_create.append(province)
                code_to_region[province.code] = province
            
            ChinaRegion.objects.bulk_create(regions_to_create)
            
            regions_to_create = []
            
            for province_data in data:
                province = code_to_region[province_data['code']]
                for city_data in province_data.get('children', []):
                    city_count += 1
                    city = ChinaRegion(
                        code=city_data['code'],
                        name=city_data['name'],
                        level=2,
                        parent=province
                    )
                    regions_to_create.append(city)
                    code_to_region[city.code] = city
            
            ChinaRegion.objects.bulk_create(regions_to_create)
            
            regions_to_create = []
            
            for province_data in data:
                for city_data in province_data.get('children', []):
                    city = code_to_region[city_data['code']]
                    for district_data in city_data.get('children', []):
                        district_count += 1
                        district = ChinaRegion(
                            code=district_data['code'],
                            name=district_data['name'],
                            level=3,
                            parent=city
                        )
                        regions_to_create.append(district)
            
            ChinaRegion.objects.bulk_create(regions_to_create)
        
        total = province_count + city_count + district_count
        print(f"Import summary: {province_count} provinces, {city_count} cities, {district_count} districts")
        return {'success': True, 'count': total, 'provinces': province_count, 'cities': city_count, 'districts': district_count}
    
    # ===== 查询方法 =====
    
    @staticmethod
    def get_provinces() -> List[ChinaRegion]:
        """获取所有省份"""
        return list(ChinaRegion.objects.filter(level=1).order_by('code'))
    
    @staticmethod
    def get_cities(province_code: str) -> List[ChinaRegion]:
        """获取省份下的所有城市"""
        province = ChinaRegion.objects.filter(code=province_code, level=1).first()
        if not province:
            return []
        return list(province.children.filter(level=2).order_by('code'))
    
    @staticmethod
    def get_districts(city_code: str) -> List[ChinaRegion]:
        """获取城市下的所有区县"""
        city = ChinaRegion.objects.filter(code=city_code, level=2).first()
        if not city:
            return []
        return list(city.children.filter(level=3).order_by('code'))
    
    @staticmethod
    def get_by_code(code: str) -> Optional[ChinaRegion]:
        """根据代码获取行政区划"""
        return ChinaRegion.objects.filter(code=code).first()
    
    @staticmethod
    def search(keyword: str, limit: int = 20) -> List[ChinaRegion]:
        """搜索行政区划"""
        return list(ChinaRegion.objects.filter(
            name__icontains=keyword
        ).order_by('level', 'code')[:limit])
    
    @staticmethod
    def get_full_path(region_code: str) -> str:
        """获取完整路径（如：广东省-深圳市-南山区）"""
        region = ChinaRegion.objects.filter(code=region_code).first()
        if not region:
            return ''
        
        return region.full_path
    
    @staticmethod
    def get_tree() -> List[Dict]:
        """获取完整的树形结构"""
        provinces = ChinaRegion.objects.filter(level=1).order_by('code')
        
        result = []
        for province in provinces:
            province_data = {
                'code': province.code,
                'name': province.name,
                'level': 1,
                'children': []
            }
            
            for city in province.children.filter(level=2).order_by('code'):
                city_data = {
                    'code': city.code,
                    'name': city.name,
                    'level': 2,
                    'children': [
                        {'code': d.code, 'name': d.name, 'level': 3}
                        for d in city.children.filter(level=3).order_by('code')
                    ]
                }
                province_data['children'].append(city_data)
            
            result.append(province_data)
        
        return result
    
    @staticmethod
    def get_stats() -> Dict:
        """获取统计信息"""
        return {
            'total': ChinaRegion.objects.count(),
            'provinces': ChinaRegion.objects.filter(level=1).count(),
            'cities': ChinaRegion.objects.filter(level=2).count(),
            'districts': ChinaRegion.objects.filter(level=3).count(),
        }
