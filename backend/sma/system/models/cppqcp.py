import hashlib
import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from sma.utils.models import CoreModel, table_prefix, get_custom_app_models, FileModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AnalyzeStatistic(CoreModel):
    """
    分析统计
    """
    file_type = models.CharField(max_length=200, verbose_name="文件类型", help_text="文件类型")
    b_type = models.CharField(max_length=200, verbose_name="业务类型", help_text="业务类型")
    min_time = models.IntegerField(null=True, verbose_name="最短分析时间", help_text="最短分析时间", blank=True)
    min_section_cnt = models.IntegerField(null=True, verbose_name="最短分析时间的章节数",
                                          help_text="最短分析时间的章节数", blank=True)
    min_paragraph_cnt = models.IntegerField(null=True, verbose_name="最短分析时间的段落数",
                                            help_text="最短分析时间的段落数", blank=True)
    min_table_cnt = models.IntegerField(null=True, verbose_name="最短分析时间的表格数",
                                        help_text="最短分析时间的表格数", blank=True)
    min_picture_cnt = models.IntegerField(null=True, verbose_name="最短分析时间的图片数",
                                          help_text="最短分析时间的图片数", blank=True)
    min_size = models.CharField(max_length=50, verbose_name="最短分析时间文件大小", help_text="最短分析时间文件大小",
                                blank=True)
    min_page = models.IntegerField(null=True, verbose_name="最短分析时间的页数", help_text="最短分析时间的页数",
                                   blank=True)
    max_time = models.IntegerField(null=True, verbose_name="最长分析时间", help_text="最长分析时间", blank=True)
    max_section_cnt = models.IntegerField(null=True, verbose_name="最长分析时间的章节数",
                                          help_text="最长分析时间的章节数", blank=True)
    max_paragraph_cnt = models.IntegerField(null=True, verbose_name="最长分析时间的段落数",
                                            help_text="最长分析时间的段落数", blank=True)
    max_table_cnt = models.IntegerField(null=True, verbose_name="最长分析时间的表格数",
                                        help_text="最长分析时间的表格数", blank=True)
    max_picture_cnt = models.IntegerField(null=True, verbose_name="最长分析时间的图片数",
                                          help_text="最长分析时间的图片数", blank=True)
    max_size = models.CharField(max_length=50, verbose_name="最长分析时间文件大小", help_text="最长分析时间文件大小",
                                blank=True)
    max_page = models.IntegerField(null=True, verbose_name="最长分析时间的页数", help_text="最长分析时间的页数",
                                   blank=True)
    average_time = models.IntegerField(null=True, verbose_name="平均分析时间", help_text="平均分析时间", blank=True)
    avg_section_cnt = models.IntegerField(null=True, verbose_name="平均分析时间的章节数",
                                          help_text="平均分析时间的章节数", blank=True)
    avg_paragraph_cnt = models.IntegerField(null=True, verbose_name="平均分析时间的段落数",
                                            help_text="平均分析时间的段落数", blank=True)
    avg_table_cnt = models.IntegerField(null=True, verbose_name="平均分析时间的表格数",
                                        help_text="平均分析时间的表格数", blank=True)
    avg_picture_cnt = models.IntegerField(null=True, verbose_name="平均分析时间的图片数",
                                          help_text="平均分析时间的图片数", blank=True)
    avg_size = models.CharField(max_length=50, verbose_name="平均分析时间文件大小", help_text="平均分析时间文件大小",
                                blank=True)
    mvg_page = models.IntegerField(null=True, verbose_name="分析时间的页数", help_text="最短分析时间的页数", blank=True)

    class Meta:
        db_table = table_prefix + "ANASTATISTIC"  # 表名
        verbose_name = "各业务文件分析统计表"
        verbose_name_plural = verbose_name
        ordering = ("id",)


class Customer(CoreModel):
    """
    Customer 模型，包含 type 和 name 属性
    """
    type = models.CharField(max_length=50, verbose_name="客户类型", help_text="客户的类型")
    name = models.CharField(max_length=255, verbose_name="客户名称", help_text="客户的名称")

    class Meta:
        db_table =  table_prefix + "customer"
        verbose_name = "客户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.type} - {self.name}"


class MaterialNumber(CoreModel):
    """
    MaterialNumber 模型，包含 phase 和 material_number 属性
    """
    phase = models.CharField(max_length=100, verbose_name="阶段", help_text="材料所处的阶段")
    material_number = models.CharField(max_length=100, verbose_name="料号", help_text="料号")

    class Meta:
        db_table =  table_prefix + "material_number"
        verbose_name = "料号"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.phase} - {self.material_number}"

