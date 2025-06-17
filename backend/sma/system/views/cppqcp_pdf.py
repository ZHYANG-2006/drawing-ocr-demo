import os

from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.decorators import action

from application import settings
from sma.system.models import JsonFile
from sma.system.models.cppqcp import PdfFile
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet

class PdfFileSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = PdfFile
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

class PdfFileViewSet(CustomModelViewSet):
    """
    PdfFile 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = PdfFile.objects.all()
    serializer_class = PdfFileSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = PdfFileSerializer
    update_serializer_class = PdfFileSerializer

    # 定义过滤、搜索和排序字段
    search_fields = [
        'process',
        'file_type',
        'customer',
        'is_universal',
        'name',
        'flow_name',
        'material_number',
        'type',
        'lob',
        'pfmea_type',
        'branch',
        'queue_order',
        'analyze_version',
        'start_analyze_time',
        'finish_analyze_time',
        'has_expired',
        'creator_name',
        'create_datetime',
        'creator_name',
        'creator',
        'uploader_name',
    ]

    ordering_fields = [
        'process',
        'create_datetime',
        'update_datetime',
        'progress',
        'material_number',
        'lob',
        'type',
        'pfmea_type',
        'branch',
        'queue_order',
        'analyze_version',
        'start_analyze_time',
        'finish_analyze_time',
        'has_expired',
        'creator_name',
        'creator',
        'uploader_name',
    ]

    def create(self, request, *args, **kwargs):
        """
        自定义创建逻辑
        """
        file = request.FILES.get('file')  # 获取上传的文件
        if not file:
            return ErrorResponse(msg='请上传文件')

        # 指定存储路径
        upload_dir = settings.PATH_PDF_CPPQCP
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.name)

        # 检查文件是否已存在
        # if default_storage.exists(file_path):
        #     return ErrorResponse(msg=f"文件 {file.name} 已存在，无法上传")

        # 保存文件到指定路径
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 去掉文件后缀
        file_name, file_extension = os.path.splitext(file.name)

        # 创建 PdfFile 数据
        data = request.data.dict()  # 转为可变字典
        data['name'] = file_name  # 去掉后缀的文件名
        data['file_path'] = file_path  # 保存文件路径到模型字段
        data['business_type'] = "CPP&QCP"
        data['file_extension'] = file_extension  # 文件后缀类型
        data['uploader_name'] = request.user.name

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        pdf_file = serializer.save()  # 保存数据库记录

        return SuccessResponse(data=serializer.data, msg="文件上传成功")

    def list(self, request, *args, **kwargs):
        """
        重写list方法
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset()).order_by('name').order_by('-create_datetime')
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(serializer.data,msg="获取成功")


    # 额外的业务逻辑接口
    @action(detail=True, methods=['post'])
    def reset_analysis(self, request, pk=None):
        """
        自定义接口：重置文件的分析状态
        """
        pdf_file = self.get_object()
        pdf_file.is_analyzed = False
        pdf_file.progress = 0
        pdf_file.save(update_fields=['is_analyzed', 'progress'])
        return DetailResponse(data={'id': pdf_file.id, 'message': '分析状态已重置'})

    @action(detail=False, methods=['get'])
    def recent_files(self, request):
        """
        自定义接口：获取最近上传的文件
        """
        recent_files = self.queryset.order_by('-create_datetime')[:10]  # 取最近 10 条
        serializer = self.get_serializer(recent_files, many=True)
        return SuccessResponse(data=serializer.data, msg="最近的文件列表获取成功")

    def destroy(self, request, *args, **kwargs):
        """
        自定义删除逻辑：删除文件和数据库记录
        """
        pk = kwargs.get('pk')  # 从 kwargs 获取主键 (pk)

        try:
            # 获取要删除的 ReviewResult 对象
            instance = PdfFile.objects.get(pk=pk)
            # 删除数据库记录
            instance.delete()
            return SuccessResponse(data=[], msg="删除成功")
        except PdfFile.DoesNotExist:
            return ErrorResponse(msg=f"ReviewResult with pk {pk} does not exist")