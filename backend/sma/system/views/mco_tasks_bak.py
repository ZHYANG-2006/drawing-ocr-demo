# tasks.py
import socket
import requests
import queue
import threading
import os
import re
import json
import time
import traceback
import pymysql
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from conf.env import *

from sma.system.models.mco import MCOPdfFile, MCOJsonFile, MCOJsonPage, MCOJsonContent, MCOJsonParagraph

# 假设原先的解析逻辑写在以下函数中
# from .views import

task_queue = queue.Queue()


def process_polygon(polygon):
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
                left_top = min(unique_points, key=lambda p: (p[0], p[1]))  # 左上
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

def fetch_jade_rpa_info(mco_pn: str):
    """
    根据 MCO_PN 去 MySQL 查询 InternalProject / CustomerPN / Internal_ModelCode
    :return: dict 或 None
    """
    sql = """
        SELECT InternalProject, CustomerPN, Internal_ModelCode
        FROM Jade_RPA
        WHERE MCO_PN = %s
        LIMIT 1
    """
    conn = pymysql.connect(**MYSQL_CFG)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (mco_pn,))
            row = cur.fetchone()
            if row:
                return {
                    "internal_project": row[0],
                    "customer_pn": row[1],
                    "internal_model_code": row[2],
                }
    finally:
        conn.close()
    return None

def parse_file_in_worker(pdf_file_id):
    """
    从队列取到任务后执行的解析逻辑。
    注意：因为工作线程与 Django ORM 交互，需要用 id 再次获取 model 实例，
    避免跨线程直接使用不安全的 model 实例。
    """
    try:
        pdf_file = MCOPdfFile.objects.get(id=pdf_file_id)
        # 获取服务器地址前缀
        server_ip = socket.gethostbyname(socket.gethostname())  # 假设pdf_file对象中有一个server_ip属性存储服务器地址

        # 根据服务器前缀选择不同的接口
        if server_ip.startswith("172.30"):
            # 服务器前缀为 172，调用真实接口
            url_analyze = "http://172.16.94.134:5020/analyze"
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
            response_v = requests.get(f"http://172.16.94.134:5020/")
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
            upload_dir = settings.PATH_JSON_MCO
            os.makedirs(upload_dir, exist_ok=True)
            json_file_path = os.path.join(upload_dir, f"{pdf_file.id}_{version_number}_result.json")

            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(response_data, json_file, ensure_ascii=False, indent=4)
            order_in_file = 0
            # 更新 JsonFile 数据库记录
            json_file_instance = MCOJsonFile.objects.create(
                source_file=pdf_file,
                analyze_version=version_str,
                owner_file=pdf_file.name,
                name=f"{pdf_file.id}_{version_number}_result",
                file_path=upload_dir,
                business_type="MCO",
            )
            # 逐个处理 sections 数据
            order_of_section = 0
            contains_st = False
            has_xbar = False
            page_number = 0
            for page in response_data:
                page_number = page_number + 1
                json_page = MCOJsonPage.objects.create(
                    recognition_result=json_file_instance,
                    page=page_number,
                )
                order_in_file = order_in_file + 1
                order_of_content = 1
                contents = page.get("content", [])
                json_content = MCOJsonContent.objects.create(
                    page=json_page,
                    order_in_file=order_in_file,
                    order_of_content=order_of_content
                )
                order_of_element = 0
                count = 1
                for content_data in contents:
                    if count == 1:
                        lines = [line.strip() for line in content_data.get("value", "").strip().split('\n')]

                        title = lines[0].split(':', 1)[1].strip()
                        drawing_number = lines[1].split(':', 1)[1].strip()
                        rev = lines[2].split(':', 1)[1].strip()
                        drawing_number = drawing_number.replace(" ", "")
                        mco_pn = f"{drawing_number}-{rev}"
                        jade_info = fetch_jade_rpa_info(mco_pn)
                        json_file_instance.title = title
                        json_file_instance.drawing_number = drawing_number
                        json_file_instance.rev = rev
                        if jade_info:
                            json_file_instance.internal_code = jade_info["internal_project"]
                            json_file_instance.flex_part_number = jade_info["customer_pn"]
                            json_file_instance.project_description = jade_info["internal_model_code"]
                        json_file_instance.save()
                        pdf_file.title = title
                        pdf_file.drawing_number = drawing_number
                        pdf_file.rev = rev
                        if jade_info:
                            pdf_file.internal_code = jade_info["internal_project"]
                            pdf_file.flex_part_number = jade_info["customer_pn"]
                            pdf_file.project_description = jade_info["internal_model_code"]
                        pdf_file.save()
                        count += 1
                        continue
                    order_of_element += 1
                    order_in_file += 1
                    content_type = content_data.get("type")
                    if content_type == "Paragraph-text" or content_type == "Paragraph":
                        value = content_data.get("value", "")

                        # 确保字符串是 UTF-8 并手动解码
                        if isinstance(value, bytes):
                            value = value.decode("utf-8")  # 避免错误编码存入 Oracle
                        MCOJsonParagraph.objects.create(
                            content=json_content,
                            page=content_data.get("page", 0),
                            value=value,
                            # ch_value=content_data.get("ch_value", ""),
                            polygon=process_polygon(content_data.get("polygon", {})),
                            order_in_file=order_in_file,
                            order_of_element=order_of_element,
                            pdf = pdf_file,
                            pdf_name = pdf_file.name,
                            title = pdf_file.title,
                            drawing_number = pdf_file.drawing_number,
                            rev = pdf_file.rev,
                            internal_code = pdf_file.internal_code,
                            flex_part_number = pdf_file.flex_part_number,
                            project_description = pdf_file.project_description,
                            num=content_data.get("num", 0),
                        )
        else:
            # 标记文件解析失败
            pdf_file.queue_order = -2
            pdf_file.progress = 0
            pdf_file.finish_analyze_time = datetime.now()
            pdf_file.save()
    except Exception as e:
        # 如果解析失败，做好异常记录，避免线程崩溃退出
        traceback.print_exc()
        # 标记任务为解析失败
        MCOPdfFile.objects.filter(id=pdf_file_id).update(
            progress=0,
            queue_order=-2,
            finish_analyze_time=timezone.now()
        )

def parse_worker():
    """
    单线程工作函数：循环从队列中获取文件ID并进行解析
    """
    while True:
        pdf_file_id = task_queue.get()  # 阻塞等待
        if pdf_file_id is None:
            # 约定：收到 None 表示 worker 要退出
            break

        parse_file_in_worker(pdf_file_id)

        # 通知队列任务已完成
        task_queue.task_done()


# 创建并启动后台线程（daemon=True 表示主进程退出后，该线程自动结束）
worker_thread = threading.Thread(target=parse_worker, daemon=True)
worker_thread.start()
