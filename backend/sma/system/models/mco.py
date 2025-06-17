import hashlib
import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from sma.utils.models import CoreModel, table_prefix, get_custom_app_models, FileModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

class MCOPdfFile(FileModel):
    """
    PDF 文件模型
    """
    total_pages = models.IntegerField(null=True, verbose_name="总页数", help_text="PDF文件的总页数", blank=True)
    flow_name = models.CharField(null=True, max_length=255, verbose_name="流程名", help_text="流程名", blank=True)
    queue_order = models.IntegerField(default=-1, verbose_name='解析队列', help_text="用于确认当前文件在队列中的位置",
                                      blank=True)
    is_analyzed = models.BooleanField(default=0, verbose_name='是否已分析', help_text="用于确认文件是否已经过分析提取",
                                      blank=True)
    analyze_version = models.CharField(null=True, max_length=255, verbose_name="PDF提取接口版本号",
                                       help_text="PDF提取接口版本号", blank=True)
    has_expired = models.BooleanField(null=True, default=False, verbose_name='是否已过期', help_text="未使用最新接口进行提取",
                                      blank=True)
    expect_analyze_time = models.IntegerField(null=True, default=0, verbose_name="期望分析时长",
                                              help_text="期望分析时长", blank=True)
    start_analyze_time = models.DateTimeField(null=True, verbose_name="开始分析时间", help_text="开始分析时间",
                                              blank=True)
    finish_analyze_time = models.DateTimeField(null=True, verbose_name="结束分析时间", help_text="结束分析时间",
                                               blank=True)
    real_analyze_time = models.IntegerField(null=True, default=0, verbose_name="实际分析时长", help_text="实际分析时长",
                                            blank=True)
    progress = models.DecimalField(null=True, default=0, max_digits=5, decimal_places=2, verbose_name="分析进度百分比",
                                   help_text="分析进度百分比")
    section_cnt = models.IntegerField(null=True, verbose_name="章节数", help_text="章节数", blank=True)
    paragraph_cnt = models.IntegerField(null=True, verbose_name="段落数", help_text="段落数", blank=True)
    table_cnt = models.IntegerField(null=True, verbose_name="表格数", help_text="表格数", blank=True)
    picture_cnt = models.IntegerField(null=True, verbose_name="图片数", help_text="图片数", blank=True)
    title = models.CharField(max_length=255, verbose_name="title", help_text="title", null=True, blank=True)
    drawing_number = models.CharField(max_length=255, verbose_name="drawing_number", help_text="drawing_number", null=True, blank=True)
    internal_code = models.CharField(max_length=255, verbose_name="internal_code", help_text="internal_code", null=True, blank=True)
    project_description = models.CharField(max_length=255, verbose_name="project_description", help_text="project_description", null=True, blank=True)
    flex_part_number = models.CharField(max_length=255, verbose_name="flex_part_number", help_text="flex_part_number", null=True, blank=True)
    rev = models.CharField(max_length=255, verbose_name="rev", help_text="rev", null=True, blank=True)
    polygon = models.JSONField(verbose_name="段落多边形区域", blank=True, null=True)
    key_words = models.TextField(null=True, blank=True, verbose_name="关键词")

    # 统计字段
    total_count = models.IntegerField(null=True, default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(null=True, default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(null=True, default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(null=True, default=0, verbose_name="未通过的子项数量")
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    def update_progress(self, current_step, total_steps):
        """
        更新分析进度
        """
        self.progress = (current_step / total_steps) * 100
        self.save(update_fields=['progress'])

    class Meta:
        db_table = table_prefix + "MCO_PDF"  # 表名
        verbose_name = "PDF文件"
        verbose_name_plural = verbose_name

class MCOJsonFile(FileModel):
    """
    JSON 文件模型
    """
    source_file = models.ForeignKey(MCOPdfFile, related_name="jsonfiles", on_delete=models.CASCADE, null=True, blank=True)
    analyze_version = models.CharField(max_length=255, verbose_name="PDF提取接口版本号", help_text="PDF提取接口版本号", blank=True)
    owner_file = models.CharField(max_length=255, verbose_name="所属文件", help_text="所属文件", blank=True)
    section_cnt = models.IntegerField(null=True, verbose_name="章节数", help_text="章节数", blank=True)
    paragraph_cnt = models.IntegerField(null=True, verbose_name="段落数", help_text="段落数", blank=True)
    table_cnt = models.IntegerField(null=True, verbose_name="表格数", help_text="表格数", blank=True)
    image_cnt = models.IntegerField(null=True, verbose_name="图片数", help_text="图片数", blank=True)
    title = models.CharField(max_length=255, verbose_name="title", help_text="title", null=True, blank=True)
    drawing_number = models.CharField(max_length=255, verbose_name="drawing_number", help_text="drawing_number", null=True, blank=True)
    internal_code = models.CharField(max_length=255, verbose_name="internal_code", help_text="internal_code", null=True, blank=True)
    project_description = models.CharField(max_length=255, verbose_name="project_description", help_text="project_description", null=True, blank=True)
    flex_part_number = models.CharField(max_length=255, verbose_name="flex_part_number", help_text="flex_part_number", null=True, blank=True)
    rev = models.CharField(max_length=255, verbose_name="rev", help_text="rev", null=True, blank=True)
    key_words = models.TextField(null=True, blank=True, verbose_name="关键词")

    class Meta:
        db_table = table_prefix + "MCO_JSON"  # 表名
        verbose_name = "JSON文件"
        verbose_name_plural = verbose_name

class MCOJsonPage(CoreModel):
    """
    JSON 章节模型
    """
    recognition_result = models.ForeignKey(MCOJsonFile, related_name="pages", on_delete=models.CASCADE, null=True, blank=True)
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name="页码", help_text="页码")
    class Meta:
        db_table = table_prefix + "MCO_PAGE"  # 表名
        verbose_name = "JSON页面"
        verbose_name_plural = verbose_name


class MCOJsonContent(CoreModel):
    """
    JSON 内容模型
    """
    page = models.ForeignKey(MCOJsonPage, related_name="contents", on_delete=models.CASCADE, null=True, blank=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_content = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内content顺序",
                                           help_text="块内content顺序")

    class Meta:
        db_table = table_prefix + "MCO_CONTENT"  # 表名
        verbose_name = "JSON内容"
        verbose_name_plural = verbose_name

class MCOJsonParagraph(CoreModel):
    """
    JSON 段落模型
    """
    content = models.ForeignKey(MCOJsonContent, related_name="paragraphs", on_delete=models.CASCADE, null=True, blank=True)
    pdf = models.ForeignKey(MCOPdfFile, related_name="paragraphs", on_delete=models.CASCADE, null=True,
                                blank=True)
    value = models.TextField(null=True, blank=True, verbose_name="段落内容")
    ch_value = models.TextField(null=True, blank=True, verbose_name="段落中文内容")
    polygon = models.JSONField(verbose_name="段落多边形区域", blank=True, null=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_element  = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内元素顺序", help_text="块内元素顺序")
    key_words = models.TextField(null=True, blank=True, verbose_name="关键词")
    pdf_name = models.CharField(max_length=255, verbose_name="name", help_text="name", null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name="title", help_text="title", null=True, blank=True)
    drawing_number = models.CharField(max_length=255, verbose_name="drawing_number", help_text="drawing_number",
                                      null=True, blank=True)
    internal_code = models.CharField(max_length=255, verbose_name="internal_code", help_text="internal_code", null=True, blank=True)
    project_description = models.CharField(max_length=255, verbose_name="project_description", help_text="project_description", null=True, blank=True)
    flex_part_number = models.CharField(max_length=255, verbose_name="flex_part_number", help_text="flex_part_number", null=True, blank=True)
    rev = models.CharField(max_length=255, verbose_name="rev", help_text="rev", null=True, blank=True)
    num = models.IntegerField(default=0, null=True, blank=True, verbose_name="段落序号", help_text="段落序号")

    class Meta:
        db_table = table_prefix + "MCO_PARAGRAPH"  # 表名
        verbose_name = "JSON段落"
        verbose_name_plural = verbose_name

class MCOCMPPair(CoreModel):
    """
    JSON 段落模型
    """
    old_pdf = models.ForeignKey(MCOPdfFile, related_name="cmp_records_as_old", on_delete=models.CASCADE, null=True, blank=True)
    new_pdf = models.ForeignKey(MCOPdfFile, related_name="cmp_records_as_new", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = table_prefix + "MCO_CMPPAIR"  # 表名
        verbose_name = "比较记录"
        verbose_name_plural = verbose_name

class MCOCMPDiff(CoreModel):
    """
    JSON 段落模型
    """
    cmp_pair = models.ForeignKey(MCOCMPPair, related_name="cmp_diffs", on_delete=models.CASCADE, null=True, blank=True)
    old_pdf_path = models.TextField(null=True, blank=True, verbose_name="旧PDF地址")
    new_pdf_path = models.TextField(null=True, blank=True, verbose_name="新PDF地址")
    old_para_polygon = models.JSONField(verbose_name="旧段落区域", blank=True, null=True)
    new_para_polygon = models.JSONField(verbose_name="新段落区域", blank=True, null=True)
    old_para_value = models.TextField(null=True, blank=True, verbose_name="旧PDF内容")
    new_para_value = models.TextField(null=True, blank=True, verbose_name="新PDF内容")
    old_para_num = models.IntegerField(default=0, null=True, blank=True, verbose_name="旧段落序号", help_text="旧段落序号")
    new_para_num = models.IntegerField(default=0, null=True, blank=True, verbose_name="新段落序号", help_text="新段落序号")
    type = models.CharField(max_length=255, verbose_name="type", help_text="type", null=True, blank=True)
    analyze = models.TextField(null=True, blank=True, verbose_name="分析")
    diff = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = table_prefix + "MCO_CMPDIFF"  # 表名
        verbose_name = "比较区别"
        verbose_name_plural = verbose_name

class MCOFileHistory(CoreModel):
    """
    JSON 段落模型
    """
    file_name = models.TextField(null=True, blank=True, verbose_name="文件名")
    drawing_number = models.CharField(max_length=255, verbose_name="drawing_number", help_text="drawing_number", null=True, blank=True)
    rev = models.CharField(max_length=255, verbose_name="rev", help_text="rev", null=True, blank=True)
    is_analyzed = models.BooleanField(default=0, verbose_name='是否已分析', help_text="用于确认文件是否已经过分析提取", blank=True)
    analyze_rst = models.CharField(max_length=255, verbose_name="分析结果", help_text="分析结果", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "MCO_FILEHISTORY"  # 表名
        verbose_name = "历史文件"
        verbose_name_plural = verbose_name

class MonitorConfig(models.Model):
    directory_path = models.CharField('监控目录', max_length=500)
    # 存储 cron 表达式字段，也可拆成 hour/minute 分别存
    cron_minute = models.CharField('分钟', default='0', max_length=20)
    cron_hour   = models.CharField('小时',   default='2', max_length=20)
    enabled     = models.BooleanField('启用', default=False)
    last_run    = models.DateTimeField('上次运行', null=True, blank=True)

    def __str__(self):
        return f"{self.directory_path} @ {self.cron_hour}:{self.cron_minute} ({'ON' if self.enabled else 'OFF'})"

class ProcessedFile(models.Model):
    file_name    = models.CharField('文件名', max_length=500, unique=True)
    processed_at = models.DateTimeField('处理时间', auto_now_add=True)

    def __str__(self):
        return self.file_name