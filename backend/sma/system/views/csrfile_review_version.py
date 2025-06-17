import base64
import os
import logging
import re
from django.db.models import Q, F, Value, CharField, TextField, Func
from django.db.models.functions import Replace, Upper

from django.core.files.storage import default_storage
from django.db import transaction
from django.http import FileResponse
from rest_framework import serializers
from rest_framework.decorators import action
from packaging.version import parse

from application import settings
from sma.system.models.csrfile import CSRReviewVersion, CSRPdfFile, CSRJsonFile, CSRReviewGroup, CSRJsonSection, CSRJsonContent, \
    CSRJsonParagraph, CSRJsonImage, CSRJsonTable, CSRJsonTableCell, CSRReviewResult
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet

# 配置日志记录器
logger = logging.getLogger(__name__)

class CSRReviewVersionSerializer(CustomModelSerializer):
    """
    ReviewVersion 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = CSRReviewVersion
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

class CSRReviewVersionViewSet(CustomModelViewSet):
    """
    ReviewVersion 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = CSRReviewVersion.objects.all()
    serializer_class = CSRReviewVersionSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = CSRReviewVersionSerializer
    update_serializer_class = CSRReviewVersionSerializer

    # 定义过滤、搜索和排序字段
    # filter_fields = ['process']  # 支持的过滤字段
    search_fields = [
        'meet_req',
        'is_execute',
        'mflex_file',
        'remark',
        'process',
        'customer',
        'customer_file_name',
        'customer_file_code',
        'customer_file_version',
        'last_status',
        'status',
        'creator_name',
        'creator',
        'uploader_name',
    ];
    ordering_fields = [
        'meet_req',
        'is_execute',
        'mflex_file',
        'remark',
        'process',
        'customer',
        'customer_file_name',
        'customer_file_code',
        'customer_file_version',
        'last_status',
        'status',
        'creator_name',
        'creator',
        'uploader_name',
    ];

    def sanitize_string(self,s):
        """移除字符串中的换行符和空格，仅处理字符串类型"""
        if isinstance(s, str):
            return s.replace('\n', '').replace(' ', '').upper()
        return s  # 如果不是字符串，直接返回原值

    def extract_elements(self, value):
        if isinstance(value, list):
            # value 是一个列表，逐个元素进行清理
            sanitized = [self.sanitize_string(elem) for elem in value if isinstance(elem, str)]
            return [elem for elem in sanitized if elem]  # 移除空字符串
        elif isinstance(value, str):
            # value 是一个字符串，检查是否为列表格式的字符串
            value_stripped = value.strip()
            if re.match(r'^\[.*\]$', value_stripped):
                # 使用正则表达式提取中括号内的内容
                elements = re.findall(r'\[([^\]]*)\]', value_stripped)
                sanitized = [self.sanitize_string(elem) for elem in elements]
                return [elem for elem in sanitized if elem]  # 移除空字符串
            else:
                # 单纯的字符串
                sanitized = self.sanitize_string(value)
                return [sanitized] if sanitized else []
        else:
            # 其他类型，返回空列表
            return []

    def get_latest_section_review_group(self, review_group):
        # 1. 清理非 `value` 字段的值
        sanitized_process = review_group.process
        sanitized_customer = review_group.customer

        # 2. 清理并提取 `value` 字段的元素
        sanitized_elements = self.extract_elements(self.sanitize_string(review_group.value))

        # 日志记录 sanitized_elements
        logger.debug(f"Sanitized Elements for ReviewGroup ID {review_group.id}: {sanitized_elements}")

        # 3. 构建查询集，注解清理后的字段并指定 output_field
        queryset = CSRReviewGroup.objects.annotate(
            clean_value=Upper(
                RegexpReplace(
                    F('value'),
                    r'\\n| ',  # 正确的正则表达式模式
                    '',
                    output_field=TextField(),
                )
            )
        ).filter(
            process=sanitized_process,
            customer=sanitized_customer,
            status__in=['Closed', 'Cancel'],
        ).exclude(id=review_group.id)

        clean_values = queryset.values_list('clean_value', flat=True)
        for clean_val in clean_values:
            print(f"clean_value: {clean_val}")


        # 4. 处理 `value` 字段的过滤
        if sanitized_elements:
            if len(sanitized_elements) > 1:
                # 列表格式的字符串，确保所有元素都存在
                for elem in sanitized_elements:
                    print(f"Applying filter: clean_value__icontains='{elem}'")
                    queryset = queryset.filter(clean_value__icontains=elem)
            else:
                # 单纯的字符串，直接比较
                queryset = queryset.filter(clean_value__icontains=sanitized_elements[0])
                i=1
        else:
            # sanitized_elements 为空，记录警告并决定是否继续过滤
            logger.warning(
                f"Sanitized elements list is empty for ReviewGroup ID {review_group.id}. Skipping 'value' filtering.")
            # 根据业务逻辑，可以选择不进行 'value' 过滤，或者其他处理
            # 例如，可以选择不对 `value` 进行过滤，保持原有的查询集
            pass  # 这里选择不进行 'value' 过滤

        # 5. 排序并获取最新的匹配记录
        latest_section_review_group = queryset.order_by('-create_datetime').first()

        return latest_section_review_group

    def create(self, request, *args, **kwargs):
        pdf_file_id = request.data  # 从前端获取 PdfFile 的 ID
        if not pdf_file_id:
            return ErrorResponse(msg="缺少 PdfFile 的 ID")

        try:
            # 获取 PdfFile 对象
            pdf_file = CSRPdfFile.objects.get(id=pdf_file_id)
        except CSRPdfFile.DoesNotExist:
            return ErrorResponse(msg="指定的 PdfFile 不存在")

        # 获取该 PdfFile 的最新版本的 PdfJson
        json_files = CSRJsonFile.objects.filter(source_file=pdf_file)

        # 提取所有版本号
        versions = [(parse(json_file.analyze_version), json_file) for json_file in json_files]
        latest_analyze_version = None
        # 找到最高版本
        if versions:
            latest_version, latest_jsonfile = max(versions, key=lambda v: v[0])
            latest_analyze_version = latest_jsonfile.analyze_version
        else:
            latest_version = None
            latest_jsonfile = None

        if latest_analyze_version is None:
            return ErrorResponse(msg="该 PdfFile 没有关联的 JsonFile 版本")

        try:
            json_files = CSRJsonFile.objects.filter(source_file=pdf_file, analyze_version=latest_analyze_version)
            if not json_files.exists():
                return ErrorResponse(msg="未找到对应的 JsonFile 记录")
            elif json_files.count() > 1:
                # 如果匹配到多条，返回第一条（或其他处理逻辑）
                pdf_json = json_files.first()
                # 或者返回错误
                # return ErrorResponse(msg="查询到多个 JsonFile 记录，请检查数据唯一性")
            else:
                pdf_json = json_files.first()
        except CSRJsonFile.DoesNotExist:
            return ErrorResponse(msg="未找到对应的 JsonFile 记录")

        # 检查是否有状态为 'ongoing' 的 ReviewVersion
        ongoing_review_versions = CSRReviewVersion.objects.filter(jsonfile=pdf_json, status='OnGoing')
        if ongoing_review_versions.exists():
            return ErrorResponse(msg="该 PdfFile 已经有正在进行中的 ReviewVersion，无法创建新的")

        # 如果存在状态为 'closed' 的 ReviewVersion，复制并将状态更新为 'cancel'
        closed_review_versions = CSRReviewVersion.objects.filter(jsonfile=pdf_json, status='Closed')
        if closed_review_versions.exists():
            # 复制 closed 状态的 ReviewVersion 及其关联的 ReviewGroup 和 Sections
            with transaction.atomic():
                # 假设我们只需要处理一个 'closed' 的对象，取第一个
                closed_review_version = closed_review_versions.first()
                # 复制 ReviewVersion

                review_version_data = {
                    "jsonfile": closed_review_version.jsonfile,
                    "file_name": closed_review_version.file_name,
                    "process": closed_review_version.process,
                    "customer": closed_review_version.customer,
                    "customer_file_name": closed_review_version.customer_file_name,
                    "customer_file_code": closed_review_version.customer_file_code,
                    "customer_file_version": closed_review_version.customer_file_version,
                    "creator": closed_review_version.creator,
                    "modifier": closed_review_version.modifier,
                    "dept_belong_id": closed_review_version.dept_belong_id,
                    "uploader_name": closed_review_version.uploader_name,
                    "status": 'OnGoing',
                    "last_status": closed_review_version.last_status,
                }

                # 创建新的 ReviewVersion（状态为 cancel）
                new_review_version = CSRReviewVersion.objects.create(**review_version_data)

                # 复制所有关联的 ReviewGroup
                for review_group in closed_review_version.review_groups.all():
                    new_review_group = CSRReviewGroup.objects.create(
                        element_type=review_group.element_type,
                        review_version=new_review_version,
                        order_in_version=review_group.order_in_version,
                        element_ids=review_group.element_ids,
                        row_index=review_group.row_index,
                        last_status=review_group.last_status,
                        process=new_review_version.process,
                        customer=new_review_version.customer,
                        customer_file_name=new_review_version.customer_file_name,
                        customer_file_code=new_review_version.customer_file_code,
                        customer_file_version=new_review_version.customer_file_version,
                        uploader_name=new_review_version.uploader_name,
                        status="OnGoing",
                    )
                    # 复制多对多关系
                    new_review_group.sections.set(review_group.sections.all())
                    new_review_group.paragraphs.set(review_group.paragraphs.all())
                    new_review_group.images.set(review_group.images.all())
                    new_review_group.cells.set(review_group.cells.all())

                    # 复制关联的 ReviewResult
                    for review_result in review_group.results.all():
                        CSRReviewResult.objects.create(
                            group=new_review_group,
                            status=review_result.status,
                            meet_req=review_result.meet_req,
                            is_execute=review_result.is_execute,
                            mflex_file=review_result.mflex_file,
                            remark=review_result.remark,
                            process=review_result.process,
                            customer=review_result.customer,
                            customer_file_name=review_result.customer_file_name,
                            customer_file_code=review_result.customer_file_code,
                            customer_file_version=review_result.customer_file_version,
                            uploader_name=review_result.uploader_name,
                            creator=closed_review_version.creator,
                            modifier=closed_review_version.modifier,
                            dept_belong_id=closed_review_version.dept_belong_id,
                            last_status=review_result.last_status,
                            value=review_result.value,
                        )
                closed_review_version.status = 'Cancel'
                closed_review_version.save()
                for review_group in closed_review_version.review_groups.all():
                    review_group.status = 'Cancel'
                    review_group.save()
                # 返回成功响应
                return SuccessResponse(msg="升版 ReviewVersion")

        # 准备创建 ReviewVersion 的数据
        review_version_data = {
            "jsonfile": pdf_json.id,
            "process": pdf_file.process,
            "customer": pdf_file.customer,
            "customer_file_name": pdf_file.customer_file_name,
            "customer_file_code": pdf_file.customer_file_code,
            "customer_file_version": pdf_file.customer_file_version,
            "uploader_name": pdf_file.uploader_name,
            "status": "OnGoing",

        }

        # 创建新的 ReviewVersion 实例
        # review_version = ReviewVersion.objects.create(**review_version_data)
        with transaction.atomic():
            serializer = self.get_serializer(data=review_version_data)
            serializer.is_valid(raise_exception=True)
            review_version = serializer.save()  # 保存数据库记录
            order_in_version = 0

            # 创建 ReviewGroup 实例
            # 为 JsonFile 关联的 sections 创建 ReviewGroup
            for section in pdf_json.sections.all().order_by('order_in_file'):
                order_in_version += 1
                review_group=CSRReviewGroup.objects.create(
                    element_type="section",
                    element_ids=[section.id],
                    review_version=review_version,
                    order_in_version=order_in_version,
                    last_status="EMPTY",
                    value=section.value,
                    process=review_version.process,
                    customer=review_version.customer,
                    customer_file_name=review_version.customer_file_name,
                    customer_file_code=review_version.customer_file_code,
                    customer_file_version=review_version.customer_file_version,
                    uploader_name=review_version.uploader_name,
                    status="OnGoing",
                )
                review_group.sections.add(section)

                latest_section_review_group = self.get_latest_section_review_group(review_group)

                if latest_section_review_group:
                    # 获取关联的 ReviewResult
                    related_review_results = CSRReviewResult.objects.filter(group=latest_section_review_group)
                    review_group.last_status = 'SUCCESS'
                    review_group.save()
                    # 复制 ReviewResult 并关联到新的 ReviewGroup
                    for review_result in related_review_results:
                        CSRReviewResult.objects.create(
                            group=review_group,
                            status='OnGoing',
                            name=review_version.file_name,
                            meet_req=review_version.meet_req,
                            is_execute=review_version.is_execute,
                            mflex_file=review_version.mflex_file,
                            remark=review_version.remark,
                            process=review_version.process,
                            customer=review_version.customer,
                            customer_file_name=review_version.customer_file_name,
                            customer_file_code=review_version.customer_file_code,
                            customer_file_version=review_version.customer_file_version,
                            uploader_name=review_version.uploader_name,
                            creator=review_result.creator,
                            modifier=review_result.modifier,
                            dept_belong_id=review_result.dept_belong_id,
                            last_status=review_result.last_status,
                            value=review_result.value,
                        )
                for content in section.contents.all():
                    elements = []

                    # 添加段落
                    for paragraph in content.paragraphs.all():
                        elements.append({
                            "type": "paragraph",
                            "element_ids": [paragraph.id],
                            "order_in_file": paragraph.order_in_file,
                            "review_version": review_version,
                            "value": paragraph.value,
                        })

                    # 添加单元格
                    cell_groups = {}
                    for table in content.tables.all():
                        for cell in table.cells.all():
                            # 按照表格 ID 和 row_index 组合分组
                            group_key = (table.id, cell.row_index)
                            if group_key not in cell_groups:
                                cell_groups[group_key] = {
                                    "type": "cell",
                                    "element_ids": [],
                                    "order_in_file": cell.order_in_file,
                                    "row_index": cell.row_index,
                                    "review_version": review_version,
                                    "value": [],
                                }
                            cell_groups[group_key]["element_ids"].append(cell.id)
                            if isinstance(cell.value, bytes):
                                cell_groups[group_key]["value"].append(cell.id)
                            else:
                                cell_groups[group_key]["value"].append(f'[{cell.value}]')
                    # 将单元格分组添加到元素列表
                    for group in cell_groups.values():
                        elements.append(group)

                    # 添加图片
                    for image in content.images.all():
                        elements.append({
                            "type": "image",
                            "element_ids": [image.id],
                            "order_in_file": image.order_in_file,
                            "review_version": review_version,
                            "value": image.id,
                        })

                    # 按照 order_in_file 排序
                    elements.sort(key=lambda x: x["order_in_file"])

                    # 创建 ReviewGroup
                    for element in elements:
                        order_in_version += 1
                        review_group=CSRReviewGroup.objects.create(
                            element_type=element["type"],
                            element_ids=element["element_ids"],  # 存储多个元素 ID
                            row_index=element.get("row_index"),  # 对于非单元格元素，这里为 None
                            review_version=element["review_version"],
                            order_in_version=order_in_version,
                            last_status="EMPTY",
                            value=element["value"],
                            process=review_version.process,
                            customer=review_version.customer,
                            customer_file_name=review_version.customer_file_name,
                            customer_file_code=review_version.customer_file_code,
                            customer_file_version=review_version.customer_file_version,
                            uploader_name=review_version.uploader_name,
                            status="OnGoing",
                        )
                        if element["type"] == "section":
                            # 关联 SectionReviewGroup 中间表
                            sections = CSRJsonSection.objects.filter(id__in=element["element_ids"])
                            review_group.sections.set(sections)  # 设置关联的 Section

                        elif element["type"] == "paragraph":
                            # 关联 ParagraphReviewGroup 中间表
                            paragraphs = CSRJsonParagraph.objects.filter(id__in=element["element_ids"])
                            review_group.paragraphs.set(paragraphs)  # 设置关联的 Paragraph

                        elif element["type"] == "image":
                            # 关联 ImageReviewGroup 中间表
                            images = CSRJsonImage.objects.filter(id__in=element["element_ids"])
                            review_group.images.set(images)  # 设置关联的 Image

                        elif element["type"] == "cell":
                            # 关联 CellReviewGroup 中间表
                            cells = CSRJsonTableCell.objects.filter(id__in=element["element_ids"])
                            review_group.cells.set(cells)  # 设置关联的 Cell

                        # 查找最新的 ReviewGroup，排除当前新建的 ReviewGroup
                        latest_review_group = self.get_latest_section_review_group(review_group)

                        if latest_review_group:
                            # 获取关联的 ReviewResult
                            related_review_results = CSRReviewResult.objects.filter(group=latest_review_group)
                            review_group.last_status = 'SUCCESS'
                            review_group.save()
                            # 复制 ReviewResult 并关联到新的 ReviewGroup
                            for review_result in related_review_results:
                                CSRReviewResult.objects.create(
                                    group=review_group,
                                    status='OnGoing',
                                    meet_req=review_version.meet_req,
                                    is_execute=review_version.is_execute,
                                    mflex_file=review_version.mflex_file,
                                    remark=review_version.remark,
                                    process=review_result.process,
                                    customer=review_result.customer,
                                    customer_file_name=review_result.customer_file_name,
                                    customer_file_code=review_result.customer_file_code,
                                    customer_file_version=review_result.customer_file_version,
                                    uploader_name=review_result.uploader_name,
                                    creator=review_result.creator,
                                    modifier=review_result.modifier,
                                    dept_belong_id=review_result.dept_belong_id,
                                    last_status=review_result.last_status,
                                    value=review_result.value,
                                )
                            # 更新 order_in_version
                        order_in_version += 1
        return SuccessResponse(data=[], msg="新建Review成功")

    def list(self, request, *args, **kwargs):
        """
        重写list方法
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset()).order_by('customer_file_name')
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(serializer.data,msg="获取成功")

    @action(detail=False, methods=['post'])
    def getpdf(self, request):
        """
        获取 PDF 文件路径
        """
        try:
            # 获取请求中的 `review_version_id`
            review_version_id = request.data.get("review_version_id")
            if not review_version_id:
                return ErrorResponse(msg="缺少审核版本 ID")

            # 查找 ReviewVersion 对象
            review_version = CSRReviewVersion.objects.get(id=review_version_id)
            if not review_version:
                return ErrorResponse(msg="未找到对应的审核版本")

            # 通过关联的 JsonFile 获取 PdfFile
            json_file = review_version.jsonfile
            if not json_file or not json_file.source_file:
                return ErrorResponse(msg="未找到关联的 PDF 文件")

            # 获取 PdfFile 的文件路径
            pdf_file_path = json_file.source_file.file_path
            if not pdf_file_path:
                return ErrorResponse(msg="PDF 文件路径为空")

            # 返回文件流供前端加载
            response = FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(pdf_file_path)}"'
            return response
        except CSRReviewVersion.DoesNotExist:
            return ErrorResponse(msg="指定的审核版本不存在")
        except Exception as e:
            return ErrorResponse(msg=f"获取 PDF 文件失败: {str(e)}")


    @action(detail=True, methods=["get"])
    def getjson(self, request, pk=None):
        """
        获取指定 ReviewVersion 的 JSON 数据和关联层次
        """
        try:
            # 获取指定的 ReviewVersion
            review_version = CSRReviewVersion.objects.get(id=pk)

            # 获取关联的 JsonFile
            json_file = review_version.jsonfile

            if not json_file:
                return ErrorResponse(msg="未找到关联的 JsonFile")

            # 获取关联的 ReviewGroup 数据
            review_groups = review_version.review_groups.all().order_by("order_in_version")

            # 获取 JsonFile 的相关层次数据
            sections = CSRJsonSection.objects.filter(recognition_result=json_file).order_by("order_in_file")
            data = []

            for section in sections:
                review_group = review_groups.filter(sections__id=section.id).first()
                section_data = {
                    "type": "Section",
                    "id": section.id,
                    "order_in_file": section.order_in_file,
                    "value": section.value,
                    "ch_value": section.ch_value,
                    "thai_value": section.thai_value,
                    "has_xbar": section.has_xbar,
                    "has_strike_through": section.has_strike_through,
                    "true_value": section.true_value,
                    "true_ch_value": section.true_ch_value,
                    "true_thai_value": section.true_thai_value,
                    "page": section.page,
                    "polygon": section.polygon,
                    "contents": [],
                    "review_group_id": review_group.id,
                }
                # 获取该 section 的内容
                contents = CSRJsonContent.objects.filter(section=section).order_by("order_in_file")
                for content in contents:
                    content_data = {
                        "id": content.id,
                        "order_in_file": content.order_in_file,
                        "elements": [],  # 包含所有元素的统一排序列表
                    }

                    # 获取段落
                    paragraphs = CSRJsonParagraph.objects.filter(content=content).order_by("order_in_file")
                    paragraph_data = [
                        {
                            "type": "Paragraph",
                            "id": p.id,
                            "order_in_file": p.order_in_file,
                            "value": p.value,
                            "ch_value": p.ch_value,
                            "thai_value": p.thai_value,
                            "has_xbar": p.has_xbar,
                            "has_strike_through": p.has_strike_through,
                            "true_value": p.true_value,
                            "true_ch_value": p.true_ch_value,
                            "true_thai_value": p.true_thai_value,
                            "page": p.page,
                            "polygon": p.polygon,
                            "review_group_id": review_groups.filter(paragraphs__id=p.id).first().id,
                        }
                        for p in paragraphs
                    ]
                    print('paragraph_data', paragraph_data)
                    # 获取图片
                    images = CSRJsonImage.objects.filter(content=content).order_by("order_in_file")
                    image_data = [
                        {
                            "type": "Image",
                            "id": img.id,
                            "order_in_file": img.order_in_file,
                            "image_base64": f"{base64.b64encode(img.image_bytes).decode('utf-8')}" if img.image_bytes else None,
                            "page": img.page,
                            "polygon": img.polygon,
                            "review_group_id": review_groups.filter(images__id=img.id).first().id,
                        }
                        for img in images
                    ]

                    # 获取表格及其单元格
                    tables = CSRJsonTable.objects.filter(content=content).order_by("order_in_file")
                    table_data = []
                    for table in tables:
                        cells = CSRJsonTableCell.objects.filter(table=table).order_by("order_in_file")
                        cell_data = [
                            {
                                "id": cell.id,
                                "type": "Cell",
                                "order_in_file": cell.order_in_file,
                                "cell_type": cell.cell_type,
                                "value": cell.value,
                                "ch_value": cell.ch_value,
                                "thai_value": cell.thai_value,
                                "has_xbar": cell.has_xbar,
                                "has_strike_through": cell.has_strike_through,
                                "true_value": cell.true_value,
                                "true_ch_value": cell.true_ch_value,
                                "true_thai_value": cell.true_thai_value,
                                "image_base64": f"data:image/jpeg;base64,{base64.b64encode(cell.image_bytes).decode('utf-8')}" if cell.image_bytes else None,
                                "row_index": cell.row_index,
                                "col_index": cell.col_index,
                                "row_span": cell.row_span,
                                "col_span": cell.col_span,
                                "page": cell.page,
                                "polygon": cell.polygon,
                                "is_virtual": cell.is_virtual,
                                "review_group_id": review_groups.filter(cells__id=cell.id).first().id,
                            } for cell in cells
                        ]
                        table_data.append(
                            {
                                "type": "Table",
                                "id": table.id,
                                "order_in_file": table.order_in_file,
                                "rows_num": table.rows_num,
                                "cols_num": table.cols_num,
                                "polygon": table.polygon,
                                "page": table.page,
                                "cells": cell_data,
                            }
                        )

                    # 合并所有元素并按 order_in_file 排序
                    all_elements = paragraph_data + image_data + table_data
                    all_elements.sort(key=lambda x: x["order_in_file"])

                    content_data["elements"] = all_elements
                    section_data["contents"].append(content_data)

                data.append(section_data)

            # 返回完整的数据
            response_data = {
                "review_version": {
                    "id": review_version.id,
                    "file_name": review_version.file_name,
                    "process": review_version.process,
                },
                "json_file": {
                    "id": json_file.id,
                    "name": json_file.name,
                },
                "review_groups": [
                    {
                        "id": group.id,
                        "key": group.id,
                        "order_in_version": group.order_in_version,
                        "element_type": group.element_type,
                        "element_ids": group.element_ids,
                        "last_status": group.last_status,
                        "status": group.status,
                    }
                    for group in review_groups
                ],
                "sections": data,
            }

            return SuccessResponse(data=response_data, msg="获取 JSON 数据成功")
        except CSRReviewVersion.DoesNotExist:
            return ErrorResponse(msg="未找到指定的 ReviewVersion")
        except Exception as e:
            return ErrorResponse(msg=f"获取数据时发生错误: {str(e)}")

    @action(detail=False, methods=['post'])
    def closestatus(self, request):
        review_version_id = request.data.get("review_version_id")

        try:
            # 获取ReviewVersion
            review_version = CSRReviewVersion.objects.get(id=review_version_id)

            # 获取与该ReviewVersion关联的所有ReviewGroup
            review_groups = CSRReviewGroup.objects.filter(review_version=review_version)

            # 存储没有ReviewResult的ReviewGroup的group_id
            empty_review_groups = ''
            error_review_groups = ''

            for group in review_groups:
                # 获取当前ReviewGroup的ReviewResult数量
                review_result_count = CSRReviewResult.objects.filter(group=group).count()

                if review_result_count == 0:
                    group.last_status = "EMPTY"
                    group.save()
                    review_version.last_status = "ERROR"
                    empty_review_groups += '[' + str(group.id) + ']'  # 添加group_id

                if group.last_status == "ERROR":
                    review_version.last_status = "ERROR"
                    error_review_groups += '[' + str(group.id) + ']'  # 添加group_id

            # 如果有没有ReviewResult的ReviewGroup，返回失败信息
            if empty_review_groups:
                return ErrorResponse(msg='某些ReviewGroup未包含ReviewResult'+ empty_review_groups)
            if error_review_groups:
                return ErrorResponse(msg='某些ReviewGroup填写错误'+ error_review_groups)

            # 如果所有ReviewGroup都包含ReviewResult，则关闭该ReviewVersion
            review_version.status = 'Closed'
            review_version.save()
            for review_group in review_version.review_groups.all():
                review_group.status = 'Closed'
                review_group.save()
                for review_result in review_group.results.all():
                    review_result.status = 'Closed'
                    review_result.save()
            return SuccessResponse(data=[], msg="已成功关闭该Review")

        except CSRReviewVersion.DoesNotExist:
            return ErrorResponse(msg='ReviewVersion不存在')

        except Exception as e:
            return ErrorResponse(msg='fail')

    @action(detail=False, methods=['post'])
    def export_reviews(self, request):
        review_version_id = request.data['id']  # 从前端获取 PdfFile 的 ID
        if not review_version_id:
            return ErrorResponse(msg="缺少 review_version 的 ID")
        results = []
        try:
            # 获取 PdfFile 对象
            reviewVersion = CSRReviewVersion.objects.get(id=review_version_id)
            for review_group in reviewVersion.review_groups.all():
                for review_result in review_group.results.all():
                    if review_result.meet_req == 'Y':
                        results.append({
                            "process": review_result.process,
                            "customer": review_result.customer,
                            "customer_file_name": review_result.customer_file_name,
                            "customer_file_code": review_result.customer_file_code,
                            "customer_file_version": review_result.customer_file_version,
                            "uploader_name": review_result.uploader_name,
                            "meet_req": review_result.meet_req,
                            "is_execute": review_result.is_execute,
                            "mflex_file": review_result.mflex_file,
                            "remark": review_result.remark,
                        })
        except CSRReviewVersion.DoesNotExist:
            return ErrorResponse(msg="指定的 review_version 不存在")
        # 5. 返回：只带 results，就不需要前端做分页了
        return SuccessResponse(data=results, msg="导出成功")

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
            instance = CSRReviewVersion.objects.get(pk=pk)
            # 删除数据库记录
            instance.delete()
            return SuccessResponse(data=[], msg="删除成功")
        except CSRReviewVersion.DoesNotExist:
            return ErrorResponse(msg=f"ReviewVersion with pk {pk} does not exist")

class RegexpReplace(Func):
    function = 'REGEXP_REPLACE'
    output_field = CharField()

    def __init__(self, expression, pattern, replacement, **extra):
        super().__init__(expression, Value(pattern), Value(replacement), **extra)