import hashlib
import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from sma.utils.models import CoreModel, table_prefix, get_custom_app_models, FileModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class CSRPdfFile(FileModel):
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

    process = models.CharField(max_length=255, verbose_name="处理过程", help_text="文件处理过程", blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    customer_file_name = models.CharField(max_length=255, verbose_name="客户文件名称", help_text="客户文件名称", blank=True, null=True)
    customer_file_code = models.CharField(max_length=255, verbose_name="客户文件编号", help_text="客户文件编号", blank=True, null=True)
    customer_file_version = models.CharField(max_length=255, verbose_name="客户文件版本", help_text="客户文件版本", blank=True, null=True)
    last_status = models.CharField(max_length=255, verbose_name="最后状态", help_text="最后状态", blank=True, null=True)

    # 统计字段
    total_count = models.IntegerField(null=True, default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(null=True, default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(null=True, default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(null=True, default=0, verbose_name="未通过的子项数量")
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    class Meta:
        db_table = table_prefix + "CSR_PDF"  # 表名
        verbose_name = "PDF文件"
        verbose_name_plural = verbose_name

class CSRJsonFile(FileModel):
    """
    JSON 文件模型
    """
    source_file = models.ForeignKey(CSRPdfFile, related_name="jsonfiles", on_delete=models.CASCADE, null=True, blank=True)
    analyze_version = models.CharField(max_length=255, verbose_name="PDF提取接口版本号", help_text="PDF提取接口版本号", blank=True)
    owner_file = models.CharField(max_length=255, verbose_name="所属文件", help_text="所属文件", blank=True)
    section_cnt = models.IntegerField(null=True, verbose_name="章节数", help_text="章节数", blank=True)
    paragraph_cnt = models.IntegerField(null=True, verbose_name="段落数", help_text="段落数", blank=True)
    table_cnt = models.IntegerField(null=True, verbose_name="表格数", help_text="表格数", blank=True)
    image_cnt = models.IntegerField(null=True, verbose_name="图片数", help_text="图片数", blank=True)

    _reset = False  # 用于判断是否是重置

    class Meta:
        db_table = table_prefix + "CSR_JSON"  # 表名
        verbose_name = "JSON文件"
        verbose_name_plural = verbose_name

class CSRReviewResult(CoreModel):
    """
    检查结果模型
    """
    group = models.ForeignKey(
        'CSRReviewGroup',
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
    meet_req = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="识别特性", help_text="表示是否已识别的特性"
    )
    is_execute = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="是否执行", help_text="是否执行"
    )
    mflex_file = models.TextField(null=True, blank=True, verbose_name="MFLEX内部文件编号")
    remark = models.CharField(max_length=255, verbose_name="描述", help_text="描述", blank=True, null=True)
    process = models.CharField(max_length=255, verbose_name="处理过程", help_text="文件处理过程", blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    customer_file_name = models.CharField(max_length=255, verbose_name="客户文件名称", help_text="客户文件名称",
                                          blank=True, null=True)
    customer_file_code = models.CharField(max_length=255, verbose_name="客户文件编号", help_text="客户文件编号",
                                          blank=True, null=True)
    customer_file_version = models.CharField(max_length=255, verbose_name="客户文件版本", help_text="客户文件版本",
                                             blank=True, null=True)
    last_status = models.CharField(max_length=255, verbose_name="最后状态", help_text="最后状态", blank=True, null=True)
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")
    value = models.TextField(null=True, blank=True, verbose_name="内容")

    class Meta:
        db_table = table_prefix + "CSRREVIEW_RESULT"
        verbose_name = "检查结果"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.feature_name} - {self.status}"

class CSRReviewGroup(CoreModel):
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
        'CSRJsonSection',
        related_name="review_groups",
        through="CSRSectionReviewGroup",
        verbose_name="关联章节"
    )
    paragraphs = models.ManyToManyField(
        'CSRJsonParagraph',
        related_name="review_groups",
        through="CSRParagraphReviewGroup",
        verbose_name="关联段落"
    )
    images = models.ManyToManyField(
        'CSRJsonImage',
        related_name="review_groups",
        through="CSRImageReviewGroup",
        verbose_name="关联图片"
    )
    cells = models.ManyToManyField(
        'CSRJsonTableCell',
        related_name="review_groups",
        through="CSRCellReviewGroup",
        verbose_name="关联单元格"
    )

    review_version = models.ForeignKey(
        'CSRReviewVersion',
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

    process = models.CharField(max_length=255, verbose_name="处理过程", help_text="文件处理过程", blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    customer_file_name = models.CharField(max_length=255, verbose_name="客户文件名称", help_text="客户文件名称",
                                          blank=True, null=True)
    customer_file_code = models.CharField(max_length=255, verbose_name="客户文件编号", help_text="客户文件编号",
                                          blank=True, null=True)
    customer_file_version = models.CharField(max_length=255, verbose_name="客户文件版本", help_text="客户文件版本",
                                             blank=True, null=True)
    last_status = models.CharField(max_length=255, verbose_name="最后状态", help_text="最后状态", blank=True, null=True)
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")
    value = models.TextField(null=True, blank=True, verbose_name="内容")

    class Meta:
        db_table = table_prefix + "CSRREVIEW_GROUP"
        verbose_name = "检查结果组"
        verbose_name_plural = verbose_name

class CSRSectionReviewGroup(models.Model):
    review_group = models.ForeignKey(CSRReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    section = models.ForeignKey('CSRJsonSection', on_delete=models.CASCADE, verbose_name="章节")

    class Meta:
        db_table = table_prefix + "CSRSectionReviewGroup"
        verbose_name = "章节关联表"
        verbose_name_plural = verbose_name


class CSRParagraphReviewGroup(models.Model):
    review_group = models.ForeignKey(CSRReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    paragraph = models.ForeignKey('CSRJsonParagraph', on_delete=models.CASCADE, verbose_name="段落")

    class Meta:
        db_table = table_prefix + "CSRParagraphReviewGroup"
        verbose_name = "段落关联表"
        verbose_name_plural = verbose_name


class CSRImageReviewGroup(models.Model):
    review_group = models.ForeignKey(CSRReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    image = models.ForeignKey('CSRJsonImage', on_delete=models.CASCADE, verbose_name="图片")

    class Meta:
        db_table = table_prefix + "CSRImageReviewGroup"
        verbose_name = "图片关联表"
        verbose_name_plural = verbose_name


class CSRCellReviewGroup(models.Model):
    review_group = models.ForeignKey(CSRReviewGroup, on_delete=models.CASCADE, verbose_name="检查结果组")
    cell = models.ForeignKey('CSRJsonTableCell', on_delete=models.CASCADE, verbose_name="单元格")

    class Meta:
        db_table = table_prefix + "CSRCellReviewGroup"
        verbose_name = "单元格关联表"
        verbose_name_plural = verbose_name



class CSRReviewVersion(CoreModel):
    """
    审核版本模型
    """
    # 与 JsonFile 的多对一关系
    jsonfile = models.ForeignKey(
        'CSRJsonFile',
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
    process = models.CharField(max_length=255, verbose_name="处理过程", help_text="文件处理过程", blank=True, null=True)
    customer = models.CharField(max_length=255, verbose_name="客户", help_text="文件对应的客户", blank=True, null=True)
    customer_file_name = models.CharField(max_length=255, verbose_name="客户文件名称", help_text="客户文件名称",
                                          blank=True, null=True)
    customer_file_code = models.CharField(max_length=255, verbose_name="客户文件编号", help_text="客户文件编号",
                                          blank=True, null=True)
    customer_file_version = models.CharField(max_length=255, verbose_name="客户文件版本", help_text="客户文件版本",
                                             blank=True, null=True)
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    last_status = models.CharField(max_length=255, verbose_name="最后状态", help_text="最后状态", blank=True, null=True)

    class Meta:
        db_table = table_prefix + "CSRREVIEW_VERSION"  # 表名
        verbose_name = "审核版本"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"ReviewVersion (JSON File ID: {self.jsonfile.id}, Status: {self.status})"


class CSRJsonSection(CoreModel):
    """
    JSON 章节模型
    """
    recognition_result = models.ForeignKey(CSRJsonFile, related_name="sections", on_delete=models.CASCADE, null=True, blank=True)
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

    class Meta:
        db_table = table_prefix + "CSRJSON_SECTION"  # 表名
        verbose_name = "JSON章节"
        verbose_name_plural = verbose_name


class CSRJsonContent(CoreModel):
    """
    JSON 内容模型
    """
    section = models.ForeignKey(CSRJsonSection, related_name="contents", on_delete=models.CASCADE, null=True, blank=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_content = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内content顺序", help_text="块内content顺序")
    polygon = models.JSONField(verbose_name="多边形区域", blank=True, null=True)

    # 统计字段
    total_count = models.IntegerField(default=0, verbose_name="总子项数量")
    unchecked_count = models.IntegerField(default=0, verbose_name="未校验子项数量")
    passed_count = models.IntegerField(default=0, verbose_name="通过的子项数量")
    failed_count = models.IntegerField(default=0, verbose_name="未通过的子项数量")

    class Meta:
        db_table = table_prefix + "CSRJSON_CONTENT"  # 表名
        verbose_name = "JSON内容"
        verbose_name_plural = verbose_name

class CSRJsonParagraph(CoreModel):
    """
    JSON 段落模型
    """
    content = models.ForeignKey(CSRJsonContent, related_name="paragraphs", on_delete=models.CASCADE, null=True, blank=True)
    page = models.IntegerField(default=0, null=True, blank=True, verbose_name="页码", help_text="页码")
    value = models.TextField(null=True, blank=True, verbose_name="段落内容")
    ch_value = models.TextField(null=True, blank=True, verbose_name="段落中文内容")
    thai_value = models.TextField(null=True, blank=True, verbose_name="段落泰文")
    polygon = models.JSONField(verbose_name="段落多边形区域", blank=True, null=True)
    order_in_file = models.IntegerField(default=0, null=True, blank=True, verbose_name="全局顺序", help_text="全局顺序")
    order_of_element  = models.IntegerField(default=0, null=True, blank=True, verbose_name="块内元素顺序", help_text="块内元素顺序")
    has_strike_through = models.BooleanField(default=0, verbose_name='是否有划去线', help_text="用于判断是否需处理划去线", blank=True)
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

    class Meta:
        db_table = table_prefix + "CSRJSON_PARAGRAPH"  # 表名
        verbose_name = "JSON段落"
        verbose_name_plural = verbose_name


class CSRJsonTable(CoreModel):
    """
    JSON 表格模型
    """
    content = models.ForeignKey(CSRJsonContent, related_name="tables", on_delete=models.CASCADE, null=True, blank=True)
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

    class Meta:
        db_table = table_prefix + "CSRJSON_TABLE"  # 表名
        verbose_name = "JSON表格"
        verbose_name_plural = verbose_name

class CSRJsonImage(CoreModel):
    """
    JSON 图片模型
    """
    content = models.ForeignKey(CSRJsonContent, related_name="images", on_delete=models.CASCADE, null=True, blank=True)
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

    class Meta:
        db_table = table_prefix + "CSRJSON_IMAGE"  # 表名
        verbose_name = "JSON图片"
        verbose_name_plural = verbose_name

class CSRJsonTableCell(CoreModel):
    """
    JSON 表格单元格模型
    """
    table = models.ForeignKey(CSRJsonTable, related_name="cells", on_delete=models.CASCADE, null=True, blank=True)
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

    class Meta:
        db_table = table_prefix + "CSRJSON_TABLECELL"  # 表名
        verbose_name = "JSON表格单元格"
        verbose_name_plural = verbose_name


class CSRImageFile(FileModel):
    """
    图片文件模型
    """
    image_file = models.ForeignKey(CSRJsonImage, related_name="json_images", on_delete=models.CASCADE, null=True, blank=True)
    resolution = models.CharField(max_length=50, verbose_name="分辨率", help_text="图片文件的分辨率", null=True, blank=True)
    format = models.CharField(max_length=10, verbose_name="图片格式", help_text="图片格式", null=True, blank=True)  # 如 jpg, png
    image_length = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="图片长度", help_text="图片长度")
    image_width = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="图片宽度", help_text="图片宽度")
    owner_file = models.CharField(max_length=255, verbose_name="所属文件", help_text="所属文件", blank=True)
    owner_file_type = models.CharField(max_length=10, verbose_name="图片所属内容类型", help_text="图片所属内容类型", null=True, blank=True)
    owner_file_page = models.IntegerField(null=True, default=0, verbose_name="所在页码", help_text="所在页码", blank=True)

    class Meta:
        db_table = table_prefix + "CSRFILE_IMAGE"  # 表名
        verbose_name = "图片文件"
        verbose_name_plural = verbose_name


class CSRJsonXBar(CoreModel):
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
        db_table = table_prefix + "CSRJSON_XBar"  # 表名
        verbose_name = "JSONXBar"
        verbose_name_plural = verbose_name


class CSRJsonStrikeThroughText(CoreModel):
    """
    JSON 删除线模型
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    strike_text = models.CharField(max_length=200, verbose_name="删除线文本")
    strike_polygon = models.JSONField(verbose_name="删除线文本多边形区域", blank=True, null=True)

    class Meta:
        db_table = table_prefix + "CSRJSON_STText"  # 表名
        verbose_name = "JSON删除线"
        verbose_name_plural = verbose_name