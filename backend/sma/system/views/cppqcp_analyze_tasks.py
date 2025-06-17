import base64
import socket

from django.http import JsonResponse
from django.db.models import F
import os
import json
import requests
from django.db.models import Max
from django.conf import settings
from datetime import datetime

from plotly.offline.offline import build_save_image_post_script
from rest_framework.decorators import action
from rest_framework import serializers
from sma.system.models import JsonTableCell
from sma.system.models.cppqcp import PdfFile, JsonFile, JsonSection, JsonContent, JsonParagraph, JsonTable, JsonImage
import threading

from sma.utils.json_response import SuccessResponse, ErrorResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet

class CPPQCPFileSerializer(CustomModelSerializer):
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
# 全局解析锁
parse_lock = threading.Lock()
class CPPQCPTaskViewSet(CustomModelViewSet):
    queryset = PdfFile.objects.all()
    serializer_class = CPPQCPFileSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = CPPQCPFileSerializer
    update_serializer_class = CPPQCPFileSerializer

    # 定义过滤、搜索和排序字段
    filter_fields = ['name', 'is_analyzed', 'has_expired']  # 支持的过滤字段
    search_fields = ['name', 'flow_name', 'customer']  # 支持的搜索字段
    ordering_fields = ['create_datetime', 'update_datetime', 'progress']  # 支持排序的字段
    def process_polygon(self, polygon):
        """
        处理 polygon 数据，将其转换为 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] 的结构。
        如果 polygon 有五个点，删除重复并按左上、右上、右下、左下的顺序排列。
        """
        # 判断是否已经是嵌套列表
        if isinstance(polygon, list) and all(isinstance(point, list) and len(point) == 2 for point in polygon):
            # 已经是正确格式的多边形，直接返回
            return polygon

        # 判断是否为平铺的列表数据
        if isinstance(polygon, list):
            if len(polygon) == 8:
                # 已经是完整的四边形数据，转换为嵌套列表
                return [
                    [polygon[0], polygon[1]],
                    [polygon[2], polygon[3]],
                    [polygon[4], polygon[5]],
                    [polygon[6], polygon[7]],
                ]
            elif len(polygon) == 4:
                # 只有两个点，补足为四边形
                x1, y1, x2, y2 = polygon
                return [
                    [x1, y1],
                    [x2, y1],
                    [x2, y2],
                    [x1, y2],
                ]
            elif len(polygon) == 10:
                # 处理5个点的情况，删除重复点并按左上、右上、右下、左下排序
                points = [
                    [polygon[0], polygon[1]],
                    [polygon[2], polygon[3]],
                    [polygon[4], polygon[5]],
                    [polygon[6], polygon[7]],
                    [polygon[8], polygon[9]]
                ]
                # 删除重复点，利用集合去重
                unique_points = list({tuple(p) for p in points})
                if len(unique_points) == 4:
                    # 将五个点中的重复点移除并按顺序排列
                    unique_points.sort(key=lambda p: (p[0], p[1]))  # 排序为左上、右上、右下、左下
                    # 依据点的位置排序
                    left_top = min(unique_points, key=lambda p: (p[0], p[1]))   # 左上
                    right_top = max(unique_points, key=lambda p: (p[0], -p[1]))  # 右上
                    left_bottom = min(unique_points, key=lambda p: (p[0], -p[1]))  # 左下
                    right_bottom = max(unique_points, key=lambda p: (p[0], p[1]))  # 右下

                    return [left_top, right_top, right_bottom, left_bottom]

        # 既不是嵌套列表也不是平铺数据，抛出异常
        raise ValueError("Invalid polygon data. It must be a list of 4 or 8 or 10 numbers, or a nested list of points.")

    def process_polygon_spc(self, polygon):
        # 判断是否为平铺的列表数据
        if isinstance(polygon, list):
            if len(polygon) == 8:
                # 已经是完整的四边形数据，转换为嵌套列表
                return [
                    [polygon[0] * 72, polygon[1] * 72],
                    [polygon[2] * 72, polygon[3] * 72],
                    [polygon[4] * 72, polygon[5] * 72],
                    [polygon[6] * 72, polygon[7] * 72],
                ]
            elif len(polygon) == 4:
                # 只有两个点，补足为四边形
                x1, y1, x2, y2 = polygon
                return [
                    [x1, y1],
                    [x2, y1],
                    [x2, y2],
                    [x1, y2],
                ]

        # 既不是嵌套列表也不是平铺数据，抛出异常
        raise ValueError("Invalid polygon data. It must be a list of 4 or 8 numbers, or a nested list of points.")

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

    def process_file(self, pdf_file):
        """调用远程解析接口并更新状态"""
        try:
            # 获取服务器地址前缀
            server_ip = socket.gethostbyname(socket.gethostname())  # 假设pdf_file对象中有一个server_ip属性存储服务器地址

            # 根据服务器前缀选择不同的接口
            if server_ip.startswith("172.30"):
                # 服务器前缀为 172，调用真实接口
                url_analyze = "http://172.16.94.134:8020/analyze"
                headers = {
                    "x-api-key": "e5f3d701-b48f-45b7-b61d-43c1ff878226"
                }

                # 打开PDF文件并发送POST请求
                with open(pdf_file.file_path, "rb") as f:
                    files = {
                        "pdffile": f  # 使用文件对象
                    }

                    # 发送POST请求
                    response = requests.post(url_analyze, headers=headers, files=files)

                # 检查响应是否成功
                if response.status_code == 200:
                    response_data = response.json()
                    # 处理返回的JSON数据
                else:
                    print(f"请求失败，状态码：{response.status_code}")

                # 获取版本号信息
                response_v = requests.get(f"http://172.16.94.134:8020/")
                response_v_data = response_v.json()

                # 提取版本号
                version_str = response_v_data  # 默认版本号为 "v0.0.0"
                version_parts = version_str.lstrip("v").split(".")  # 移除 "v" 并拆分版本号
                version_number = (
                        int(version_parts[0]) * 10000 +
                        int(version_parts[1]) * 100 +
                        int(version_parts[2])
                ) if len(version_parts) == 3 else 0
                # 提取版本号
                pdf_file.analyze_version = version_str

            else:
                # 服务器前缀为 192，调用 mock 接口
                url_analyze = "http://localhost:7007/plugins/mock/response/"
                response = requests.get(url_analyze)

                # 检查响应是否成功
                if response.status_code == 200:
                    response_data = response.json()
                    # 处理返回的JSON数据
                else:
                    print(f"请求失败，状态码：{response.status_code}")

                # 获取版本号信息
                url_version = "http://localhost:7007/plugins/mock/version/"
                response_v = requests.get(url_version)
                response_v_data = response_v.json().get("version")

                # 提取版本号
                version_str = response_v_data  # 默认版本号为 "v0.0.0"
                version_parts = version_str.lstrip("v").split(".")  # 移除 "v" 并拆分版本号
                version_number = (
                        int(version_parts[0]) * 10000 +
                        int(version_parts[1]) * 100 +
                        int(version_parts[2])
                ) if len(version_parts) == 3 else 0
                # 提取版本号
                pdf_file.analyze_version = version_str
            if response_data:
                # 标记文件解析完成
                pdf_file.queue_order = 0
                pdf_file.progress = 100
                pdf_file.finish_analyze_time = datetime.now()
                pdf_file.save()

                # 指定存储路径
                upload_dir = settings.PATH_JSON_CPPQCP
                os.makedirs(upload_dir, exist_ok=True)
                json_file_path = os.path.join(upload_dir, f"{pdf_file.id}_{version_number}_result.json")

                os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(response_data, json_file, ensure_ascii=False, indent=4)
                order_in_file = 0
                # 更新 JsonFile 数据库记录
                json_file_instance = JsonFile.objects.create(
                    source_file=pdf_file,
                    analyze_version=version_str,
                    owner_file=pdf_file.name,
                    name=f"{pdf_file.id}_{version_number}_result",
                    file_path=upload_dir,
                    business_type="CPP&QCP",
                    # section_cnt=len(response_data.get("sections", [])),
                    # paragraph_cnt=sum(len(section.get("paragraphs", [])) for section in response_data.get("sections", [])),
                    # table_cnt=sum(len(section.get("tables", [])) for section in response_data.get("sections", [])),
                    # image_cnt=sum(len(section.get("images", [])) for section in response_data.get("sections", []))
                )

                # 逐个处理 sections 数据
                order_of_section = 0
                contains_st = False
                has_xbar = False
                for section_data in response_data:
                    order_in_file += 1
                    order_of_section += 1
                    sts = section_data.get("contains_st", [])
                    value_st = section_data.get("name", "")
                    if sts and len(sts) > 0:
                        contains_st =True
                        for st_item in sts:
                            strike_text = st_item.get("strike_text", "")
                            if strike_text in value_st:
                                value_st = value_st.replace(strike_text, "")
                    xbars = section_data.get("contains_xbar", [])
                    value_xbar = value_st
                    # 检查并处理 contains_xbar 属性
                    if xbars and len(xbars) > 0:
                        has_xbar = True
                        for xbar_item in xbars:
                            for content in xbar_item.get("content", []):
                                which_word = content.get("which_word_has_xbar", "")
                                # 替换去掉 "bar" 的内容
                                modified_word = which_word.replace("bar", "")
                                if which_word in value_xbar:
                                    value_xbar = value_xbar.replace(modified_word, which_word)
                    json_section = JsonSection.objects.create(
                        recognition_result=json_file_instance,
                        page=section_data.get("page", 0),
                        polygon=self.process_polygon(section_data.get("polygon", {})),
                        num=section_data.get("num", 0),
                        value=section_data.get("name", ""),
                        ch_value=section_data.get("ch_value", ""),
                        thai_value=section_data.get("thai_value", ""),
                        order_in_file=order_in_file,
                        order_of_section=order_of_section,
                        has_strike_through=contains_st,
                        has_xbar=has_xbar,
                        true_value=value_xbar,
                        true_ch_value=section_data.get("ch_value", ""),
                        true_thai_value = section_data.get("thai_value", "")
                    )

                    order_of_content = 1
                    order_in_file += 1
                    # 处理每个 section 下的 contents
                    contents = section_data.get("content", [])
                    json_content = JsonContent.objects.create(
                        section=json_section,
                        order_in_file=order_in_file,
                        order_of_content=order_of_content
                    )
                    order_of_element = 0
                    for content_data in contents:
                        order_of_element += 1
                        order_in_file += 1
                        contains_st = False
                        has_xbar = False
                        content_type = content_data.get("type")
                        if content_type == "Paragraph-text" or content_type == "Paragraph":
                            sts = content_data.get("contains_st", [])
                            value_st = content_data.get("value", "")
                            if sts and len(sts) > 0:
                                contains_st = True
                                for st_item in sts:
                                    strike_text = st_item.get("strike_text", "")
                                    if strike_text in value_st:
                                        value_st = value_st.replace(strike_text, "")
                            xbars = section_data.get("contains_xbar", [])
                            value_xbar = value_st
                            # 检查并处理 contains_xbar 属性
                            if xbars and len(xbars) > 0:
                                has_xbar = True
                                for xbar_item in xbars:
                                    for content in xbar_item.get("content", []):
                                        which_word = content.get("which_word_has_xbar", "")
                                        # 替换去掉 "bar" 的内容
                                        modified_word = which_word.replace("bar", "")
                                        if which_word in value_xbar:
                                            value_xbar = value_xbar.replace(modified_word, which_word)
                            JsonParagraph.objects.create(
                                content=json_content,
                                page=content_data.get("page", 0),
                                value=content_data.get("value", ""),
                                ch_value=content_data.get("ch_value", ""),
                                thai_value=content_data.get("thai_value", ""),
                                polygon=self.process_polygon(content_data.get("polygon", {})),
                                order_in_file=order_in_file,
                                order_of_element=order_of_element,
                                has_strike_through=contains_st,
                                has_xbar=has_xbar,
                                true_value=value_xbar,
                                true_ch_value=content_data.get("ch_value", ""),
                                true_thai_value=content_data.get("thai_value", "")
                            )
                        elif content_type == "Table":
                            json_table = JsonTable.objects.create(
                                content=json_content,
                                page=content_data.get("page", 0),
                                rows_num=content_data.get("rows_num", 0),
                                cols_num=content_data.get("cols_num", 0),
                                polygon=self.process_polygon(content_data.get("polygon", {})),
                                order_in_file=order_in_file,
                                order_of_element=order_of_element
                            )
                            cells_contains_image = content_data.get("image_tag", []) or []
                            cells_contains_st = content_data.get("contains_st", []) or []
                            cells_contains_xbar = content_data.get("contains_xbar", []) or []
                            cells_data = content_data.get("value", []) or []
                            order_of_cell = 0
                            for cell in cells_data:
                                row_span = cell.get("rowSpan", 1) or 1
                                col_span = cell.get("colSpan", 1) or 1
                                base_row_index = cell.get("rowIndex", 0)  # 基础行索引
                                col_index = cell.get("columnIndex", 0)  # 列索引

                                # 检查是否为图片单元格
                                is_image_cell = any(
                                    image_cell.get("rowIndex") == base_row_index and image_cell.get(
                                        "columnIndex") == col_index
                                    for image_cell in cells_contains_image
                                )

                                # 检查是否为划线文本单元格
                                is_st_cell = any(
                                    st_cell.get("rowIndex") == base_row_index and st_cell.get("columnIndex") == col_index
                                    for st_cell in cells_contains_st
                                )

                                # 检查是否为 XBar 单元格
                                is_xbar_cell = any(
                                    xbar_cell.get("rowIndex") == base_row_index and xbar_cell.get(
                                        "columnIndex") == col_index
                                    for xbar_cell in cells_contains_xbar
                                )

                                # 根据行跨度创建多个单元格
                                for span in range(row_span):
                                    # 获取 boundingRegions 的 pageNumber 和 polygon
                                    bounding_regions = cell.get("boundingRegions", [])
                                    page = bounding_regions[0].get("pageNumber", 0) if bounding_regions and isinstance(
                                        bounding_regions[0], dict) else 0
                                    polygon = self.process_polygon_spc(
                                        bounding_regions[0].get("polygon", [])) if bounding_regions else []
                                    is_virtual = False
                                    if span > 0:
                                        is_virtual = True
                                    # 设置单元格类型和内容
                                    cell_type = 0  # 默认文本类型
                                    value = cell.get("content", "")
                                    ch_value = cell.get("content_ch", "")
                                    thai_value = cell.get("thai_value", "")
                                    true_value = value
                                    true_ch_value = ch_value
                                    true_thai_value = thai_value
                                    image_bytes = None
                                    has_strike_through = False
                                    has_xbar = False

                                    # 特殊处理图片单元格
                                    if is_image_cell:
                                        image_cell = next(
                                            img for img in cells_contains_image if
                                            img.get("rowIndex") == base_row_index and img.get("columnIndex") == col_index
                                        )
                                        cell_type = 1  # 图片类型
                                        image_bytes = self.decode_image(image_cell.get("image_bytes", None))

                                    # 特殊处理划线文本单元格
                                    if is_st_cell:
                                        # 获取所有满足条件的划线文本单元格
                                        matched_st_cells = [
                                            st for st in cells_contains_st
                                            if st.get("rowIndex") == base_row_index and st.get("columnIndex") == col_index
                                        ]

                                        has_strike_through = True

                                        # 收集所有的 strike_text
                                        strike_texts = []
                                        for st_cell in matched_st_cells:
                                            strike_texts.extend(
                                                content.get("strike_text", "") for content in st_cell.get("content", [])
                                            )

                                        # 删除 strike_text 中的文本
                                        for strike_text in strike_texts:
                                            if strike_text in true_value:
                                                true_value = true_value.replace(strike_text, "")  # 删除划线文本

                                    # 特殊处理 XBar 单元格
                                    if is_xbar_cell:
                                        # 获取所有匹配的 XBar 单元格
                                        matched_xbar_cells = [
                                            xb for xb in cells_contains_xbar
                                            if xb.get("rowIndex") == base_row_index and xb.get("columnIndex") == col_index
                                        ]

                                        has_xbar = True

                                        # 收集所有的 "which_word_has_xbar"，并处理替换逻辑
                                        for xbar_cell in matched_xbar_cells:
                                            for content in xbar_cell.get("content", []):
                                                which_word = content.get("which_word_has_xbar", "")
                                                # 替换去掉 "bar" 的内容
                                                modified_word = which_word.replace("bar", "")
                                                if modified_word in true_value:
                                                    # 替换 modified_word 为原始的 which_word
                                                    true_value = true_value.replace(modified_word, which_word)

                                    order_in_file += 1
                                    order_of_cell += 1
                                    # 创建单元格
                                    JsonTableCell.objects.create(
                                        table=json_table,
                                        page=page,
                                        cell_type=cell_type,
                                        value=value,
                                        ch_value=ch_value,
                                        thai_value=thai_value,
                                        image_bytes=image_bytes,
                                        row_index=base_row_index + span,  # 动态计算行索引
                                        col_index=col_index,
                                        row_span=row_span,
                                        col_span=col_span,
                                        polygon=polygon,
                                        order_in_file=order_in_file,
                                        order_of_cell=order_of_cell,
                                        has_strike_through=has_strike_through,
                                        has_xbar=has_xbar,
                                        true_value=true_value,
                                        true_ch_value=true_ch_value,
                                        true_thai_value=true_thai_value,
                                        is_virtual=is_virtual
                                    )
                        elif content_type == "Image":
                            JsonImage.objects.create(
                            content=json_content,
                            page=content_data.get("page", 0),
                            image_bytes=self.decode_image(content_data.get("value", None)),
                            polygon = self.process_polygon(content_data.get("polygon", {})),
                            order_in_file = order_in_file,
                            order_of_element = order_of_element
                        )
            else:
                # 标记文件解析失败
                pdf_file.queue_order = -2
                pdf_file.progress = 0
                pdf_file.finish_analyze_time = datetime.now()
                pdf_file.save()
        except Exception as e:
            # 异常处理
            pdf_file.queue_order = -2
            pdf_file.progress = 0
            pdf_file.finish_analyze_time = datetime.now()
            pdf_file.save()
            raise e
        self.start_next_file()

    @action(methods=["GET"], detail=False)
    def schedule_parse(self, request):
        global parse_lock
        # 获取服务器地址前缀
        server_ip = socket.gethostbyname(socket.gethostname())  # 假设pdf_file对象中有一个server_ip属性存储服务器地址

        # 根据服务器前缀选择不同的接口
        if server_ip.startswith("172.30"):
            response_v = requests.get(f"http://172.16.94.134:8020/")

            response_v_data = response_v.json()
            version_str = response_v_data  # 默认版本号为 "v0.0.0"
        else:
            url_version = "http://localhost:7007/plugins/mock/version/"
            response_v = requests.get(url_version)
            response_v_data = response_v.json().get("version")

            # 提取版本号
            version_str = response_v_data
        # 获取文件 ID
        file_id = request.GET.get("id")
        if not file_id:
            return ErrorResponse(msg='文件 ID 缺失')

        try:
            pdf_file = PdfFile.objects.get(id=file_id)
        except PdfFile.DoesNotExist:
            return ErrorResponse(msg='文件不存在')

        if pdf_file.queue_order == 0 and pdf_file.analyze_version == version_str:
            return SuccessResponse(data=[], msg="已存在最新版本的解析，无需重新解析")

        with parse_lock:
            # 获取当前队列中的最大 queue_order
            max_queue_order = PdfFile.objects.aggregate(max_order=Max('queue_order'))['max_order'] or 0

            # 如果没有文件正在解析，直接将该文件置为解析中
            if not PdfFile.objects.filter(queue_order=1).exists():
                pdf_file.queue_order = 1
                pdf_file.start_analyze_time = datetime.now()
                pdf_file.save()
                # 开启异步任务
                threading.Thread(target=self.process_file, args=(pdf_file,)).start()
                return SuccessResponse(data=[], msg=f"文件已加入解析队列，队列位置 {pdf_file.queue_order}")

            # 否则，加入队列，设置 queue_order 为最大值加 1
            pdf_file.queue_order = max_queue_order + 1
            pdf_file.save()
        return SuccessResponse(data=[], msg=f"文件已加入解析队列，队列位置 {pdf_file.queue_order}")

    def start_next_file(self):
        """处理队列中的下一个文件"""
        next_file = PdfFile.objects.filter(queue_order__gt=1).order_by("queue_order").first()
        if next_file:
            # 将下一个文件标记为解析中
            next_file.start_analyze_time = datetime.now()
            next_file.queue_order = 1
            next_file.save()
            # 开始解析
            self.process_file(next_file)


