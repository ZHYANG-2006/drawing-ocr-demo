from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from sma.system.models.mco import MonitorConfig
import json

TASK_NAME = 'mypdf.tasks.scan_new_pdfs'

@receiver(post_save, sender=MonitorConfig)
def sync_monitor_to_beat(sender, instance: MonitorConfig, **kwargs):
    # 1. 构造或获取 CrontabSchedule
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=instance.cron_minute,
        hour=instance.cron_hour,
        day_of_week='*', day_of_month='*', month_of_year='*'
    )
    # 2. 创建或更新 PeriodicTask
    pt, created = PeriodicTask.objects.update_or_create(
        name=f"ScanPDFs::{instance.pk}",
        defaults={
            'task': TASK_NAME,
            'crontab': schedule,
            'args': json.dumps([instance.directory_path]),
            'enabled': instance.enabled,
        }
    )

@receiver(post_delete, sender=MonitorConfig)
def delete_monitor_beat(sender, instance: MonitorConfig, **kwargs):
    PeriodicTask.objects.filter(name=f"ScanPDFs::{instance.pk}").delete()