class Feature(CoreModel):
    """
    Feature 表模型
    """
    feature_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="特性名称", help_text="特性的名称")
    feature_type = models.CharField(null=True, blank=True, max_length=255, verbose_name="特性类型", help_text="特性的类型")
    att_description = models.TextField(null=True, blank=True, verbose_name="属性描述", help_text="特性的属性描述")
    tolerance_type = models.FloatField(null=True, blank=True, verbose_name="公差类型", help_text="特性公差类型")
    target_value = models.FloatField(null=True, blank=True, verbose_name="目标值", help_text="特性的目标值")
    upper_tolerance = models.FloatField(null=True, blank=True, verbose_name="上公差", help_text="上公差值")
    is_uppert_contain = models.BooleanField(blank=True, max_length=50, verbose_name="是否包含上公差", help_text="是否包含上公差值")
    lower_tolerance = models.FloatField(null=True, blank=True, verbose_name="下公差", help_text="下公差值")
    is_lowert_contain = models.BooleanField(blank=True, max_length=50, verbose_name="是否包含下公差", help_text="是否包含下公差值")
    unit = models.CharField(null=True, blank=True, max_length=50, verbose_name="单位", help_text="特性单位")

    class Meta:
        db_table = table_prefix + "feature"
        verbose_name = "特性"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.feature_name


class PdfFile(FileModel):
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

    branch = models.CharField(max_length=255, verbose_name="阶段", help_text="文件的阶段", blank=True, null=True)
    phase = models.CharField(max_length=255, verbose_name="阶段", help_text="文件的阶段", blank=True, null=True)
    process = models.CharField(max_length=255, verbose_name="处理过程", help_text="文件处理过程", blank=True, null=True)
    file_type = models.CharField(max_length=255, verbose_name="文件类型", help_text="文件的类型", blank=True, null=True)
    is_universal = models.CharField(max_length=255, default="N", verbose_name="是否通用", help_text="是否为通用文件", blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    material_number = models.CharField(max_length=255, verbose_name="材料编号", help_text="文件对应的材料编号",
                                       blank=True, null=True)
    type = models.CharField(max_length=255, verbose_name="LOB类型", help_text="LOB类型",
                                       blank=True, null=True)
    lob = models.CharField(max_length=255, verbose_name="LOB", help_text="文件的业务领域", blank=True, null=True)
    pfmea_type = models.CharField(max_length=255, verbose_name="PFMEA类别", help_text="PFMEA类别", blank=True, null=True)

    # 统计字段
    total_count = models.IntegerField(null=True, default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(null=True, default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(null=True, default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(null=True, default=0, verbose_name="未通过的子项数量")
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    def update_check_status(self):
        # 获取按 create_datetime 降序排列的最新 jsonfile
        latest_jsonfile = self.jsonfiles.order_by('-create_datetime').first()

        if latest_jsonfile:
            # 从最新的 jsonfile 中获取统计数据
            self.passed_count = latest_jsonfile.passed_count
            self.failed_count = latest_jsonfile.failed_count
            self.unchecked_count = latest_jsonfile.unchecked_count
            self.total_count = latest_jsonfile.total_count

            # 保存更新
            self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])
        else:
            # 如果没有 jsonfiles，则设置计数为 0
            self.passed_count = 0
            self.failed_count = 0
            self.unchecked_count = 0
            self.total_count = 0
            self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])

    def reset_status(self):
        # 获取按 create_datetime 降序排列的最新 jsonfile
        latest_jsonfile = self.jsonfiles.order_by('-create_datetime').first()
        if latest_jsonfile:
            latest_jsonfile.reset_status()
        self.update_check_status()

    def update_progress(self, current_step, total_steps):
        """
        更新分析进度
        """
        self.progress = (current_step / total_steps) * 100
        self.save(update_fields=['progress'])

    class Meta:
        db_table = table_prefix + "FILE_PDF"  # 表名
        verbose_name = "PDF文件"
        verbose_name_plural = verbose_name

class JsonFile(FileModel):
    """
    JSON 文件模型
    """
    source_file = models.ForeignKey(PdfFile, related_name="jsonfiles", on_delete=models.CASCADE, null=True, blank=True)
    analyze_version = models.CharField(max_length=255, verbose_name="PDF提取接口版本号", help_text="PDF提取接口版本号", blank=True)
    owner_file = models.CharField(max_length=255, verbose_name="所属文件", help_text="所属文件", blank=True)
    section_cnt = models.IntegerField(null=True, verbose_name="章节数", help_text="章节数", blank=True)
    paragraph_cnt = models.IntegerField(null=True, verbose_name="段落数", help_text="段落数", blank=True)
    table_cnt = models.IntegerField(null=True, verbose_name="表格数", help_text="表格数", blank=True)
    image_cnt = models.IntegerField(null=True, verbose_name="图片数", help_text="图片数", blank=True)

    _reset = False  # 用于判断是否是重置

    def update_check_status(self):
        sections = self.sections.all()

        self.passed_count = sum(section.passed_count for section in sections)
        self.failed_count = sum(section.failed_count for section in sections)
        self.unchecked_count = sum(section.unchecked_count for section in sections)
        self.total_count = sum(section.total_count for section in sections)

        self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])
        # 向上传递
        if not self._reset:
            self.source_file.update_check_status()

    def reset_status(self):
        self._reset = True
        sections = self.sections.all()
        for section in sections:
            section.reset_status()
        self.update_check_status()
        self._reset = False

    class Meta:
        db_table = table_prefix + "FILE_JSON"  # 表名
        verbose_name = "JSON文件"
        verbose_name_plural = verbose_name

