from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sma.system'

    def ready(self):
        # 在应用启动时导入 signals 以注册信号处理器
        import sma.system.signals
        from .views.mco_tasks import worker_thread