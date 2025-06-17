import hashlib
import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from sma.utils.models import CoreModel, table_prefix, get_custom_app_models, FileModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class IqaDir(CoreModel):
    verification_serial_number = models.TextField(null=True, blank=True, verbose_name="检验流水号")
    rubber_model = models.TextField(null=True, blank=True, verbose_name="胶型号")
    material_number = models.TextField(null=True, blank=True, verbose_name="料号")
    original_rubber_lot = models.TextField(null=True, blank=True, verbose_name="原胶LOT")
    supplier = models.TextField(null=True, blank=True, verbose_name='供应商')
    measurement_count = models.IntegerField(null=True, blank=True, verbose_name="测量次数")
    match_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, null=True, blank=True, verbose_name="匹配率", help_text="IQA匹配率"
    )
    peak_value = models.DecimalField(
        max_digits=10, decimal_places=1, default=0, null=True, blank=True, verbose_name="峰值", help_text="IQA峰值"
    )
    dir_type = models.TextField(null=True, blank=True, verbose_name="目录类型")
    folder_name = models.TextField(null=True, blank=True, verbose_name="文件夹名")
    file_count = models.IntegerField(null=True, blank=True, verbose_name="文件数")
    path = models.TextField(null=True, blank=True, verbose_name='保存路径')
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    class Meta:
        db_table = table_prefix + "IqaDir"
        verbose_name = "IQA目录"
        verbose_name_plural = verbose_name

class IqaFile(CoreModel):
    iqa_dir = models.ForeignKey(IqaDir, related_name="iqafiles", on_delete=models.CASCADE, null=True,
                                           blank=True)
    file_type = models.TextField(null=True, blank=True, verbose_name="文件类型")
    file_name = models.TextField(null=True, blank=True, verbose_name="文件名")
    folder_name = models.TextField(null=True, blank=True, verbose_name="文件夹名")
    path = models.TextField(null=True, blank=True, verbose_name='保存路径')
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    class Meta:
        db_table = table_prefix + "IqaFile"
        verbose_name = "IQA文件"
        verbose_name_plural = verbose_name

class IqaData(CoreModel):
    iqa_file = models.OneToOneField(
        IqaFile,
        related_name="iqadata",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    incoming_date = models.DateTimeField(null=True, verbose_name="Incoming Date", help_text="Incoming Date",
                                               blank=True)
    verification_serial_number = models.TextField(null=True, blank=True, verbose_name="流水号")
    pn = models.TextField(null=True, blank=True, verbose_name="P/N")
    original_rubber_model = models.TextField(null=True, blank=True, verbose_name="原胶型号")
    supplier = models.TextField(null=True, blank=True, verbose_name='供应商')
    original_rubber_dc = models.TextField(null=True, blank=True, verbose_name="原胶DC")
    match_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, null=True, blank=True, verbose_name="匹配率", help_text="IQA匹配率"
    )
    file_name = models.TextField(null=True, blank=True, verbose_name="文件名")
    folder_name = models.TextField(null=True, blank=True, verbose_name="文件夹名")
    path = models.TextField(null=True, blank=True, verbose_name='保存路径')
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    class Meta:
        db_table = table_prefix + "IqaData"
        verbose_name = "IQA总表"
        verbose_name_plural = verbose_name

# class IqaDetailGroup(models.Model):
#     verification_serial_number = models.TextField(null=True, blank=True, verbose_name="检验流水号")
#     rubber_model = models.TextField(null=True, blank=True, verbose_name="胶型号")
#     material_number = models.TextField(null=True, blank=True, verbose_name="料号")
#     original_rubber_lot = models.TextField(null=True, blank=True, verbose_name="原胶LOT")
#     supplier = models.TextField(null=True, blank=True, verbose_name='供应商')
#     measurement_count = models.IntegerField(null=True, blank=True, verbose_name="测量次数")
#
#     class Meta:
#         db_table = table_prefix + "IqaDetailGroup"
#         verbose_name = "IQA峰值总表"
#         verbose_name_plural = verbose_name

class IqaPeakValue(CoreModel):
    # iqa_detail_group = models.ForeignKey(IqaDetailGroup, related_name="peaks", on_delete=models.CASCADE, null=True,
    #                                        blank=True)
    # iqa_file = models.OneToOneField(
    #     IqaFile,
    #     related_name="iqapeak",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True
    # )
    iqa_file = models.ForeignKey(IqaFile, related_name="iqapeakvalues", on_delete=models.CASCADE, null=True,
                                blank=True)
    verification_serial_number = models.TextField(null=True, blank=True, verbose_name="检验流水号")
    rubber_model = models.TextField(null=True, blank=True, verbose_name="胶型号")
    material_number = models.TextField(null=True, blank=True, verbose_name="料号")
    original_rubber_lot = models.TextField(null=True, blank=True, verbose_name="原胶LOT")
    supplier = models.TextField(null=True, blank=True, verbose_name='供应商')
    measurement_count = models.IntegerField(null=True, blank=True, verbose_name="测量次数")
    peak_value = models.DecimalField(
        max_digits=10, decimal_places=1, default=0, null=True, blank=True, verbose_name="峰值", help_text="IQA峰值"
    )
    file_name = models.TextField(null=True, blank=True, verbose_name="文件名")
    folder_name = models.TextField(null=True, blank=True, verbose_name="文件夹名")
    path = models.TextField(null=True, blank=True, verbose_name='保存路径')
    uploader_name = models.CharField(max_length=255, null=True, blank=True, help_text="上传人", verbose_name="上传人")

    class Meta:
        db_table = table_prefix + "IqaPeakValue"
        verbose_name = "IQA峰值"
        verbose_name_plural = verbose_name