class ReviewResult(CoreModel):
    """
    检查结果模型
    """
    group = models.ForeignKey(
        'ReviewGroup',
        related_name="results",
        on_delete=models.CASCADE,
        verbose_name="检查结果组"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("OnGoing", "进行中"),
            ("Closed", "已关闭"),
            ("Cancel", "过期")
        ],
        default="OnGoing",
        verbose_name="审核状态",
        help_text="审核状态，可以是进行中或已关闭"
    )
    reason = models.TextField(null=True, blank=True, verbose_name="未通过原因")

    # 新增字段
    feature_recognized = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="识别特性", help_text="表示是否已识别的特性"
    )
    plm_standard_process = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="PLM标准工艺", help_text="特性的标准工艺"
    )
    plm_device_type = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="设备类别", help_text="设备类别"
    )
    plm_procedure = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="步骤", help_text="步骤"
    )
    function22 = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="2.2功能", help_text="2.2功能"
    )
    function23 = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="2.3功能", help_text="2.3功能"
    )
    feature_category = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="特性类别", help_text="特性的类别"
    )
    checkCategory = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="特性类型", help_text="特性的类型"
    )
    ###############################################################################################
    checkedItem = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="特性编号", help_text="特性编号"
    )
    checkedQuest = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="特性名称", help_text="特性的名称"
    )
    checkRule = models.CharField(
        max_length=765, null=True, blank=True, verbose_name="属性描述", help_text="特性的属性描述"
    )
    limitType = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="公差类型", help_text="特性公差类型"
    )
    standardValue = models.DecimalField(
        max_digits=10, decimal_places=4, default=0, null=True, blank=True, verbose_name="目标值", help_text="特性的目标值"
    )
    limitUp = models.DecimalField(
        max_digits=10, decimal_places=4, default=0, null=True, blank=True, verbose_name="上公差", help_text="特性的上公差值"
    )
    containLimitUp = models.CharField(
        max_length=255, default="N", null=True, blank=True, verbose_name="是否包含上公差", help_text="是否包含上公差值"
    )
    limitDown = models.DecimalField(
        max_digits=10, decimal_places=4, default=0, null=True, blank=True, verbose_name="下公差", help_text="特性的下公差值"
    )
    containLimitDown = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="是否包含下公差", help_text="是否包含下公差值"
    )
    unitCode = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="单位", help_text="特性单位"
    )
    evaluation_measurement = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="评价/测量技术", help_text="评价/测量技术"
    )
    capacity = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="容量", help_text="容量"
    )
    frequency = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="频率", help_text="频率"
    )
    control_method = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="控制方法", help_text="控制方法"
    )
    action = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="测试", help_text="测试"
    )
    responsibility = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="责任人", help_text="责任人"
    )
    name = models.CharField(max_length=255, verbose_name="文件名称", help_text="文件名称", blank=True, null=True)
    process = models.CharField(max_length=255, verbose_name="处理过程", help_text="文件处理过程", blank=True, null=True)
    file_type = models.CharField(max_length=255, verbose_name="文件类型", help_text="文件的类型", blank=True, null=True)
    is_universal = models.CharField(max_length=255, default="N", verbose_name="是否通用", help_text="是否为通用文件",
                                    blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    material_number = models.CharField(max_length=255, verbose_name="材料编号", help_text="文件对应的材料编号",
                                       blank=True, null=True)
    type = models.CharField(max_length=255, verbose_name="LOB类型", help_text="LOB类型",
                                       blank=True, null=True)
    lob = models.CharField(max_length=255, verbose_name="LOB", help_text="文件的业务领域", blank=True, null=True)
    pfmea_type = models.CharField(max_length=255, verbose_name="PFMEA类别", help_text="PFMEA类别", blank=True,
                                  null=True)
    branch = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="厂区", help_text="厂区"
    )
    last_status = models.CharField(max_length=255, verbose_name="最后状态", help_text="最后状态", blank=True, null=True)
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")
    value = models.TextField(null=True, blank=True, verbose_name="内容")

    class Meta:
        db_table = table_prefix + "REVIEW_RESULT"
        verbose_name = "检查结果"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.feature_name} - {self.status}"

