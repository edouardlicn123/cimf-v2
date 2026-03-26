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


DEFAULT_TAXONOMIES = [
    # ========== 旧版移植词汇表 (18个) ==========
    {
        "name": "性别",
        "slug": "gender",
        "description": "性别分类",
        "items": ["男", "女", "其他"]
    },
    {
        "name": "客户类型",
        "slug": "customer_type",
        "description": "客户类型分类",
        "items": ["潜在客户", "正式客户", "VIP客户", "上市公司", "非上市企业"]
    },
    {
        "name": "国家/地区",
        "slug": "country",
        "description": "世界各国和地区",
        "items": [
            "阿富汗", "阿尔巴尼亚", "阿尔及利亚", "阿拉伯联合酋长国", "阿根廷", "亚美尼亚", "澳大利亚",
            "奥地利", "阿塞拜疆", "巴哈马", "巴林", "孟加拉国", "巴巴多斯", "白俄罗斯", "比利时", "伯利兹",
            "贝宁", "不丹", "玻利维亚", "波斯尼亚和黑塞哥维那", "博茨瓦纳", "巴西", "文莱", "保加利亚",
            "布基纳法索", "布隆迪", "喀麦隆", "加拿大", "佛得角", "中非共和国", "乍得", "智利", "中国",
            "哥伦比亚", "科摩罗", "刚果共和国", "刚果民主共和国", "哥斯达黎加", "科特迪瓦", "克罗地亚",
            "古巴", "塞浦路斯", "捷克", "丹麦", "多米尼加共和国", "厄瓜多尔", "埃及", "萨尔瓦多",
            "赤道几内亚", "厄立特里亚", "爱沙尼亚", "斯威士兰", "埃塞俄比亚", "斐济", "芬兰", "法国",
            "加蓬", "冈比亚", "格鲁吉亚", "德国", "加纳", "希腊", "格林纳达", "危地马拉", "几内亚",
            "几内亚比绍", "圭亚那", "海地", "梵蒂冈", "洪都拉斯", "匈牙利", "冰岛", "印度", "印度尼西亚",
            "伊朗", "伊拉克", "爱尔兰", "以色列", "意大利", "牙买加", "日本", "约旦", "哈萨克斯坦",
            "肯尼亚", "基里巴斯", "朝鲜", "韩国", "科威特", "吉尔吉斯斯坦", "老挝", "拉脱维亚", "黎巴嫩",
            "莱索托", "利比里亚", "利比亚", "列支敦士登", "立陶宛", "卢森堡", "马达加斯加", "马拉维",
            "马来西亚", "马尔代夫", "马里", "马耳他", "毛里塔尼亚", "毛里求斯", "墨西哥", "密克罗尼西亚",
            "摩尔多瓦", "摩纳哥", "蒙古", "黑山", "摩洛哥", "莫桑比克", "缅甸", "纳米比亚", "瑙鲁",
            "尼泊尔", "荷兰", "新西兰", "尼加拉瓜", "尼日尔", "尼日利亚", "北马其顿", "挪威", "阿曼",
            "巴基斯坦", "帕劳", "巴拿马", "巴布亚新几内亚", "巴拉圭", "秘鲁", "菲律宾", "波兰", "葡萄牙",
            "卡塔尔", "罗马尼亚", "俄罗斯", "卢旺达", "圣基茨和尼维斯", "圣卢西亚", "圣文森特和格林纳丁斯",
            "萨摩亚", "圣马力诺", "沙特阿拉伯", "塞内加尔", "塞尔维亚", "塞舌尔", "塞拉利昂", "新加坡",
            "斯洛伐克", "斯洛文尼亚", "索马里", "南非", "南苏丹", "西班牙", "斯里兰卡", "苏丹", "苏里南",
            "瑞典", "瑞士", "叙利亚", "台湾省", "塔吉克斯坦", "坦桑尼亚", "泰国", "多哥", "汤加",
            "特立尼达和多巴哥", "突尼斯", "土耳其", "土库曼斯坦", "图瓦卢", "乌干达", "乌克兰", "英国",
            "美国", "乌拉圭", "乌兹别克斯坦", "瓦努阿图", "梵蒂冈", "委内瑞拉", "越南", "也门", "赞比亚", "津巴布韦"
        ]
    },
    {
        "name": "项目状态",
        "slug": "project_status",
        "description": "项目状态分类",
        "items": ["进行中", "已完成", "已暂停", "已取消"]
    },
    {
        "name": "项目阶段",
        "slug": "project_phase",
        "description": "项目阶段分类",
        "items": ["需求调研", "方案设计", "开发中", "测试阶段", "验收阶段", "交付完成"]
    },
    {
        "name": "优先级",
        "slug": "priority",
        "description": "优先级分类",
        "items": ["高", "中", "低"]
    },
    {
        "name": "部门",
        "slug": "department",
        "description": "部门分类",
        "items": ["销售部", "技术部", "财务部", "行政部"]
    },
    {
        "name": "合同状态",
        "slug": "contract_status",
        "description": "合同状态分类",
        "items": ["草稿", "审批中", "已签署", "已到期"]
    },
    {
        "name": "付款状态",
        "slug": "payment_status",
        "description": "付款状态分类",
        "items": ["未付款", "部分付款", "已付清"]
    },
    {
        "name": "客户跟进状态",
        "slug": "followup_status",
        "description": "客户跟进状态分类",
        "items": ["待联系", "已联系", "沟通中", "意向明确", "已报价", "已签约", "已流失"]
    },
    {
        "name": "任务状态",
        "slug": "task_status",
        "description": "任务状态分类",
        "items": ["待开始", "进行中", "待审核", "已完成", "已延期", "已取消"]
    },
    {
        "name": "风险等级",
        "slug": "risk_level",
        "description": "风险等级分类",
        "items": ["低风险", "中风险", "高风险", "严重"]
    },
    {
        "name": "企业规模",
        "slug": "company_size",
        "description": "企业规模分类",
        "items": ["小型(1-50人)", "中型(51-500人)", "大型(501-2000人)", "超大型(2000人+)"]
    },
    {
        "name": "户籍类型",
        "slug": "household_type",
        "description": "户籍类型分类",
        "items": ["本地户籍", "常住人口", "流动人口", "暂住证"]
    },
    {
        "name": "居住状况",
        "slug": "residence_status",
        "description": "居住状况分类",
        "items": ["自有住房", "租房", "借住", "集体宿舍"]
    },
    {
        "name": "社保状态",
        "slug": "insurance_status",
        "description": "社保状态分类",
        "items": ["已缴纳", "缴纳中", "断缴", "未缴纳"]
    },
    {
        "name": "婚姻状况",
        "slug": "marital_status",
        "description": "婚姻状况分类",
        "items": ["未婚", "已婚", "离异", "丧偶"]
    },
    {
        "name": "文化程度",
        "slug": "education_level",
        "description": "文化程度分类",
        "items": ["小学", "初中", "高中/中专", "大专", "本科", "硕士", "博士"]
    },
    # ========== 新增业务词汇表 (9个) ==========
    {
        "name": "开发技术",
        "slug": "tech_stack",
        "description": "开发技术分类",
        "items": ["Java", "Python", "PHP", "Node.js", "Vue", "React", "MySQL", "PostgreSQL"]
    },
    {
        "name": "项目结束原因",
        "slug": "end_reason",
        "description": "项目结束原因分类",
        "items": ["顺利完成", "客户终止", "预算不足", "不可抗力"]
    },
    {
        "name": "客户等级",
        "slug": "customer_level",
        "description": "客户等级分类",
        "items": ["A级(重点)", "B级(普通)", "C级(潜在)"]
    },
    {
        "name": "建筑类型",
        "slug": "building_type",
        "description": "建筑类型分类",
        "items": ["住宅小区", "商住混合", "商业建筑", "公共建筑", "政府建筑", "私人住宅"]
    },
    {
        "name": "省份",
        "slug": "province",
        "description": "中国省级行政区",
        "items": ["北京市", "天津市", "上海市", "重庆市", "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省", "河南省", "湖北省", "湖南省", "广东省", "海南省", "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省", "台湾省", "内蒙古自治区", "广西壮族自治区", "西藏自治区", "宁夏回族自治区", "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区"]
    },
    {
        "name": "会员等级",
        "slug": "member_level",
        "description": "会员等级分类",
        "items": ["普通会员", "银卡", "金卡", "钻石卡"]
    },
    {
        "name": "会员状态",
        "slug": "member_status",
        "description": "会员状态分类",
        "items": ["正常", "冻结", "已过期"]
    },
    {
        "name": "积分来源",
        "slug": "points_source",
        "description": "积分来源分类",
        "items": ["消费", "注册", "签到", "推荐"]
    },
    {
        "name": "优惠券类型",
        "slug": "coupon_type",
        "description": "优惠券类型分类",
        "items": ["满减券", "折扣券", "礼品券", "代金券"]
    },
    # ========== 新增经济普查词汇表 (10个) ==========
    {
        "name": "经济类型",
        "slug": "economic_type",
        "description": "经济类型分类",
        "items": ["国有企业", "集体企业", "民营企业", "外资企业", "合资企业", "个体经营"]
    },
    {
        "name": "登记注册类型",
        "slug": "registration_type",
        "description": "登记注册类型分类",
        "items": ["企业", "事业单位", "机关", "社会团体", "民办非企业单位", "基金会", "居委会", "村委会"]
    },
    {
        "name": "企业控股情况",
        "slug": "ownership_type",
        "description": "企业控股情况分类",
        "items": ["国有控股", "集体控股", "私人控股", "港澳台商控股", "外商控股"]
    },
    {
        "name": "企业性质",
        "slug": "enterprise_type",
        "description": "国内企业性质分类",
        "items": ["国有企业", "民营企业", "集体企业", "混合所有制企业", "股份制企业", "上市公司", "外资企业", "合资企业", "港澳台资企业"]
    },
    {
        "name": "企业性质(海外)",
        "slug": "enterprise_nature",
        "description": "海外企业性质分类",
        "items": ["股份公司", "有限责任公司", "合伙企业", "个人独资企业", "合资企业", "子公司", "分公司", "代表处", "非营利组织", "信托"]
    },
    {
        "name": "经营状态",
        "slug": "business_status",
        "description": "经营状态分类",
        "items": ["正常营业", "停业(歇业)", "筹建", "当年关闭", "当年破产"]
    },
    {
        "name": "从业人员规模",
        "slug": "employee_scale",
        "description": "从业人员规模分类",
        "items": ["1-4人", "5-9人", "10-19人", "20-49人", "50-99人", "100-299人", "300-499人", "500-999人", "1000人及以上"]
    },
    {
        "name": "行业门类",
        "slug": "industry",
        "description": "行业门类分类",
        "items": ["农林牧渔业", "采矿业", "制造业", "电力燃气水生产供应业", "建筑业", "批发零售业", "交通运输仓储邮政业", "住宿餐饮业", "金融业", "房地产业", "租赁商务服务业", "科研技术服务业", "水利环境公共设施管理业", "居民服务修理其他服务业", "教育", "卫生社会工作", "文化体育娱乐业", "公共管理社会组织"]
    },
    {
        "name": "执行会计制度",
        "slug": "accounting_system",
        "description": "执行会计制度分类",
        "items": ["企业会计制度", "事业单位会计制度", "行政单位会计制度", "民间非营利组织会计制度"]
    },
    {
        "name": "盈利状态",
        "slug": "profit_status",
        "description": "盈利状态分类",
        "items": ["盈利", "亏损", "持平"]
    },
    {
        "name": "是否高新企业",
        "slug": "high_tech",
        "description": "是否高新企业分类",
        "items": ["是", "否"]
    },
    {
        "name": "是否有自营进出口权",
        "slug": "import_export",
        "description": "自营进出口权分类",
        "items": ["有", "无"]
    },
]


