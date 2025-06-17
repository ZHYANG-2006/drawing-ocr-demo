import hashlib
import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from sma.utils.models import CoreModel, table_prefix, get_custom_app_models, FileModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Material(CoreModel):
    """
    JSON 章节模型
    """

    number = models.CharField(max_length=255, verbose_name="material_number", help_text="material_number", null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name="material_name", help_text="material_name", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "STACK_MATERIALS"  # 表名
        verbose_name = "材料"
        verbose_name_plural = verbose_name

class STACKPdfFile(FileModel):
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
    materials = models.ManyToManyField(
        Material,
        related_name='pdf_files',  # 反向查询时使用的名称，可自定义
        blank=True
    )
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
        db_table = table_prefix + "STACK_PDF"  # 表名
        verbose_name = "PDF文件"
        verbose_name_plural = verbose_name

class STACKJsonFile(FileModel):
    """
    JSON 文件模型
    """
    source_file = models.ForeignKey(STACKPdfFile, related_name="jsonfiles", on_delete=models.CASCADE, null=True, blank=True)
    analyze_version = models.CharField(max_length=255, verbose_name="PDF提取接口版本号", help_text="PDF提取接口版本号", blank=True)
    owner_file = models.CharField(max_length=255, verbose_name="所属文件", help_text="所属文件", blank=True)
    section_cnt = models.IntegerField(null=True, verbose_name="章节数", help_text="章节数", blank=True)
    paragraph_cnt = models.IntegerField(null=True, verbose_name="段落数", help_text="段落数", blank=True)
    table_cnt = models.IntegerField(null=True, verbose_name="表格数", help_text="表格数", blank=True)
    image_cnt = models.IntegerField(null=True, verbose_name="图片数", help_text="图片数", blank=True)

    class Meta:
        db_table = table_prefix + "STACK_JSON"  # 表名
        verbose_name = "JSON文件"
        verbose_name_plural = verbose_name

class STACKJsonContent(CoreModel):
    """
    JSON 内容模型
    """
    json_file = models.ForeignKey(STACKJsonFile, related_name="contents", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = table_prefix + "STACK_CONTENT"  # 表名
        verbose_name = "JSON内容"
        verbose_name_plural = verbose_name

class STACKJsonTable(CoreModel):
    """
    JSON 段落模型
    """
    json_content = models.ForeignKey(STACKJsonContent, related_name="tables", on_delete=models.CASCADE, null=True, blank=True)
    rows_num = models.IntegerField(default=0, verbose_name="行数")
    cols_num = models.IntegerField(default=0, verbose_name="列数")

    class Meta:
        db_table = table_prefix + "STACK_TABLE"  # 表名
        verbose_name = "JSON表格"
        verbose_name_plural = verbose_name

class STACKJsonTableCell(CoreModel):
    """
    JSON 表格单元格模型
    """
    table = models.ForeignKey(STACKJsonTable, related_name="cells", on_delete=models.CASCADE, null=True, blank=True)
    value = models.TextField(null=True, blank=True, verbose_name="单元格内容")
    row_index = models.IntegerField(default=0, verbose_name="行号")
    col_index = models.IntegerField(default=0, verbose_name="列号")
    row_span = models.IntegerField(default=0, verbose_name="行扩展")
    col_span = models.IntegerField(default=0, verbose_name="列扩展")
    type = models.CharField(max_length=255, verbose_name="type", help_text="type", null=True, blank=True)
    bg_color = models.CharField(max_length=255, verbose_name="bg_color", help_text="bg_color", null=True, blank=True)
    font_color = models.CharField(max_length=255, verbose_name="font_color", help_text="font_color", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "STACK_TABLECELL"  # 表名
        verbose_name = "JSON表格单元格"
        verbose_name_plural = verbose_name