class ReviewGroup(CoreModel):
    order_in_version = models.IntegerField(default=0, null=True, blank=True, verbose_name="version内", help_text="全局顺序")
    element_type = models.CharField(
        max_length=50,
        choices=[
            ("section", "JsonSection"),
            ("paragraph", "JsonParagraph"),
            ("cell", "JsonTableCell"),
            ("image", "JsonImage"),
        ],
        verbose_name="元素类型"
    )

    sections = models.ManyToManyField(
        'JsonSection',
        related_name="review_groups",
        through="SectionReviewGroup",
        verbose_name="关联章节"
    )
    paragraphs = models.ManyToManyField(
        'JsonParagraph',
        related_name="review_groups",
        through="ParagraphReviewGroup",
        verbose_name="关联段落"
    )
    images = models.ManyToManyField(
        'JsonImage',
        related_name="review_groups",
        through="ImageReviewGroup",
        verbose_name="关联图片"
    )
    cells = models.ManyToManyField(
        'JsonTableCell',
        related_name="review_groups",
        through="CellReviewGroup",
        verbose_name="关联单元格"
    )

    review_version = models.ForeignKey(
        'ReviewVersion',
        related_name='review_groups',
        on_delete=models.CASCADE,
        verbose_name="审核版本",
        help_text="关联的审核版本"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("OnGoing", "进行中"),
            ("Closed", "已关闭"),
            ("Cancel", "过期")
        ],
        default="OnGoing",
        verbose_name="审核状态",
        help_text="审核状态，可以是进行中或已关闭"
    )

    element_ids = models.JSONField(verbose_name="元素ID列表", help_text="存储多个元素ID", blank=True, null=True)
    row_index = models.IntegerField(null=True, blank=True, verbose_name="行号（仅适用于表格单元格）")

    name = models.CharField(max_length=255, verbose_name="文件名称", help_text="文件名称", blank=True, null=True)
    process = models.CharField(max_length=255, verbose_name="处理过程", help_text="文件处理过程", blank=True, null=True)
    file_type = models.CharField(max_length=255, verbose_name="文件类型", help_text="文件的类型", blank=True, null=True)
    is_universal = models.CharField(max_length=255, default="N", verbose_name="是否通用", help_text="是否为通用文件",
                                    blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    material_number = models.CharField(max_length=255, verbose_name="材料编号", help_text="文件对应的材料编号",
                                       blank=True, null=True)
    type = models.CharField(max_length=255, verbose_name="LOB类型", help_text="LOB类型",
                                       blank=True, null=True)
    lob = models.CharField(max_length=255, verbose_name="LOB", help_text="文件的业务领域", blank=True, null=True)
    pfmea_type = models.CharField(max_length=255, verbose_name="PFMEA类别", help_text="PFMEA类别", blank=True,
                                  null=True)
    branch = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="厂区", help_text="厂区"
    )
    last_status = models.CharField(max_length=255, verbose_name="最后状态", help_text="最后状态", blank=True, null=True)
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")
    value = models.TextField(null=True, blank=True, verbose_name="内容")

    class Meta:
        db_table = table_prefix + "REVIEW_GROUP"
        verbose_name = "检查结果组"
        verbose_name_plural = verbose_name

