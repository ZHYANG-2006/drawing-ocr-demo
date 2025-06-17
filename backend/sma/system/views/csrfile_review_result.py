import os
import cx_Oracle

from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework import serializers
from rest_framework.decorators import action

from application import settings
from sma.system.models import CSRReviewVersion
from sma.system.models.csrfile import CSRPdfFile, CSRReviewResult, CSRReviewGroup
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet

from conf.env import *

class CSRReviewResultSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = CSRReviewResult
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

class CSRReviewResultViewSet(CustomModelViewSet):
    """
    PdfFile 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = CSRPdfFile.objects.all()
    serializer_class = CSRReviewResultSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = CSRReviewResultSerializer
    update_serializer_class = CSRReviewResultSerializer

    # 定义过滤、搜索和排序字段
    # filter_fields = ['name', 'process', 'is_analyzed', 'has_expired']  # 支持的过滤字段
    search_fields = [
        'process',
        'customer',
        'customer_file_name',
        'customer_file_code',
        'customer_file_version',
        'last_status',
        'status',
        'update_datetime_after',
        'update_datetime_before'
        'uploader_name',
    ];

    ordering_fields = [
        'process',
        'customer',
        'customer_file_name',
        'customer_file_code',
        'customer_file_version',
        'last_status',
        'status'
        'modifier_name',
        'uploader_name',
    ];

    def create(self, request, *args, **kwargs):
        """
        自定义创建逻辑
        """
        file = request.FILES.get('file')  # 获取上传的文件
        if not file:
            return ErrorResponse(msg='请上传文件')

        # 指定存储路径
        upload_dir = settings.PATH_PDF_CSRFILE
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.name)

        # 检查文件是否已存在
        if default_storage.exists(file_path):
            return ErrorResponse(msg=f"文件 {file.name} 已存在，无法上传")

        # 保存文件到指定路径
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 去掉文件后缀
        file_name, file_extension = os.path.splitext(file.name)

        # 创建 PdfFile 数据
        data = request.data.copy()  # 转为可变字典
        data['name'] = file_name  # 去掉后缀的文件名
        data['file_path'] = file_path  # 保存文件路径到模型字段
        data['business_type'] = "CSRFILE"
        data['file_extension'] = file_extension  # 文件后缀类型

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        pdf_file = serializer.save()  # 保存数据库记录

        return SuccessResponse(data=serializer.data, msg="文件上传成功")

    def list(self, request, *args, **kwargs):
        """
        根据传递的 ReviewGroup ID 获取该组关联的所有 ReviewResult 记录
        """
        group_id = request.query_params.get('id')  # 获取请求中的 group_id 参数
        if not group_id:
            return ErrorResponse(msg="请提供 ReviewGroup 的 ID")

        try:
            group = CSRReviewGroup.objects.get(id=group_id)  # 查找 ReviewGroup
        except CSRReviewGroup.DoesNotExist:
            return ErrorResponse(msg=f"ReviewGroup ID {group_id} 不存在")

        # 获取该 ReviewGroup 关联的所有 ReviewResult
        review_results = CSRReviewResult.objects.filter(group=group).order_by('-create_datetime')

        # 序列化结果
        serializer = self.get_serializer(review_results, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    @action(detail=False, methods=['post'])
    def savereview(self, request, *args, **kwargs):
        """
        保存或更新 ReviewResult，判断是否有 id 来决定是创建还是更新
        """
        review_id = request.data.get('record').get('id')  # 获取传递的 ReviewResult ID
        reviewVersion_id = request.data.get('versionId')
        reviewVersion = CSRReviewVersion.objects.get(id=reviewVersion_id)
        review_data = request.data.get('record')
        group_id = request.data.get('record').get('group')
        if group_id:
            group = CSRReviewGroup.objects.get(id=group_id)
        # 如果传递了 review_id，尝试查找对应的 ReviewResult，否则创建一个新的
        with transaction.atomic():
            if review_id:
                try:
                    review_result = CSRReviewResult.objects.get(id=review_id)
                except CSRReviewResult.DoesNotExist:
                    return ErrorResponse(msg=f"ReviewResult ID {review_id} 不存在")
                # 更新 ReviewResult 记录
                review_result.meet_req = review_data.get('meet_req', review_result.meet_req)
                review_result.is_execute = review_data.get('is_execute', review_result.is_execute)
                review_result.mflex_file = review_data.get('mflex_file', review_result.mflex_file)
                review_result.remark = review_data.get('remark', review_result.remark)
                review_result.last_status = review_data.get('last_status', review_result.last_status)
                review_result.uploader_name = reviewVersion.uploader_name
                review_result.value = group.value
                review_result.save()
            else:
                # 如果没有 review_id，创建新的 ReviewResult
                data = review_data.copy()  # 复制数据以便修改
                data['process'] = reviewVersion.process
                data['customer'] = reviewVersion.customer
                data['customer_file_name'] = reviewVersion.customer_file_name
                data['customer_file_code'] = reviewVersion.customer_file_code
                data['customer_file_version'] = reviewVersion.customer_file_version
                data['last_status'] = reviewVersion.last_status
                data['uploader_name'] = reviewVersion.uploader_name
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                new_review_result = serializer.save()  # 保存新记录
            if group:
                # Fetch all related ReviewResults for the group
                related_review_results = CSRReviewResult.objects.filter(group=group)

                if related_review_results.exists():
                    any_error = related_review_results.filter(last_status='ERROR').exists()
                    all_success = related_review_results.filter(
                        last_status='SUCCESS').count() == related_review_results.count()

                    if any_error:
                        group.last_status = 'ERROR'
                        reviewVersion.last_status = 'ERROR'
                    elif all_success:
                        group.last_status = 'SUCCESS'
                    else:
                        group.last_status = 'ERROR'
                    group.save()
                    reviewVersion.save()
                else:
                    # No related ReviewResults
                    group.last_status = 'EMPTY'
                    reviewVersion.last_status = 'EMPTY'
                    group.save()
                    reviewVersion.save()
            return SuccessResponse(data=[], msg="ReviewResult 创建成功")

    def destroy(self, request, *args, **kwargs):
        """
        自定义删除逻辑：删除文件和数据库记录
        """
        pk = kwargs.get('pk')  # 从 kwargs 获取主键 (pk)

        try:
            # 获取要删除的 ReviewResult 对象
            instance = CSRReviewResult.objects.get(pk=pk)
            group = instance.group

            # 删除数据库记录
            instance.delete()
            if group:
                # Fetch all related ReviewResults for the group
                related_review_results = CSRReviewResult.objects.filter(group=group)
                if related_review_results.exists():
                    any_error = related_review_results.filter(last_status='ERROR').exists()
                    all_success = related_review_results.filter(
                        last_status='SUCCESS').count() == related_review_results.count()
                    if any_error:
                        group.last_status = 'ERROR'
                    elif all_success:
                        group.last_status = 'SUCCESS'
                    else:
                        group.last_status = 'ERROR'
                    group.save()
                else:
                    # No related ReviewResults
                    group.last_status = 'EMPTY'
                    group.save()
            return SuccessResponse(data=[], msg="删除成功")
        except CSRReviewResult.DoesNotExist:
            return ErrorResponse(msg=f"ReviewResult with pk {pk} does not exist")