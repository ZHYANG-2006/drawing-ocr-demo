import os
import cx_Oracle

from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework import serializers
from rest_framework.decorators import action

from application import settings
from sma.system.models import ReviewVersion
from sma.system.models.cppqcp import PdfFile, ReviewResult, ReviewGroup
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet

from conf.env import *

class ReviewResultSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = ReviewResult
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

class ReviewResultViewSet(CustomModelViewSet):
    """
    PdfFile 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = PdfFile.objects.all()
    serializer_class = ReviewResultSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = ReviewResultSerializer
    update_serializer_class = ReviewResultSerializer

    # 定义过滤、搜索和排序字段
    # filter_fields = ['name', 'process', 'is_analyzed', 'has_expired']  # 支持的过滤字段
    search_fields = [
        'name',
        'process',
        'flow_name',
        'customer',
        'file_type',
        'pfmea_type',
        'is_universal',
        'material_number',
        'type'
        'lob',
        'file_name',
        'modifier_name',
        'status',
        'has_pfmea',
        'pfmea_time_after',
        'pfmea_time_before',
        'update_datetime_after',
        'update_datetime_before'
        'uploader_name',
    ];

    ordering_fields = [
        'create_datetime',
        'update_datetime',
        'progress',
        'material_number',
        'file_name',
        'pfmea_type',
        'status',
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
        upload_dir = settings.PATH_PDF_CPPQCP
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
        data['business_type'] = "CPP&QCP"
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
            group = ReviewGroup.objects.get(id=group_id)  # 查找 ReviewGroup
        except ReviewGroup.DoesNotExist:
            return ErrorResponse(msg=f"ReviewGroup ID {group_id} 不存在")

        # 获取该 ReviewGroup 关联的所有 ReviewResult
        review_results = ReviewResult.objects.filter(group=group).order_by('-create_datetime')

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
        reviewVersion = ReviewVersion.objects.get(id=reviewVersion_id)
        review_data = request.data.get('record')
        group_id = request.data.get('record').get('group')
        if group_id:
            group = ReviewGroup.objects.get(id=group_id)
        # 如果传递了 review_id，尝试查找对应的 ReviewResult，否则创建一个新的
        with transaction.atomic():
            if review_id:
                try:
                    review_result = ReviewResult.objects.get(id=review_id)
                except ReviewResult.DoesNotExist:
                    return ErrorResponse(msg=f"ReviewResult ID {review_id} 不存在")

                # 更新 ReviewResult 记录
                review_result.name = review_data.get('name', review_result.name)
                review_result.feature_recognized = review_data.get('feature_recognized', review_result.feature_recognized)
                review_result.plm_standard_process = review_data.get('plm_standard_process', review_result.plm_standard_process)
                review_result.plm_device_type = review_data.get('plm_device_type', review_result.plm_device_type)
                review_result.plm_procedure = review_data.get('plm_procedure', review_result.plm_procedure)
                review_result.function22 = review_data.get('function22', review_result.function22)
                review_result.function23 = review_data.get('function23', review_result.function23)
                review_result.feature_category = review_data.get('feature_category', review_result.feature_category)
                review_result.checkCategory = review_data.get('checkCategory', review_result.checkCategory)
                review_result.checkedQuest = review_data.get('checkedQuest', review_result.checkedQuest)
                review_result.checkRule = review_data.get('checkRule', review_result.checkRule)
                review_result.limitType = review_data.get('limitType', review_result.limitType)
                review_result.standardValue = review_data.get('standardValue', review_result.standardValue)
                review_result.limitUp = review_data.get('limitUp', review_result.limitUp)
                review_result.containLimitUp = review_data.get('containLimitUp', review_result.containLimitUp)
                review_result.limitDown = review_data.get('limitDown', review_result.limitDown)
                review_result.containLimitDown = review_data.get('containLimitDown', review_result.containLimitDown)
                review_result.unitCode = review_data.get('unitCode', review_result.unitCode)
                review_result.evaluation_measurement = review_data.get('evaluation_measurement', review_result.evaluation_measurement)
                review_result.capacity = review_data.get('capacity', review_result.capacity)
                review_result.frequency = review_data.get('frequency', review_result.frequency)
                review_result.control_method = review_data.get('control_method', review_result.control_method)
                review_result.action = review_data.get('action', review_result.action)
                review_result.responsibility = review_data.get('responsibility', review_result.responsibility)
                review_result.last_status = review_data.get('last_status', review_result.last_status)
                review_result.uploader_name = reviewVersion.uploader_name
                review_result.value = group.value
                review_result.save()
            else:
                # 如果没有 review_id，创建新的 ReviewResult
                data = review_data.copy()  # 复制数据以便修改
                data['name'] = reviewVersion.file_name
                data['process'] = reviewVersion.process
                data['file_type'] = reviewVersion.file_type
                data['is_universal'] = reviewVersion.is_universal
                data['customer'] = reviewVersion.customer
                data['material_number'] = reviewVersion.material_number
                data['lob'] = reviewVersion.lob
                data['type'] = reviewVersion.type
                data['pfmea_type'] = reviewVersion.pfmea_type
                data['group'] = group.id
                data['branch'] = reviewVersion.branch
                data['uploader_name'] = reviewVersion.uploader_name
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                new_review_result = serializer.save()  # 保存新记录
            if group:
                # Fetch all related ReviewResults for the group
                related_review_results = ReviewResult.objects.filter(group=group)

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

    @action(detail=False, methods=['get'])
    def getplm(self, request, *args, **kwargs):
        dsn = cx_Oracle.makedsn(
            PLM_HOST_TEST,  # 获取主机名或使用默认值
            1521,  # 获取端口号或使用默认值
            service_name=PLM_NAME_TEST  # 使用 service_name
        )
        connection = cx_Oracle.connect(
            user=PLM_USER_TEST,
            password=PLM_PASSWORD_TEST,
            dsn=dsn
        )

        try:
            cursor = connection.cursor()
            query = """
                    SELECT DISTINCT 
                       TRIM(REPLACE(OPCODE, CHR(49824), ' ')) AS OPCODE, 
                       TRIM(REPLACE(DEVICETYPE, CHR(49824), ' ')) AS DEVICETYPE
                    FROM TBLOP
                    WHERE EATTRIBUTE2 = 'PLM'
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            options = [{"value": row[0], "type": row[1]} for row in rows]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        return SuccessResponse(options, msg="查询成功")

    @action(detail=False, methods=['get'])
    def getcheckitem(self, request, *args, **kwargs):
        dsn = cx_Oracle.makedsn(
            PLM_HOST_TEST,  # 获取主机名或使用默认值
            1521,  # 获取端口号或使用默认值
            service_name=PLM_NAME_TEST  # 使用 service_name
        )
        connection = cx_Oracle.connect(
            user=PLM_USER_TEST,
            password=PLM_PASSWORD_TEST,
            dsn=dsn
        )

        try:
            cursor = connection.cursor()
            query = """
                    select CHECKEDITEM , EATTRIBUTE7,  CHECKRULE, UNIT, CHECKCRITERIONID, CHECKCATEGORY from tblqccheckcriterion
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            options = [{"checkedQuest": row[0], "checkRule": row[2], "limitType": row[1], "unitCode": row[3], "ID": row[4], "checkCategory": row[5]} for row in rows]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        return SuccessResponse(options, msg="查询成功")

    def destroy(self, request, *args, **kwargs):
        """
        自定义删除逻辑：删除文件和数据库记录
        """
        pk = kwargs.get('pk')  # 从 kwargs 获取主键 (pk)

        try:
            # 获取要删除的 ReviewResult 对象
            instance = ReviewResult.objects.get(pk=pk)
            group = instance.group

            # 删除数据库记录
            instance.delete()
            if group:
                # Fetch all related ReviewResults for the group
                related_review_results = ReviewResult.objects.filter(group=group)
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
        except ReviewResult.DoesNotExist:
            return ErrorResponse(msg=f"ReviewResult with pk {pk} does not exist")