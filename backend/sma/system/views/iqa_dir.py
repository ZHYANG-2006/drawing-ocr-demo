import os
import shutil

import io
from django.http import HttpResponse
from datetime import datetime

import openpyxl
from openpyxl.workbook import Workbook
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.decorators import action

from application import settings
from sma.system.models.iqa import IqaDir, IqaPeakValue, IqaData, IqaFile
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet

from sma.utils.extract_utils import process_file, export_excel


class IqaDirSerializer(CustomModelSerializer):
    """
    IqaDir 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = IqaDir
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

class IqaDirViewSet(CustomModelViewSet):
    """
    IqaData 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = IqaDir.objects.all()
    serializer_class = IqaDirSerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = IqaDirSerializer
    update_serializer_class = IqaDirSerializer
    # 定义过滤、搜索和排序字段
    search_fields = [
        'verification_serial_number',
        'rubber_model',
        'material_number',
        'original_rubber_lot',
        'supplier',
        'measurement_count',
        'match_rate',
        'peak_value',
        'dir_type',
        'folder_name',
        'path',
        'create_datetime',
        'creator_name',
        'creator',
        'uploader_name',
    ]
    ordering_fields = [
        'verification_serial_number',
        'rubber_model',
        'material_number',
        'original_rubber_lot',
        'supplier',
        'measurement_count',
        'match_rate',
        'peak_value',
        'dir_type',
        'folder_name',
        'path',
        'create_datetime',
        'creator_name',
        'creator',
        'uploader_name',
    ]

    def create(self, request, *args, **kwargs):
        """
        自定义创建逻辑
        """
        files = request.FILES.getlist('file')  # 获取上传的文件
        if not files:
            return ErrorResponse(msg='请上传文件')
        # 指定存储路径
        upload_dir = os.path.join(settings.PATH_PDF_IQA, request.data.get('folder_name'))
        os.makedirs(upload_dir, exist_ok=True)
        dept = request.user.dept.dept_belong_id
        new_IqaDir = IqaDir.objects.create(
            dir_type = '',
            folder_name = request.data.get('folder_name'),
            path = upload_dir,
            uploader_name = request.user.name,
            file_count = len(files),
            dept_belong_id=dept,
        )
        for f in files:
            file_path = os.path.join(upload_dir, f.name)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            rst = {}
            try:
                rst = process_file(f)  # 可能发生异常
            except Exception as e:
                print(f"处理文件 {f.name} 时出错: {e}")
                rst = {}  # 发生错误时返回一个空字典，避免后续代码出错
                continue
            new_IqaFile = IqaFile.objects.create(
                iqa_dir = new_IqaDir,
                file_name = f.name,
                folder_name = request.data.get('folder_name'),
                path = file_path,
                uploader_name = request.user.name,
                dept_belong_id=dept,
            )
            if "detail_data" in rst:
                new_IqaDir.verification_serial_number = rst["verification_serial_number"]
                new_IqaDir.rubber_model = rst["rubber_model"]
                new_IqaDir.material_number = rst["material_number"]
                new_IqaDir.original_rubber_lot = rst["original_rubber_lot"]
                new_IqaDir.supplier = rst["supplier"]
                new_IqaDir.measurement_count = rst["measurement_count"]
                peak_values = rst["detail_data"]
                for value in peak_values:
                    new_IqaDir.dir_type = "peak"
                    new_IqaDir.save()
                    new_IqaFile.file_type = "peak"
                    new_IqaFile.save()
                    try:
                        new_IqaPeakValue = IqaPeakValue.objects.create(
                            iqa_file = new_IqaFile,
                            verification_serial_number = rst['verification_serial_number'],
                            rubber_model = rst['rubber_model'],
                            material_number = rst['material_number'],
                            original_rubber_lot = rst['original_rubber_lot'],
                            supplier = rst['supplier'],
                            measurement_count = rst['measurement_count'],
                            peak_value = value,
                            file_name = f.name,
                            folder_name = request.data.get('folder_name'),
                            path = file_path,
                            uploader_name = request.user.name,
                            dept_belong_id=dept,
                        )
                        new_IqaPeakValue.save()
                    except Exception as e:
                        print(f"创建 {f.name}IqaData 记录时出错: {e}")
            else:
                new_IqaDir.dir_type = "iqa"
                new_IqaDir.save()
                new_IqaFile.file_type = "iqa"
                new_IqaFile.save()

                # 如果 rst['supplier'] 为空，提取文件名的末尾部分作为供应商名称
                supplier = rst['supplier']
                if not supplier:  # 如果 supplier 为空
                    file_name_without_ext = os.path.splitext(f.name)[0]  # 去除文件后缀
                    supplier = file_name_without_ext.split()[-1]  # 取文件名空格分割的最后部分
                try:
                    new_IqaData = IqaData.objects.create(
                        iqa_file=new_IqaFile,
                        incoming_date=rst['incoming_date'],
                        verification_serial_number=rst['verification_serial_number'],
                        pn=rst['pn'],
                        original_rubber_model=rst['original_rubber_model'],
                        original_rubber_dc=rst['original_rubber_dc'],
                        supplier=supplier,  # 使用修正后的 supplier
                        match_rate=rst['match_rate'],
                        file_name=f.name,
                        folder_name=request.data.get('folder_name'),
                        path=file_path,
                        uploader_name=request.user.name,
                        dept_belong_id=dept,
                    )
                    new_IqaData.save()
                except Exception as e:
                    print(f"创建 {f.name}IqaData 记录时出错: {e}")
        return SuccessResponse(msg="文件上传成功")

    def list(self, request, *args, **kwargs):
        """
        重写list方法
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset()).order_by('-create_datetime')
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(serializer.data,msg="获取成功")

    def destroy(self, request, *args, **kwargs):
        """
        自定义删除逻辑：删除文件和数据库记录
        """
        pk = kwargs.get('pk')  # 从 kwargs 获取主键 (pk)

        try:
            # 获取要删除的 ReviewResult 对象
            instance = IqaDir.objects.get(pk=pk)
            folder_path = instance.path
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # 递归删除文件夹及其所有内容
                shutil.rmtree(folder_path)
                print(f"文件夹 {folder_path} 已删除.")
            else:
                print(f"指定路径 {folder_path} 不存在或不是文件夹.")
            # 删除数据库记录
            instance.delete()
            return SuccessResponse(data=[], msg="删除成功")
        except IqaDir.DoesNotExist:
            return ErrorResponse(msg=f"ReviewResult with pk {pk} does not exist")

    @action(detail=False, methods=['get'])
    def exportExcel(self, request):
        pk = request.GET.get('id')
        instance = IqaDir.objects.get(pk=pk)
        if instance.dir_type == "iqa":
            context = []
            iqafiles = instance.iqafiles.all()
            for file in iqafiles:
                try:
                    iqadata = file.iqadata
                    context.append({
                        "incoming_date": iqadata.incoming_date,
                        "verification_serial_number": iqadata.verification_serial_number,
                        "pn": iqadata.pn,
                        "original_rubber_model": iqadata.original_rubber_model,
                        "supplier": iqadata.supplier,
                        "original_rubber_dc": iqadata.original_rubber_dc,
                        "match_rate": iqadata.match_rate,
                    })
                except Exception as e:
                    continue
            wb = export_excel(context, 'iqa')

            # 3. 保存到内存并构造 HttpResponse
            output_stream = io.BytesIO()
            wb.save(output_stream)
            output_stream.seek(0)

            response = HttpResponse(
                content=output_stream.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response['Content-Disposition'] = 'attachment; filename="iqadir_export.xlsx"'
            return response
        else:
            context = []
            iqafiles = instance.iqafiles.all()
            for file in iqafiles:
                try:
                    # 收集当前 file 下的所有峰值信息
                    peaks = file.iqapeakvalues.all()
                    peaks_data = []
                    for peak in peaks:
                        peaks_data.append({

                            "peak_value": peak.peak_value,
                        })
                    peaks_data = sorted(peaks_data, key=lambda item: item["peak_value"])
                    context.append({
                        "verification_serial_number": peaks[0].verification_serial_number,
                        "rubber_model": peaks[0].rubber_model,
                        "material_number": peaks[0].material_number,
                        "original_rubber_lot": peaks[0].original_rubber_lot,
                        "supplier": peaks[0].supplier,
                        "measurement_count": peaks[0].measurement_count,
                        "peaks": peaks_data,
                    })
                except Exception as e:
                    continue
            wb = export_excel(context, 'peak')

            # 3. 保存到内存并构造 HttpResponse
            output_stream = io.BytesIO()
            wb.save(output_stream)
            output_stream.seek(0)

            response = HttpResponse(
                content=output_stream.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response['Content-Disposition'] = 'attachment; filename="iqadir_export.xlsx"'
            return response
