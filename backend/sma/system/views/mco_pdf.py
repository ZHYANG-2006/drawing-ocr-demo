import os

from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.decorators import action
from django.http import FileResponse
from application import settings
from sma.system.models.mco import MCOPdfFile, MCOJsonFile, MCOJsonPage, MCOJsonContent, MCOJsonParagraph
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from django.db.models import Max
from django.utils import timezone
from .mco_tasks import task_queue

class MCOPdfFileSerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = MCOPdfFile
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

class MCOPdfFileViewSet(CustomModelViewSet):
    """
    PdfFile 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = MCOPdfFile.objects.all()
    serializer_class = MCOPdfFileSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = MCOPdfFileSerializer
    update_serializer_class = MCOPdfFileSerializer

    # 定义过滤、搜索和排序字段
    search_fields = [
        'name',
        'title',
        'drawing_number',
        'rev',
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
        'name',
        'title',
        'drawing_number',
        'rev',
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

    def get_permissions(self):
        # 如果是 POST 且不是单条记录操作（即 create）
        if self.request.method == 'POST' and 'pk' not in self.kwargs:
            return [AllowAny()]
        # 其它动作仍需登录
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        自定义创建逻辑
        """
        file = request.FILES.get('file')  # 获取上传的文件
        if not file:
            return ErrorResponse(msg='请上传文件')

        # 指定存储路径
        upload_dir = settings.PATH_PDF_MCO
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
        if MCOPdfFile.objects.filter(name=file_name).exists():
            return ErrorResponse(msg=f"文件名 “{file_name}” 已存在，无法重复上传")

        if request.user and request.user.is_authenticated:
            uploader_name = getattr(request.user, 'name', request.user.username)
        else:
            uploader_name = request.data.get('uploader_name', 'Anonymous')  # 或者直接写 'Anonymous'
        # 创建 PdfFile 数据
        data = request.data.dict()  # 转为可变字典
        data['name'] = file_name  # 去掉后缀的文件名
        data['file_path'] = file_path  # 保存文件路径到模型字段
        data['business_type'] = "MCO"
        data['file_extension'] = file_extension  # 文件后缀类型
        data['uploader_name'] = uploader_name
        data['modifier'] = 1
        data['dept_belong_id'] = 1
        data['creator_id'] = 1

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        pdf_file = serializer.save()  # 保存数据库记录
        version_str = "0.0.0"
        # 如果已经解析过最新版本则直接返回
        # if pdf_file.queue_order == 0 and pdf_file.analyze_version == version_str:
        if pdf_file.queue_order == 0:
            return SuccessResponse(data=[], msg="已存在最新版本的解析，无需重新解析")

        # 设置排队顺序 (queue_order)
        # 如果有正在解析的，自己排在后面，否则直接置为1
        if MCOPdfFile.objects.filter(queue_order=1).exists():
            max_queue_order = MCOPdfFile.objects.aggregate(max_order=Max('queue_order'))['max_order'] or 1
            pdf_file.queue_order = max_queue_order + 1
        else:
            pdf_file.queue_order = 1
        pdf_file.start_analyze_time = timezone.now()
        pdf_file.analyze_version = version_str
        pdf_file.save()

        # 将任务（文件ID）放入队列
        task_queue.put(pdf_file.id)

        return SuccessResponse(data=[], msg=f"文件已加入解析队列，队列位置 {pdf_file.queue_order}")

        # return SuccessResponse(data=serializer.data, msg="文件上传成功")

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
            instance = MCOPdfFile.objects.get(pk=pk)
            # 删除数据库记录
            instance.delete()
            return SuccessResponse(data=[], msg="删除成功")
        except MCOPdfFile.DoesNotExist:
            return ErrorResponse(msg=f"ReviewResult with pk {pk} does not exist")

    @action(detail=False, methods=['post'])
    def getpdf(self, request):
        """
        获取 PDF 文件路径
        """
        try:
            # 获取请求中的 `id`
            file_id = request.data.get("id")
            if not file_id:
                return ErrorResponse(msg="缺少审核版本 ID")
            # 查找 ReviewVersion 对象
            pdf_file = MCOPdfFile.objects.get(id=file_id)
            if not pdf_file:
                return ErrorResponse(msg="未找到对应的PDF文件")
            # jsonFiles = JsonFile.objects.filter(source_file=pdf_file).order_by("create_datetime")
            # if len(jsonFiles) == 0:
            #     return ErrorResponse(msg="未找到关联的Json")
            # 通过关联的 JsonFile 获取 PdfFile
            # json_file = jsonFiles[0]
            # 获取 PdfFile 的文件路径
            pdf_file_path = pdf_file.file_path
            if not pdf_file_path:
                return ErrorResponse(msg="PDF 文件路径为空")

            # 返回文件流供前端加载
            response = FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(pdf_file_path)}"'
            return response
        except MCOPdfFile.DoesNotExist:
            return ErrorResponse(msg="指定的PDF不存在")
        except Exception as e:
            return ErrorResponse(msg=f"获取 PDF 文件失败: {str(e)}")

    @action(detail=True, methods=["get"])
    def getjson(self, request, pk=None):
        """
        获取指定 ReviewVersion 的 JSON 数据和关联层次
        """
        try:
            # 获取请求中的 `id`
            file_id = pk
            if not file_id:
                return ErrorResponse(msg="缺少审核版本 ID")
            # 查找 ReviewVersion 对象
            pdf_file = MCOPdfFile.objects.get(id=file_id)
            if not pdf_file:
                return ErrorResponse(msg="未找到对应的PDF文件")
            jsonFiles = MCOJsonFile.objects.filter(source_file=pdf_file).order_by("create_datetime")
            if len(jsonFiles) == 0:
                return ErrorResponse(msg="未找到关联的Json")
            # 通过关联的 JsonFile 获取 PdfFile
            json_file = jsonFiles[0]
            # 获取 PdfFile 的文件路径

            if not json_file:
                return ErrorResponse(msg="未找到关联的 JsonFile")

            # 获取 JsonFile 的相关层次数据
            pages = MCOJsonPage.objects.filter(recognition_result=json_file).order_by("page")
            data = []

            for page in pages:
                page_data = {
                    "id": page.id,
                    "page": page.page,
                    "contents": [],
                }
                # 获取该 section 的内容
                contents = MCOJsonContent.objects.filter(page=page).order_by("page")
                for content in contents:
                    content_data = {
                        "id": content.id,
                        "order_in_file": content.order_in_file,
                    }

                    title_paragraph = [
                        {
                            "type": "Paragraph",
                            "id": 0,
                            "order_in_file": 0,
                            "value": f"TITLE:{pdf_file.title}\nDRAWING NUMBER:{pdf_file.drawing_number}\nREV.:{pdf_file.rev}\n",
                            "page": 1,
                            "polygon": pdf_file.polygon,
                        }
                    ]
                    # 获取段落
                    paragraphs = MCOJsonParagraph.objects.filter(content=content).order_by("order_in_file")
                    paragraph_data = [
                        {
                            "type": "Paragraph",
                            "id": p.id,
                            "order_in_file": p.order_in_file,
                            "value": p.value,
                            "page": 1,
                            "polygon": p.polygon,
                        }
                        for p in paragraphs
                    ]
                    # 合并所有元素并按 order_in_file 排序
                    paragraph_data.sort(key=lambda x: x["order_in_file"])
                    all_elements = title_paragraph + paragraph_data
                    content_data["elements"] = all_elements
                    page_data["contents"].append(content_data)

                data.append(page_data)

            # 返回完整的数据
            response_data = {
                "json_file": {
                    "id": json_file.id,
                    "name": json_file.name,
                },
                "pages": data,
            }

            return SuccessResponse(data=response_data, msg="获取 JSON 数据成功")
        except MCOPdfFile.DoesNotExist:
            return ErrorResponse(msg="未找到指定的 ReviewVersion")
        except Exception as e:
            return ErrorResponse(msg=f"获取数据时发生错误: {str(e)}")