class SectionReviewGroup(models.Model):
    review_group = models.ForeignKey(ReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    section = models.ForeignKey('JsonSection', on_delete=models.CASCADE, verbose_name="章节")

    class Meta:
        db_table = table_prefix + "SectionReviewGroup"
        verbose_name = "章节关联表"
        verbose_name_plural = verbose_name


class ParagraphReviewGroup(models.Model):
    review_group = models.ForeignKey(ReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    paragraph = models.ForeignKey('JsonParagraph', on_delete=models.CASCADE, verbose_name="段落")

    class Meta:
        db_table = table_prefix + "ParagraphReviewGroup"
        verbose_name = "段落关联表"
        verbose_name_plural = verbose_name


class ImageReviewGroup(models.Model):
    review_group = models.ForeignKey(ReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    image = models.ForeignKey('JsonImage', on_delete=models.CASCADE, verbose_name="图片")

    class Meta:
        db_table = table_prefix + "ImageReviewGroup"
        verbose_name = "图片关联表"
        verbose_name_plural = verbose_name


class CellReviewGroup(models.Model):
    review_group = models.ForeignKey(ReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    cell = models.ForeignKey('JsonTableCell', on_delete=models.CASCADE, verbose_name="单元格")

    class Meta:
        db_table = table_prefix + "CellReviewGroup"
        verbose_name = "单元格关联表"
        verbose_name_plural = verbose_name



class ReviewVersion(CoreModel):
    """
    审核版本模型
    """
    # 与 JsonFile 的多对一关系
    jsonfile = models.ForeignKey(
        'JsonFile',
        related_name='review_versions',
        on_delete=models.CASCADE,
        verbose_name="关联的 JSON 文件",
        help_text="此审核版本关联的 JSON 文件"
    )

    # 审核状态字段
    status = models.CharField(
        max_length=20,
        choices=[
            ("OnGoing", "进行中"),
            ("Closed", "已关闭"),
            ("Cancel", "过期")
        ],
        default="OnGoing",
        verbose_name="审核状态",
        help_text="审核状态，可以是进行中或已关闭"
    )

    file_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    branch = models.CharField(max_length=255, verbose_name="厂区", help_text="厂区", blank=True, null=True)
    process = models.CharField(max_length=255, verbose_name="制程", help_text="制程", blank=True, null=True)
    file_type = models.CharField(max_length=255, verbose_name="文件类型", help_text="文件的类型", blank=True, null=True)
    is_universal = models.CharField(max_length=255, default="N", verbose_name="是否通用", help_text="是否为通用文件",
                                    blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    material_number = models.CharField(max_length=255, verbose_name="材料编号", help_text="文件对应的材料编号",
                                       blank=True, null=True)
    type = models.CharField(max_length=255, verbose_name="LOB类型", help_text="LOB类型",
                                       blank=True, null=True)
    lob = models.CharField(max_length=255, verbose_name="LOB", help_text="文件的业务领域", blank=True, null=True)
    pfmea_type = models.CharField(max_length=255, verbose_name="PFMEA类别", help_text="PFMEA类别", blank=True,
                                  null=True)
    has_pfmea = models.BooleanField(null=True, default=False, verbose_name='是否发送pfmea',
                                      help_text="是否发送pfmea",
                                      blank=True)
    pfmea_time = models.DateTimeField(null=True, verbose_name="发送pfmea时间", help_text="发送pfmea时间",
                                               blank=True)
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    last_status = models.CharField(max_length=255, verbose_name="最后状态", help_text="最后状态", blank=True, null=True)

    class Meta:
        db_table = table_prefix + "REVIEW_VERSION"  # 表名
        verbose_name = "审核版本"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"ReviewVersion (JSON File ID: {self.jsonfile.id}, Status: {self.status})"


class JsonSection(CoreModel):
    """
    JSON 章节模型
    """
    recognition_result = models.ForeignKey(JsonFile, related_name="sections", on_delete=models.CASCADE, null=True, blank=True)
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name="页码", help_text="页码")
    polygon = models.JSONField(verbose_name="多边形区域", blank=True, null=True)
    num = models.IntegerField(verbose_name="章节序号")
    value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    ch_value = models.TextField(null=True, blank=True, verbose_name="章节中文名称")
    thai_value = models.TextField(null=True, blank=True, verbose_name="章节泰文")
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_section  = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内章节顺序", help_text="块内章节顺序")
    has_strike_through = models.BooleanField(default=0, verbose_name='是否有划去线', help_text="用于判断是否需处理划去线",
                                      blank=True)
    has_xbar = models.BooleanField(default=0, verbose_name='是否有xbar', help_text="用于判断是否需处理xbar",
                                      blank=True)
    true_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    true_ch_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    true_thai_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    # 统计字段
    total_count = models.IntegerField(default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(default=0, verbose_name="未通过的子项数量")

    _skip_signals = False  # 用于控制是否跳过信号

    _reset = False  # 用于判断是否是重置

    def update_check_status(self):
        contents = self.contents.all()

        self.passed_count = sum(content.passed_count for content in contents)
        self.failed_count = sum(content.failed_count for content in contents)
        self.unchecked_count = sum(content.unchecked_count for content in contents)
        self.total_count = sum(content.total_count for content in contents)

        self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])

        # 向上传递
        if not self._reset:
            self.recognition_result.update_check_status()

    def reset_status(self):
        self._reset = True
        contents = self.contents.all()
        for content in contents:
            content.reset_status()
        self.update_check_status()
        self._reset = False

    class Meta:
        db_table = table_prefix + "JSON_SECTION"  # 表名
        verbose_name = "JSON章节"
        verbose_name_plural = verbose_name


class JsonContent(CoreModel):
    """
    JSON 内容模型
    """
    section = models.ForeignKey(JsonSection, related_name="contents", on_delete=models.CASCADE, null=True, blank=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_content = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内content顺序",
                                           help_text="块内content顺序")
    polygon = models.JSONField(verbose_name="多边形区域", blank=True, null=True)

    # 统计字段
    total_count = models.IntegerField(default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(default=0, verbose_name="未通过的子项数量")

    _skip_signals = False  # 用于控制是否跳过信号

    _reset = False  # 用于判断是否是重置

    def update_check_status(self):
        """
        递归统计页面内所有最底层子项的通过、未通过和未校验的数量
        """
        # 统计段落、表格单元格
        paragraphs = self.paragraphs.all()
        tables = self.tables.all()
        # 统计关联的 JsonImage
        content_type = ContentType.objects.get_for_model(self)
        images = JsonImage.objects.filter(content_type=content_type, object_id=self.id)

        self.passed_count = (sum(paragraph.passed_count for paragraph in paragraphs)
                             + sum(table.passed_count for table in tables)
                             + sum(image.passed_count for image in images))
        self.failed_count = (sum(paragraph.failed_count for paragraph in paragraphs)
                             + sum(table.failed_count for table in tables)
                             + sum(image.failed_count for image in images))
        self.unchecked_count = (sum(paragraph.unchecked_count for paragraph in paragraphs)
                                + sum(table.unchecked_count for table in tables)
                                + sum(image.unchecked_count for image in images))
        self.total_count = (sum(paragraph.total_count for paragraph in paragraphs)
                            + sum(table.total_count for table in tables)
                            + sum(image.total_count for image in images))

        self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])

        # 向上传递
        if not self._reset:
            self.section.update_check_status()

    # def reset_status(self):
    #     self._reset = True
    #     pages = self.pages.all()
    #     for page in pages:
    #         page.reset_status()
    #     self.update_check_status()
    #     self._reset = False

    def reset_status(self):
        self._reset = True
        # 统计段落、表格单元格
        paragraphs = self.paragraphs.all()
        tables = self.tables.all()
        # 统计关联的 JsonImage
        content_type = ContentType.objects.get_for_model(self)
        images = JsonImage.objects.filter(content_type=content_type, object_id=self.id)
        for paragraph in paragraphs:
            paragraph.reset_status()
        for table in tables:
            table.reset_status()
        for image in images:
            image.reset_status()
        self.update_check_status()
        self._reset = False

    class Meta:
        db_table = table_prefix + "JSON_CONTENT"  # 表名
        verbose_name = "JSON内容"
        verbose_name_plural = verbose_name

class JsonParagraph(CoreModel):
    """
    JSON 段落模型
    """
    content = models.ForeignKey(JsonContent, related_name="paragraphs", on_delete=models.CASCADE, null=True, blank=True)
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name="页码", help_text="页码")
    value = models.TextField(null=True, blank=True, verbose_name="段落内容")
    ch_value = models.TextField(null=True, blank=True, verbose_name="段落中文内容")
    thai_value = models.TextField(null=True, blank=True, verbose_name="段落泰文")
    polygon = models.JSONField(verbose_name="段落多边形区域", blank=True, null=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_element  = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内元素顺序", help_text="块内元素顺序")
    has_strike_through = models.BooleanField(default=0, verbose_name='是否有划去线', help_text="用于判断是否需处理划去线",
                                      blank=True)
    has_xbar = models.BooleanField(default=0, verbose_name='是否有xbar', help_text="用于判断是否需处理xbar",
                                      blank=True)
    true_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    true_ch_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    true_thai_value = models.TextField(null=True, blank=True, verbose_name="章节名称")

    total_count = models.IntegerField(default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(default=0, verbose_name="未通过的子项数量")

    # 新增字段
    is_checked = models.BooleanField(default=False, verbose_name="是否已检查", help_text="该段落是否已被检查")
    is_passed = models.BooleanField(null=True, blank=True, verbose_name="检查结果", help_text="是否通过检查")
    check_reason = models.TextField(null=True, blank=True, verbose_name="检查原因", help_text="如果未通过，填写原因")
    checked_by = models.CharField(max_length=255, null=True, blank=True, verbose_name="检查者",
                                  help_text="检查该段落的用户")

    _skip_signals = False  # 用于控制是否跳过信号

    _reset = False  # 用于判断是否是重置

    def update_check_status(self):
        # 如果标志位为 True，则跳过信号
        if self._skip_signals:
            return

        # 设置标志位为 True，避免递归触发
        self._skip_signals = True

        self.unchecked_count = 0 if self.is_checked else 1
        self.passed_count = 1 if self.is_checked and self.is_passed else 0
        self.failed_count = 1 if self.is_checked and not self.is_passed else 0
        self.total_count = 1

        self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])

        # 向上传递
        if not self._reset:
            self.content.update_check_status()

        # 重置标志位
        self._skip_signals = False

    def reset_status(self):
        """
        重置段落状态
        """
        self._reset = True
        self.is_checked = False
        self.is_passed = None
        self.check_reason = None
        self.checked_by = None
        self.save(update_fields=['is_checked', 'is_passed', 'check_reason', 'checked_by'])
        self.update_check_status()
        self._reset = False

    class Meta:
        db_table = table_prefix + "JSON_PARAGRAPH"  # 表名
        verbose_name = "JSON段落"
        verbose_name_plural = verbose_name


class JsonTable(CoreModel):
    """
    JSON 表格模型
    """
    content = models.ForeignKey(JsonContent, related_name="tables", on_delete=models.CASCADE, null=True, blank=True)
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name="页码", help_text="页码")
    rows_num = models.IntegerField(default=0, verbose_name="行数")
    cols_num = models.IntegerField(default=0, verbose_name="列数")
    polygon = models.JSONField(verbose_name="表格多边形区域", blank=True, null=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_element  = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内元素顺序", help_text="块内元素顺序")

    total_count = models.IntegerField(default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(default=0, verbose_name="未通过的子项数量")

    _skip_signals = False  # 用于控制是否跳过信号

    _reset = False  # 用于判断是否是重置

    def update_check_status(self):
        rows = self.rows.all()

        self.passed_count = sum(row.passed_count for row in rows)
        self.failed_count = sum(row.failed_count for row in rows)
        self.unchecked_count = sum(row.unchecked_count for row in rows)
        self.total_count = sum(row.total_count for row in rows)

        self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])

        # 向上传递
        if not self._reset:
            self.content.update_check_status()

    def reset_status(self):
        self._reset = True
        rows = self.rows.all()
        for row in rows:
            row.reset_status()
        self.update_check_status()
        self._reset = False

    class Meta:
        db_table = table_prefix + "JSON_TABLE"  # 表名
        verbose_name = "JSON表格"
        verbose_name_plural = verbose_name

