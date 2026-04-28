# -*- coding: utf-8 -*-
"""
时钟模块服务层
"""

from datetime import datetime
import time


class ClockService:

    WEEKDAYS_CN = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    WEEKDAYS_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    MONTHS_CN = ['', '一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    MONTHS_EN = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    @staticmethod
    def get_current_time():
        now = datetime.now()
        return {
            'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': int(time.time()),
            'date': now.strftime('%Y年%m月%d日'),
            'time': now.strftime('%H:%M:%S'),
            'weekday': ClockService.WEEKDAYS_CN[now.weekday()],
            'weekday_en': ClockService.WEEKDAYS_EN[now.weekday()],
            'month': ClockService.MONTHS_CN[now.month],
            'month_en': ClockService.MONTHS_EN[now.month],
        }
