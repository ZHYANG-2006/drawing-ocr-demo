import os

from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.decorators import action
from django.http import FileResponse
from application import settings
from sma.system.models.mco import MCOCMPDiff, MCOCMPPair, MCOJsonParagraph
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet
from django.http import JsonResponse
from sma.system.views.mco_cmp_tasks import compare_pdfs_task, compare_pdf
from sma.system.models.mco import MCOPdfFile
from celery.result import AsyncResult

class MCOCMPPairSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = MCOCMPPair
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

class MCOCMPPairViewSet(CustomModelViewSet):
    """
    PdfFile 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = MCOCMPPair.objects.all()
    serializer_class = MCOCMPPairSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = MCOCMPPairSerializer
    update_serializer_class = MCOCMPPairSerializer

    # 定义过滤、搜索和排序字段
    search_fields = [
        'creator_name',
        'create_datetime',
        'creator_name',
        'creator',
        'uploader_name',
    ]

    ordering_fields = [
        'creator_name',
        'create_datetime',
        'creator_name',
        'creator',
        'uploader_name',
    ]

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


    @action(detail=False, methods=['get'])
    def recent_files(self, request):
        """
        自定义接口：获取最近上传的文件
        """
        recent_files = self.queryset.order_by('-create_datetime')[:10]  # 取最近 10 条
        serializer = self.get_serializer(recent_files, many=True)
        return SuccessResponse(data=serializer.data, msg="最近的文件列表获取成功")

    @action(detail=False, methods=['post'])
    def compare_pdfs_view(self, request):
        if request.method == "POST":
            # 前端发来的数据, 比如 JSON 格式：包含 old_file_path, new_file_path, old_paragraphs, new_paragraphs
            data = request.data # 或者 request.body decode后, request.JSON等
            payload = data.get('payload')
            new_drawing = payload.get("new_drawing")
            old_drawing = payload.get("old_drawing")
            new_rev = payload.get("new_rev")
            old_rev = payload.get("old_rev")
            new_pdf = MCOPdfFile.objects.get(
                drawing_number=new_drawing,
                rev=new_rev,
            )
            old_pdf = MCOPdfFile.objects.get(
                drawing_number=old_drawing,
                rev=old_rev,
            )
            old_file_path = old_pdf.file_path
            new_file_path = new_pdf.file_path
            old_file_id = old_pdf.id
            new_file_id = new_pdf.id

            # 筛选出旧PDF的段落
            old_qs = MCOJsonParagraph.objects.filter(pdf=old_pdf).order_by('num')

            # 构建 old_paragraphs 列表
            old_paragraphs = []
            for obj in old_qs:
                # polygon数组可根据 x1~y4 字段拼装
                polygon = obj.polygon
                old_paragraphs.append({
                    "num": obj.num,
                    "value": obj.value,
                    "polygon": polygon
                })

            # 同理，新PDF的段落
            new_qs = MCOJsonParagraph.objects.filter(pdf=new_pdf).order_by('num')

            new_paragraphs = []
            for obj in new_qs:
                polygon = obj.polygon
                new_paragraphs.append({
                    "num": obj.num,
                    "value": obj.value,
                    "polygon": polygon
                })
            # 需要解析 old_paragraphs, new_paragraphs，可看需求
            # 这里做简化演示
            # old_paragraphs = [
            #     {"num": 1, "value": "PULL FORCE MUST BE GREATER THAN 5 N.",
            #      "polygon": [12, 25, 210, 25, 210, 125, 12, 125]},
            #     {"num": 2, "value": "INSPECT AND MEASURE AFTER BENDING AT FATP BEFORE SYSTEM ASSEMBLY.",
            #      "polygon": [15, 130, 200, 130, 200, 180, 15, 180]},
            #     {"num": 3, "value": "THIS PARAGRAPH WAS DELETED IN THE NEW VERSION",
            #      "polygon": [12, 190, 210, 190, 210, 250, 12, 250]},
            #     {"num": 4, "value": "THIS xcscsdc DELETED IN asdadadasd abc",
            #      "polygon": [12, 190, 210, 190, 210, 250, 12, 250]}
            # ]
            #
            # new_paragraphs = [
            #     {"num": 1, "value": "PULL FORCE MUST BE GREATER THAN 1 N.",
            #      "polygon": [12, 25, 210, 25, 210, 125, 12, 125]},
            #     {"num": 2, "value": "THIS PARAGRAPH IS NEWLY ADDED.",
            #      "polygon": [15, 130, 200, 130, 200, 180, 15, 180]},
            #     {"num": 3, "value": "THIS xcscsdc DELETED IN asdadadasd",
            #      "polygon": [12, 190, 210, 190, 210, 250, 12, 250]}
            # ]
            print(">>> calling compare_pdfs_task.delay with:", old_file_id, new_file_id, old_paragraphs, new_paragraphs)
            # 调用celery异步任务
            # task = add.delay(1,2)
            # task = compare_pdf(old_paragraphs, new_paragraphs, old_file_id, new_file_id, output_json="diff_output.json")
            task = compare_pdfs_task.delay(old_file_id, new_file_id, old_paragraphs, new_paragraphs)
            # 立刻返回一个json，告诉前端任务ID
            return SuccessResponse({"task_id": task.id, "status": "pending"}, status=202)

        return ErrorResponse({"error": "Only POST allowed"}, status=405)

    @action(
        detail=False,
        methods=["get"],
        url_path=r'compare_pdfs_result_view/(?P<task_id>[^/.]+)'
    )
    def compare_pdfs_result_view(self, request, task_id=None):
        """
        根据 task_id 查询Celery任务执行情况。如果已完成，则返回对比结果。
        否则返回状态 pending / failure。
        """
        async_result = AsyncResult(task_id)  # 绑定现有的task id

        # 获取当前状态
        if async_result.state == "PENDING" or async_result.state == "STARTED":
            # 任务还在进行中
            response_data = {
                "code": 2000,
                "page": 1,
                "limit": 1,
                "total": 1,
                "data": {
                    "task_id": task_id,
                    "status": "pending"
                },
                "msg": "still running"
            }
            return SuccessResponse(response_data)
        elif async_result.state == "FAILURE":
            # 任务执行失败
            response_data = {
                "code": 4000,
                "page": 1,
                "limit": 1,
                "total": 1,
                "data": {
                    "task_id": task_id,
                    "status": "failed"
                },
                "msg": str(async_result.result)  # 里面可能包含异常信息
            }
            return SuccessResponse(response_data)

        elif async_result.state == "SUCCESS":
            # 任务执行成功, 可以取到返回值
            result_value = async_result.get()
            # 按照你对 "compare_pdfs_task" 的定义,
            # result_value = {"status":"done", "result": {...}}
            response_data = {
                "code": 2000,
                "page": 1,
                "limit": 1,
                "total": 1,
                "data": {
                    "task_id": task_id,
                    "status": "completed",
                    "result": result_value  # 这里会包含 "status":"done" and "result":{sdiff,ldiff...}
                },
                "msg": "task finished"
            }
            return SuccessResponse(response_data)

        else:
            # 其他可能的状态: RETRY 或 REVOKED
            response_data = {
                "code": 2000,
                "data": {
                    "task_id": task_id,
                    "status": async_result.state.lower()
                },
                "msg": f"current state: {async_result.state}"
            }
            return SuccessResponse(response_data)