class JsonImage(CoreModel):
    """
    JSON 图片模型
    """
    content = models.ForeignKey(JsonContent, related_name="images", on_delete=models.CASCADE, null=True, blank=True)
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name="页码", help_text="页码")
    image_bytes = models.BinaryField(verbose_name="图像数据", blank=True, null=True)
    image_width = models.IntegerField(null=True, verbose_name="图片宽度", help_text="图片宽度", blank=True)
    image_length = models.IntegerField(null=True, verbose_name="图片长度", help_text="图片长度", blank=True)
    polygon = models.JSONField(verbose_name="图像多边形区域", blank=True, null=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_element = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内图片顺序",
                                        help_text="块内图片顺序")

    total_count = models.IntegerField(default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(default=0, verbose_name="未通过的子项数量")

    # 新增字段
    is_checked = models.BooleanField(default=False, verbose_name="是否已检查", help_text="该段落是否已被检查")
    is_passed = models.BooleanField(null=True, blank=True, verbose_name="检查结果", help_text="是否通过检查")
    check_reason = models.TextField(null=True, blank=True, verbose_name="检查原因", help_text="如果未通过，填写原因")
    checked_by = models.CharField(max_length=255, null=True, blank=True, verbose_name="检查者",
                                  help_text="检查该段落的用户")

    _skip_signals = False  # 用于控制是否跳过信号

    _reset = False  # 用于判断是否是重置


    def update_check_status(self):
        # 如果标志位为 True，则跳过信号
        if self._skip_signals:
            return

        # 设置标志位为 True，避免递归触发
        self._skip_signals = True

        self.unchecked_count = 0 if self.is_checked else 1
        self.passed_count = 1 if self.is_checked and self.is_passed else 0
        self.failed_count = 1 if self.is_checked and not self.is_passed else 0
        self.total_count = 1

        self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])

        # 向上传递
        if not self._reset:
            self.content_object.update_check_status()

        # 重置标志位
        self._skip_signals = False

    def reset_status(self):
        """
        重置段落状态
        """
        self._reset = True
        self.is_checked = False
        self.is_passed = None
        self.check_reason = None
        self.checked_by = None
        self.save(update_fields=['is_checked', 'is_passed', 'check_reason', 'checked_by'])
        self.update_check_status()
        self._reset = False

    class Meta:
        db_table = table_prefix + "JSON_IMAGE"  # 表名
        verbose_name = "JSON图片"
        verbose_name_plural = verbose_name

