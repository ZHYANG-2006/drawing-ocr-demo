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
from django.utils import timezone
from django.conf import settings
from datetime import datetime

from sma.system.models import STACKJsonTableCell
from sma.system.models.stack import STACKPdfFile, STACKJsonFile, STACKJsonTable, STACKJsonContent, Material

# 假设原先的解析逻辑写在以下函数中
# from .views import

task_queue = queue.Queue()

def parse_file_in_worker(pdf_file_id):
    """
    从队列取到任务后执行的解析逻辑。
    注意：因为工作线程与 Django ORM 交互，需要用 id 再次获取 model 实例，
    避免跨线程直接使用不安全的 model 实例。
    """
    try:
        pdf_file = STACKPdfFile.objects.get(id=pdf_file_id)
        # 获取服务器地址前缀
        server_ip = socket.gethostbyname(socket.gethostname())  # 假设pdf_file对象中有一个server_ip属性存储服务器地址

        # 根据服务器前缀选择不同的接口
        if server_ip.startswith("172.30"):
            # 服务器前缀为 172，调用真实接口
            url_analyze = "http://172.16.94.134:5030/analyze"
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
            response_v = requests.get(f"http://172.16.94.134:5030/")
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
            upload_dir = settings.PATH_JSON_STACK
            os.makedirs(upload_dir, exist_ok=True)
            json_file_path = os.path.join(upload_dir, f"{pdf_file.id}_{version_number}_result.json")

            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(response_data, json_file, ensure_ascii=False, indent=4)
            pattern = re.compile(r'^[0-9\-]+$')

            # 为防止重复添加，用一个临时集合记录已经找到的 Material
            material_objs = []

            for mat_str in response_data.get("materials", []):
                if pattern.match(mat_str):
                    # 如果完全匹配数字和-
                    # 优先去 Material.number 里找
                    material_obj, created = Material.objects.get_or_create(
                        creator=pdf_file.creator,
                        number=mat_str,
                        defaults={"name": mat_str},  # 也可给个默认 name
                    )
                else:
                    # 否则去匹配 Material.name
                    material_obj, created = Material.objects.get_or_create(
                        creator=pdf_file.creator,
                        name=mat_str,
                        defaults={"number": mat_str}  # 看业务需求，number 不一定要存这个
                    )
                material_objs.append(material_obj)

            pdf_file.materials.add(*material_objs)
            pdf_file.save()
            order_in_file = 0
            # 更新 JsonFile 数据库记录
            json_file_instance = STACKJsonFile.objects.create(
                source_file=pdf_file,
                analyze_version=version_str,
                owner_file=pdf_file.name,
                name=f"{pdf_file.id}_{version_number}_result",
                file_path=upload_dir,
                business_type="STACK",
            )
            # 逐个处理 sections 数据
            order_of_section = 0
            contains_st = False
            has_xbar = False
            page_number = 0
            for table_data in response_data.get("content", []):
                order_in_file = order_in_file + 1
                order_of_content = 1
                json_content = STACKJsonContent.objects.create(
                    json_file=json_file_instance,
                )
                json_table = STACKJsonTable.objects.create(
                    json_content=json_content,
                    rows_num=table_data.get("rows", 0),
                    cols_num=table_data.get("cols", 0),
                )
                order_of_element = 0
                count = 1
                for cell in table_data.get("cells", []):
                    order_of_element += 1
                    order_in_file += 1
                    STACKJsonTableCell.objects.create(
                        table=json_table,
                        row_index=cell.get("row_index", 0),
                        col_index=cell.get("col_index", 0),
                        row_span=cell.get("row_span", 0),
                        col_span=cell.get("col_span", 0),
                        type=cell.get("type", None),
                        bg_color=cell.get("bg_color", None),
                        font_color=cell.get("font_color", None),
                        value=cell.get("value", None),
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
        STACKPdfFile.objects.filter(id=pdf_file_id).update(
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
