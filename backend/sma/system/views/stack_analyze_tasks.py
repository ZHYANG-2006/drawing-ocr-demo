import base64
import socket

from django.http import JsonResponse
from django.db.models import F
import os
import json
import requests
from django.utils import timezone
from django.db.models import Max
from django.conf import settings
from datetime import datetime

from plotly.offline.offline import build_save_image_post_script
from rest_framework.decorators import action
from rest_framework import serializers
from sma.system.models import JsonTableCell
from sma.system.models.stack import STACKPdfFile
import threading
from .stack_tasks import task_queue
from sma.utils.json_response import SuccessResponse, ErrorResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet

class STACKFileSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = STACKPdfFile
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

    # 如果需要额外处理某些字段，可以通过自定义方法处理
    def validate_progress(self, value):
        """
        自定义验证方法：确保进度值在 0 到 100 之间
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError("进度必须在 0 到 100 之间")
        return value

    def to_representation(self, instance):
        """
        自定义返回格式：在返回 JSON 时添加额外字段
        """
        representation = super().to_representation(instance)
        representation['is_analyzed_display'] = "已分析" if instance.is_analyzed else "未分析"
        return representation
# # 全局解析锁
# parse_lock = threading.Lock()
class STACKTaskViewSet(CustomModelViewSet):
    queryset = STACKPdfFile.objects.all()
    serializer_class = STACKFileSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = STACKFileSerializer
    update_serializer_class = STACKFileSerializer

    # 定义过滤、搜索和排序字段
    filter_fields = ['name', 'is_analyzed', 'has_expired']  # 支持的过滤字段
    search_fields = ['name', 'flow_name', 'customer']  # 支持的搜索字段
    ordering_fields = ['create_datetime', 'update_datetime', 'progress']  # 支持排序的字段

    def decode_image(self, image_bytes):
        """
        将 Base64 编码的 PNG 或 JPEG 数据解码为二进制流。
        如果 image_bytes 为空，则返回 None。
        """
        if not image_bytes:
            return None
        try:
            return base64.b64decode(image_bytes)
        except Exception as e:
            raise ValueError(f"Failed to decode image bytes: {e}")

    @action(methods=["GET"], detail=False)
    def schedule_parse(self, request):
        """
        将指定文件加入解析队列。由后台线程 parse_worker 顺序执行解析。
        """
        version_str = "0.0.0"
        server_ip = socket.gethostbyname(socket.gethostname())
        # 根据服务器前缀获取版本信息（可选）
        if server_ip.startswith("172.30"):
            # response_v = requests.get("http://172.16.94.134:5020/")
            # response_v_data = response_v.json()
            # version_str = response_v_data
            version_str = "0.0.0"
        else:
            # mock
            url_version = "http://localhost:7007/plugins/mock/version/"
            response_v = requests.get(url_version)
            version_str = response_v.json().get("version")

        file_id = request.GET.get("id")
        if not file_id:
            return ErrorResponse(msg='文件 ID 缺失')

        try:
            pdf_file = STACKPdfFile.objects.get(id=file_id)
        except STACKPdfFile.DoesNotExist:
            return ErrorResponse(msg='文件不存在')

        # 如果已经解析过最新版本则直接返回
        # if pdf_file.queue_order == 0 and pdf_file.analyze_version == version_str:
        if pdf_file.queue_order == 0:
            return SuccessResponse(data=[], msg="已存在最新版本的解析，无需重新解析")

        # 设置排队顺序 (queue_order)
        # 如果有正在解析的，自己排在后面，否则直接置为1
        if STACKPdfFile.objects.filter(queue_order=1).exists():
            max_queue_order = STACKPdfFile.objects.aggregate(max_order=Max('queue_order'))['max_order'] or 1
            pdf_file.queue_order = max_queue_order + 1
        else:
            pdf_file.queue_order = 1
        pdf_file.start_analyze_time = timezone.now()
        pdf_file.analyze_version = version_str
        pdf_file.save()

        # 将任务（文件ID）放入队列
        task_queue.put(pdf_file.id)

        return SuccessResponse(data=[], msg=f"文件已加入解析队列，队列位置 {pdf_file.queue_order}")

