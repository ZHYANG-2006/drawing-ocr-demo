# mypdf/tasks.py
from celery import shared_task
from django.utils import timezone
from sma.system.models.mco import ProcessedFile

@shared_task(name='mypdf.tasks.scan_new_pdfs')
def scan_new_pdfs(directory_path):
    import os
    # 读取所有 PDF 文件
    try:
        files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    except Exception as e:
        # 记录或告警
        return

    # 已处理文件集合
    processed = set(ProcessedFile.objects.values_list('file_name', flat=True))
    for fname in files:
        if fname in processed:
            continue
        fullpath = os.path.join(directory_path, fname)
        # 调用已有的解析逻辑
        from sma.system.views import mco_cmp_tasks  # 或者直接导入 create()
        mco_cmp_tasks.create_file(fullpath)  # 假设你把 create() 封装成文件路径版本

        # 标记已处理
        ProcessedFile.objects.create(file_name=fname)

    # 更新 last_run
    from sma.system.models.mco import MonitorConfig
    cfg = MonitorConfig.objects.filter(directory_path=directory_path).first()
    if cfg:
        cfg.last_run = timezone.now()
        cfg.save()
