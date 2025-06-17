import os

from django.core.files.storage import default_storage
from openpyxl.worksheet import page
from rest_framework import serializers
from rest_framework.decorators import action
from django.http import FileResponse
from application import settings
from sma.system.models.stack import Material, STACKJsonFile, STACKJsonContent, STACKJsonTable, STACKJsonTableCell
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet
from sma.system.views.user import UserSerializer

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        # 你需要返回哪些字段就写哪些
        fields = '__all__'


class STACKMaterialViewSet(CustomModelViewSet):
    creator = UserSerializer(many=True, read_only=True)
    """
        PdfFile 的视图集
        继承自 CustomModelViewSet，支持批量删除、过滤查询等
        """
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = MaterialSerializer
    update_serializer_class = MaterialSerializer

    # 定义过滤、搜索和排序字段
    search_fields = [
        'number',
        'name',
        'creator_name',
        'create_datetime',
        'creator',
        'uploader_name',
    ]

    ordering_fields = [
        'number',
        'name',
        'creator_name',
        'create_datetime',
        'creator',
        'uploader_name',
    ]

    def create(self, request, *args, **kwargs):
        """
        自定义创建逻辑
        """
        # 创建 PdfFile 数据
        data = request.data.dict()  # 转为可变字典
        # data['name'] = file_name  # 去掉后缀的文件名
        # data['file_path'] = file_path  # 保存文件路径到模型字段
        # data['business_type'] = "STACK"
        # data['file_extension'] = file_extension  # 文件后缀类型
        # data['uploader_name'] = request.user.name

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        material = serializer.save()  # 保存数据库记录

        return SuccessResponse(data=serializer.data, msg="新建成功")

    def list(self, request, *args, **kwargs):
        """
        重写list方法
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset()).order_by('name').order_by('-create_datetime')
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return SuccessResponse(serializer.data, msg="获取成功")

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
            instance = Material.objects.get(pk=pk)
            # 删除数据库记录
            instance.delete()
            return SuccessResponse(data=[], msg="删除成功")
        except Material.DoesNotExist:
            return ErrorResponse(msg=f"ReviewResult with pk {pk} does not exist")
