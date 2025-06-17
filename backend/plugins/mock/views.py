import asyncio
import os
import json
from django.http import JsonResponse


async def delayed_response(request):
    # 模拟 20 秒延迟
    await asyncio.sleep(1)

    # 指定 JSON 文件路径
    json_file_path = "F:\\sample4.json"
    # json_file_path = "F:\\stack.json"

    try:
        # 打开并读取 JSON 文件
        with open(json_file_path, 'r', encoding='UTF-8') as json_file:
            json_data = json.load(json_file)

        return JsonResponse(
            json_data,
            safe=False  # 如果 JSON 文件的内容是列表，需设置 safe=False
        )
    except FileNotFoundError:
        return JsonResponse(
            {"status": "error", "message": "JSON file not found"},
            status=404
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON format"},
            status=400
        )


def get_version(request):
    version_info = {
        "version": "v0.3.1",
        "description": "Mock API for versioning",
        "release_date": "2024-11-01"
    }
    return JsonResponse(version_info)