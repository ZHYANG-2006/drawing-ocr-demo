import os

from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.decorators import action
from django.http import FileResponse
from application import settings
from sma.system.models.mco import MCOFileHistory
from sma.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet
from smb.SMBConnection import SMBConnection

class MCOFileHistorySerializer(CustomModelSerializer):
    """
    PdfFile 模型序列化器，继承自自定义序列化器
    """
    class Meta:
        model = MCOFileHistory
        fields = '__all__'  # 序列化所有字段
        read_only_fields = ['id', 'create_datetime', 'update_datetime']  # 设置只读字段

class MCOFileHistoryViewSet(CustomModelViewSet):
    """
    PdfFile 的视图集
    继承自 CustomModelViewSet，支持批量删除、过滤查询等
    """
    queryset = MCOFileHistory.objects.all()
    serializer_class = MCOFileHistorySerializer

    # 定义用于创建和更新的序列化器（如果与默认不同）
    create_serializer_class = MCOFileHistorySerializer
    update_serializer_class = MCOFileHistorySerializer

    # 定义过滤、搜索和排序字段
    search_fields = [
        'file_name',
        'drawing_number',
        'rev',
        'is_analyzed',
        'analyze_rst',
        'creator_name',
        'create_datetime',
        'creator_name',
        'creator',
        'uploader_name',
    ]

    ordering_fields = [
        'file_name',
        'drawing_number',
        'rev',
        'is_analyzed',
        'analyze_rst',
        'creator_name',
        'create_datetime',
        'creator_name',
        'creator',
        'uploader_name',
    ]

    @action(detail=False, methods=['post'])
    def sync_files(self, request):
        # 从配置或环境变量读取：
        user = '82304110'
        pwd = '1234@Zxcv'
        server_name = 'mfcisilon01.mflex.com.cn'
        server_ip = '172.16.65.163'
        share_name = 'Design_Tooling'
        subdir = 'Project_PDF'

        # 建立 SMB 连接
        conn = SMBConnection(user, pwd, 'django_client', server_name, use_ntlm_v2=True)
        if not conn.connect(server_ip, 445):
            return ErrorResponse(msg="无法连接到 SMB 服务器")

        try:
            entries = conn.listPath(share_name, subdir)
        except Exception as e:
            return ErrorResponse(msg=f"列举远程目录失败：{e}")

        created = []
        for entry in entries:
            if entry.isDirectory:
                continue
            fn = entry.filename
            # 解析 drawing_number 和 rev（同前面逻辑）
            name, _ = os.path.splitext(fn)
            parts = name.split('-', 2)
            if len(parts) >= 2:
                drawing_number = '-'.join(parts[:-1])
                rev = parts[-1]
            else:
                drawing_number = name
                rev = ''

            obj, _ = MCOFileHistory.objects.update_or_create(
                file_name=fn,
                defaults={'drawing_number': drawing_number, 'rev': rev}
            )
            created.append(obj)

        serializer = self.get_serializer(created, many=True)
        return SuccessResponse(data=serializer.data, msg="同步成功")

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