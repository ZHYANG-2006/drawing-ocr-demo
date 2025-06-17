import os

from django_celery_beat.models import PeriodicTask
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.decorators import action
from django.http import FileResponse
from application import settings
from sma.system.models.mco import MonitorConfig
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet
from django.http import JsonResponse
from sma.system.views.mco_cmp_tasks import compare_pdfs_task, compare_pdf
from sma.system.models.mco import MCOPdfFile
from celery.result import AsyncResult

class MonitorConfigSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = MonitorConfig
        fields = '__all__'  # 序列化所有字段

class MonitorViewSet(CustomModelViewSet):
    """
    目录监控配置的增删改查
    """
    queryset = MonitorConfig.objects.all()
    serializer_class = MonitorConfigSerializer
    create_serializer_class = MonitorConfigSerializer
    update_serializer_class = MonitorConfigSerializer

    def list(self, request, *args, **kwargs):
        # 1. 过滤 & 排序
        qs = self.filter_queryset(self.get_queryset())

        # 2. DRF 分页
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            # paginator.page.paginator.count 是总条数
            total = self.paginator.page.paginator.count
            return SuccessResponse(
                data={'results': ser.data, 'count': total},
                msg="获取成功"
            )

        # 3. 不分页，直接返回全部
        ser = self.get_serializer(qs, many=True)
        return SuccessResponse(
            data={'results': ser.data, 'count': len(ser.data)},
            msg="获取成功"
        )

    def create(self, request, *args, **kwargs):
        # 新增一条 MonitorConfig
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        inst = ser.save()
        return SuccessResponse(data=ser.data, msg="创建成功")

    def update(self, request, *args, **kwargs):
        # 部分更新和整体更新都走这里
        partial = kwargs.pop('partial', False)
        inst = self.get_object()
        ser = self.get_serializer(inst, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        return SuccessResponse(data=ser.data, msg="更新成功")

    def destroy(self, request, *args, **kwargs):
        inst = self.get_object()
        inst.delete()
        return SuccessResponse(data=None, msg="删除成功")

    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """
        可选：手动触发一次立即扫描，
        比如 /api/monitor-config/{pk}/run_now/
        """
        cfg = self.get_object()
        # 触发 celery 任务，假设任务名 scan_new_pdfs 接收目录路径
        task = PeriodicTask.objects.filter(name=f"ScanPDFs::{cfg.pk}").first()
        # 也可直接调用 scan_new_pdfs.delay(cfg.directory_path)
        if task:
            task.run()
        return SuccessResponse(data=None, msg="已触发扫描")