class TaxonomyService:
    """
    词汇表服务层
    提供词汇表和词汇项的 CRUD 操作
    """
    
    @staticmethod
    def get_all_taxonomies():
        """获取所有词汇表"""
        from core.models import Taxonomy
        return Taxonomy.objects.all().order_by('id')
    
    @staticmethod
    def get_taxonomy_by_id(taxonomy_id: int):
        """获取词汇表详情"""
        from core.models import Taxonomy
        return Taxonomy.objects.filter(id=taxonomy_id).first()
    
    @staticmethod
    def get_taxonomy_by_slug(slug: str):
        """通过 slug 获取词汇表"""
        from core.models import Taxonomy
        return Taxonomy.objects.filter(slug=slug).first()
    
    @staticmethod
    def create_taxonomy(name: str, slug: str, description: str = '') -> models.Model:
        """创建词汇表"""
        from core.models import Taxonomy
        taxonomy = Taxonomy.objects.create(
            name=name,
            slug=slug,
            description=description
        )
        return taxonomy
    
    @staticmethod
    def update_taxonomy(taxonomy_id: int, name: str = None, slug: str = None, description: str = None) -> models.Model:
        """更新词汇表"""
        from core.models import Taxonomy
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
        from core.models import Taxonomy
        taxonomy = Taxonomy.objects.filter(id=taxonomy_id).first()
        if taxonomy:
            taxonomy.delete()
            return True
        return False
    
    @staticmethod
    def get_items(taxonomy_id: int) -> List[models.Model]:
        """获取词汇表的所有词汇项"""
        from core.models import TaxonomyItem
        return TaxonomyItem.objects.filter(taxonomy_id=taxonomy_id).order_by('weight', 'name')
    
    @staticmethod
    def create_item(taxonomy_id: int, name: str, description: str = '', weight: int = None) -> models.Model:
        """创建词汇项"""
        from core.models import TaxonomyItem
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
        from core.models import TaxonomyItem
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
        from core.models import TaxonomyItem
        item = TaxonomyItem.objects.filter(id=item_id).first()
        if item:
            item.delete()
            return True
        return False
    
    @staticmethod
    def reorder_items(taxonomy_id: int, item_ids: List[int]) -> bool:
        """重新排序词汇项"""
        from core.models import TaxonomyItem
        for idx, item_id in enumerate(item_ids):
            TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).update(weight=idx)
        return True
    
    @staticmethod
    def init_default_taxonomies() -> int:
        """初始化预置分类数据，返回创建的词汇表数量"""
        from core.models import Taxonomy, TaxonomyItem
        
        created_count = 0
        
        for tax_data in DEFAULT_TAXONOMIES:
            existing = Taxonomy.objects.filter(slug=tax_data['slug']).first()
            if existing:
                continue
            
            taxonomy = Taxonomy.objects.create(
                name=tax_data['name'],
                slug=tax_data['slug'],
                description=tax_data.get('description', '')
            )
            
            for idx, item_name in enumerate(tax_data['items']):
                TaxonomyItem.objects.create(
                    taxonomy=taxonomy,
                    name=item_name,
                    weight=idx
                )
            
            created_count += 1
        
        return created_count
    
    @staticmethod
    def generate_items_ai(taxonomy_id: int, count: int = 10) -> List[str]:
        """AI 生成词汇项（预留接口）"""
        return []
