from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        logger.info("CoreConfig.ready() 被调用")
        # Cron 服务不再在此处初始化，改为在 run.py 或 wsgi.py 中启动服务器时初始化
