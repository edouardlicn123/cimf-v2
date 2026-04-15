# -*- coding: utf-8 -*-
"""
ExportService - 导出服务

提供通用的数据导出功能，支持 CSV/Excel 格式
"""

from typing import List, Dict, Any
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime


class ExportService:
    """数据导出服务"""
    
    FORMAT_CSV = 'csv'
    FORMAT_XLSX = 'xlsx'
    
    EXPORTABLE_FIELD_TYPES = [
        'string', 'string_long', 'text', 'email', 'telephone',
        'integer', 'decimal', 'float', 'boolean',
        'entity_reference', 'datetime', 'date',
    ]
    
    FK_TYPES = ['fk', 'taxonomy', 'region']
    
    FILTERABLE_TYPES = ['string', 'string_long', 'text', 'email', 'telephone', 'fk']
    
    FILTERABLE_FK_FIELDS = ['country', 'industry', 'enterprise_nature', 'enterprise_type']
    
    @classmethod
    def get_exportable_fields(cls, node_type_slug: str) -> List[Dict]:
        """动态获取可导出的字段列表"""
        from importlib import import_module
        
        try:
            mod = import_module(f'modules.{node_type_slug}.module')
            if hasattr(mod, 'MODULE_INFO'):
                return mod.MODULE_INFO.get('export_fields', [])
        except (ImportError, ModuleNotFoundError):
            pass
        
        return []
    
    @classmethod
    def get_fields_info(cls, node_type_slug: str, field_names: List[str]) -> List[Dict]:
        """获取选中字段的详细信息"""
        all_fields = cls.get_exportable_fields(node_type_slug)
        return [f for f in all_fields if f['name'] in field_names]
    
    @classmethod
    def get_filterable_fields(cls, node_type_slug: str) -> List[Dict]:
        """获取可筛选的字段列表"""
        all_fields = cls.get_exportable_fields(node_type_slug)
        return [f for f in all_fields if f['type'] in cls.FILTERABLE_TYPES]
    
    @classmethod
    def has_region_field(cls, node_type_slug: str) -> bool:
        """检查节点类型是否有省市区字段"""
        all_fields = cls.get_exportable_fields(node_type_slug)
        return any(f['name'] == 'region' for f in all_fields)
    
    @classmethod
    def get_preview(cls, node_type_slug: str, field_names: List[str], 
                    filters: List[Dict] = None, limit: int = 5) -> List[Dict]:
        """获取数据预览"""
        queryset = cls._get_filtered_queryset(node_type_slug, filters)
        fields = cls.get_fields_info(node_type_slug, field_names)
        
        preview_data = []
        for item in queryset[:limit]:
            row = cls._convert_to_row(item, field_names, node_type_slug)
            preview_data.append(row)
        
        return preview_data
    
    @classmethod
    def get_record_count(cls, node_type_slug: str, filters: List[Dict] = None) -> int:
        """获取记录总数"""
        queryset = cls._get_filtered_queryset(node_type_slug, filters)
        return queryset.count()
    
    @classmethod
    def export(cls, node_type_slug: str, field_names: List[str], 
               export_format: str = 'csv', filters: List[Dict] = None) -> HttpResponse:
        """执行导出"""
        queryset = cls._get_filtered_queryset(node_type_slug, filters)
        fields = cls.get_fields_info(node_type_slug, field_names)
        
        rows = []
        for item in queryset:
            rows.append(cls._convert_to_row(item, field_names, node_type_slug))
        
        filename = cls.generate_filename(node_type_slug, export_format)
        
        if export_format == cls.FORMAT_CSV:
            return cls._export_csv(rows, fields, filename)
        else:
            return cls._export_xlsx(rows, fields, filename)
    
    @classmethod
    def generate_filename(cls, node_type_slug: str, export_format: str) -> str:
        """生成导出文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{node_type_slug}_{timestamp}.{export_format}'
    
    @classmethod
    def _export_csv(cls, rows: List[Dict], fields: List[Dict], filename: str) -> HttpResponse:
        """导出为 CSV"""
        import csv
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow([f['label'] for f in fields])
        
        for row in rows:
            writer.writerow([row.get(f['name'], '') for f in fields])
        
        return response
    
    @classmethod
    def _export_xlsx(cls, rows: List[Dict], fields: List[Dict], filename: str) -> HttpResponse:
        """导出为 XLSX"""
        from openpyxl import Workbook
        from openpyxl.utils import get_column_letter
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Data"
        
        header_font = Font(bold=True)
        header_fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        headers = [f['label'] for f in fields]
        ws.append(headers)
        
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
        
        for row in rows:
            ws.append([row.get(f['name'], '') for f in fields])
        
        for i, col in enumerate(ws.columns, 1):
            max_length = 0
            column = get_column_letter(i)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        wb.save(response)
        return response
    
    @classmethod
    def _convert_to_row(cls, item, field_names: List[str], 
                        node_type_slug: str = None) -> Dict:
        """将数据对象转换为导出行"""
        fields = cls.get_exportable_fields(node_type_slug) if node_type_slug else []
        field_type_map = {f['name']: f['type'] for f in fields}
        
        row = {}
        for field_name in field_names:
            field_type = field_type_map.get(field_name, 'string')
            value = cls._get_field_value(item, field_name, field_type)
            row[field_name] = value
        return row
    
    @classmethod
    def _get_field_value(cls, item, field_name: str, field_type: str = 'string') -> Any:
        """获取字段值"""
        if field_type in ['fk', 'taxonomy']:
            return cls._resolve_fk_field(item, field_name)
        
        if field_type == 'region':
            return cls._resolve_region_field(item)
        
        if field_type == 'boolean':
            value = getattr(item, field_name, False)
            return '是' if value else '否'
        
        return getattr(item, field_name, '') or ''
    
    @classmethod
    def _resolve_fk_field(cls, item, field_name: str) -> str:
        """解析 FK 字段，返回名称"""
        obj = getattr(item, field_name, None)
        return obj.name if obj and hasattr(obj, 'name') else ''
    
    @classmethod
    def _resolve_region_field(cls, item) -> str:
        """解析省市区 JSON 字段"""
        region = getattr(item, 'region', None) or {}
        province = region.get('province', '')
        city = region.get('city', '')
        district = region.get('district', '')
        parts = [p for p in [province, city, district] if p]
        return ' '.join(parts) if parts else ''
    
    @classmethod
    def _get_service_class(cls, node_type_slug: str):
        """动态获取服务类"""
        try:
            from importlib import import_module
            mod = import_module(f'modules.{node_type_slug}.services')
            
            # 优先查找与 node_type_slug 同名的 Service
            service_name = f'{node_type_slug.title().replace("_", "")}Service'
            if hasattr(mod, service_name):
                attr = getattr(mod, service_name)
                if hasattr(attr, 'get_list'):
                    return attr
            
            # 否则遍历查找第一个 Service
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (attr_name.endswith('Service') and 
                    hasattr(attr, 'get_list')):
                    return attr
        except (ImportError, ModuleNotFoundError):
            pass
        
        return None
    
    @classmethod
    def _get_filtered_queryset(cls, node_type_slug: str, filters: List[Dict] = None):
        """获取应用筛选条件后的 QuerySet"""
        service = cls._get_service_class(node_type_slug)
        if not service:
            raise ValueError(f"Unknown node type: {node_type_slug}")
        
        queryset = service.get_list()
        
        if not filters:
            return queryset
        
        import json
        for f in filters:
            field = f.get('field', '')
            value = f.get('value', '')
            
            if not field or not value:
                continue
            
            if field == 'region':
                try:
                    region_data = json.loads(value) if isinstance(value, str) else value
                except (json.JSONDecodeError, TypeError):
                    region_data = {}
                province = region_data.get('province', '')
                city = region_data.get('city', '')
                district = region_data.get('district', '')
                q = Q()
                if province:
                    q &= Q(**{f'region__province__icontains': province})
                if city:
                    q &= Q(**{f'region__city__icontains': city})
                if district:
                    q &= Q(**{f'region__district__icontains': district})
                queryset = queryset.filter(q)
            elif field in cls.FILTERABLE_FK_FIELDS:
                queryset = queryset.filter(**{f'{field}__name__icontains': value})
            elif field in cls.FILTERABLE_FIELD_TYPES:
                queryset = queryset.filter(**{f'{field}__icontains': value})
        
        return queryset