class JsonTableCell(CoreModel):
    """
    JSON 表格单元格模型
    """
    table = models.ForeignKey(JsonTable, related_name="cells", on_delete=models.CASCADE, null=True, blank=True)
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name="页码", help_text="页码")
    cell_type = models.IntegerField(default=0, null=True, blank=True, verbose_name="单元格类型.0,文本;1,图片;", help_text="单元格类型0,文本;1,图片;")
    value = models.TextField(null=True, blank=True, verbose_name="单元格内容")
    ch_value = models.TextField(null=True, blank=True, verbose_name="单元格中文内容")
    thai_value = models.TextField(null=True, blank=True, verbose_name="单元格泰文")
    image_bytes = models.BinaryField(verbose_name="图像数据", blank=True, null=True)
    row_index = models.IntegerField(default=0, verbose_name="行号")
    col_index = models.IntegerField(default=0, verbose_name="列号")
    row_span = models.IntegerField(default=0, verbose_name="行扩展")
    col_span = models.IntegerField(default=0, verbose_name="列扩展")
    polygon = models.JSONField(verbose_name="表格多边形区域", blank=True, null=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_cell = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内单元格顺序",
                                           help_text="块内单元格顺序")
    has_strike_through = models.BooleanField(default=0, verbose_name='是否有划去线', help_text="用于判断是否需处理划去线",
                                      blank=True)
    has_xbar = models.BooleanField(default=0, verbose_name='是否有xbar', help_text="用于判断是否需处理xbar",
                                      blank=True)
    true_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    true_ch_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    true_thai_value = models.TextField(null=True, blank=True, verbose_name="章节名称")
    is_virtual = models.BooleanField(default=False, verbose_name="是否虚拟单元格", help_text="是否虚拟单元格")

    total_count = models.IntegerField(default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(default=0, verbose_name="未通过的子项数量")

    # 新增字段
    is_checked = models.BooleanField(default=False, verbose_name="是否已检查", help_text="该段落是否已被检查")
    is_passed = models.BooleanField(null=True, blank=True, verbose_name="检查结果", help_text="是否通过检查")
    check_reason = models.TextField(null=True, blank=True, verbose_name="检查原因", help_text="如果未通过，填写原因")
    checked_by = models.CharField(max_length=255, null=True, blank=True, verbose_name="检查者", help_text="检查该段落的用户")

    _skip_signals = False  # 用于控制是否跳过信号

    _reset = False  # 用于判断是否是重置

    def assign_review_group(self):
        """
        分配检查结果组（按行号）
        """
        if self.table:
            group, _ = ReviewGroup.objects.get_or_create(
                element_type="cell",
                element_id=self.table.id,
                row_index=self.row_index
            )
            self.review_group = group
            self.save(update_fields=["review_group"])

    def update_check_status(self):
        # 如果标志位为 True，则跳过信号
        if self._skip_signals:
            return

        # 设置标志位为 True，避免递归触发
        self._skip_signals = True

        self.unchecked_count = 0 if self.is_checked else 1
        self.passed_count = 1 if self.is_checked and self.is_passed else 0
        self.failed_count = 1 if self.is_checked and not self.is_passed else 0
        self.total_count = 1

        self.save(update_fields=['passed_count', 'failed_count', 'unchecked_count', 'total_count'])

        # 向上传递
        if not self._reset:
            self.tables.update_check_status()

        # 重置标志位
        self._skip_signals = False

    def reset_status(self):
        """
        重置段落状态
        """
        self._reset = True
        self.is_checked = False
        self.is_passed = None
        self.check_reason = None
        self.checked_by = None
        self.save(update_fields=['is_checked', 'is_passed', 'check_reason', 'checked_by'])
        self.update_check_status()
        self._reset = False

    class Meta:
        db_table = table_prefix + "JSON_TABLECELL"  # 表名
        verbose_name = "JSON表格单元格"
        verbose_name_plural = verbose_name


class ImageFile(FileModel):
    """
    图片文件模型
    """
    image_file = models.ForeignKey(JsonImage, related_name="json_images", on_delete=models.CASCADE, null=True, blank=True)
    resolution = models.CharField(max_length=50, verbose_name="分辨率", help_text="图片文件的分辨率", null=True, blank=True)
    format = models.CharField(max_length=10, verbose_name="图片格式", help_text="图片格式", null=True, blank=True)  # 如 jpg, png
    image_length = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="图片长度", help_text="图片长度")
    image_width = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="图片宽度", help_text="图片宽度")
    owner_file = models.CharField(max_length=255, verbose_name="所属文件", help_text="所属文件", blank=True)
    owner_file_type = models.CharField(max_length=10, verbose_name="图片所属内容类型", help_text="图片所属内容类型", null=True, blank=True)
    owner_file_page = models.IntegerField(null=True, default=0, verbose_name="所在页码", help_text="所在页码", blank=True)

    class Meta:
        db_table = table_prefix + "FILE_IMAGE"  # 表名
        verbose_name = "图片文件"
        verbose_name_plural = verbose_name


class JsonXBar(CoreModel):
    """
    JSON 单元格XBar模型
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    xbar_polygon = models.JSONField(verbose_name="横线多边形区域")
    which_word_has_xbar = models.CharField(max_length=100, verbose_name="带横线的文字")
    word_polygon = models.JSONField(verbose_name="带横线的文字多边形区域")

    class Meta:
        db_table = table_prefix + "JSON_XBar"  # 表名
        verbose_name = "JSONXBar"
        verbose_name_plural = verbose_name


class JsonStrikeThroughText(CoreModel):
    """
    JSON 删除线模型
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    strike_text = models.CharField(max_length=200, verbose_name="删除线文本")
    strike_polygon = models.JSONField(verbose_name="删除线文本多边形区域", blank=True, null=True)

    class Meta:
        db_table = table_prefix + "JSON_STText"  # 表名
        verbose_name = "JSON删除线"
        verbose_name_plural = verbose_name