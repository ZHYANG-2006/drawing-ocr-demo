import hashlib
import os
from django.conf import settings

from rest_framework import serializers

from sma.system.models.system import FileList
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet


class FileSerializer(CustomModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, instance):
        # 获取当前请求的完整域名，包括协议和主机
        request = self.context.get('request')
        if request is not None:
            # 获取完整的主机地址（包括协议和域名）
            full_url = request.build_absolute_uri(settings.MEDIA_URL)
            return f'{full_url}{str(instance.url)}'
        else:
            # 如果 request 不存在，返回相对路径
            return f'{settings.MEDIA_URL}{str(instance.url)}'


    class Meta:
        model = FileList
        fields = "__all__"

    def create(self, validated_data):
        file_engine = 'local'
        file = self.initial_data.get('file')  # 获取上传的文件对象
        file_size = file.size
        validated_data['name'] = str(file)  # 保留文件的原始名称
        validated_data['size'] = file_size

        # 计算文件的 MD5 哈希值
        md5 = hashlib.md5()
        for chunk in file.chunks():
            md5.update(chunk)
        md5sum = md5.hexdigest()  # 得到文件的 MD5 哈希值

        # 获取文件的扩展名
        ext = os.path.splitext(file.name)[1]  # 提取文件扩展名 (如 .jpg, .png)

        # 使用 MD5 哈希值作为文件名，保留文件扩展名
        unique_file_name = f'{md5sum}{ext}'

        # 构建文件保存路径
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)  # 创建 uploads 目录（如不存在）

        # 文件的完整保存路径
        file_path = os.path.join(upload_dir, unique_file_name)

        # 将文件保存到磁盘
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 存储文件相对于 MEDIA_ROOT 的相对路径
        relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT).replace('\\', '/')
        validated_data['url'] = f'uploads/{unique_file_name}'  # 存储相对路径

        # 设置其他文件信息
        validated_data['md5sum'] = md5sum
        validated_data['engine'] = file_engine
        validated_data['mime_type'] = file.content_type

        # 审计字段
        try:
            request_user = self.request.user
            validated_data['dept_belong_id'] = request_user.dept.id
            validated_data['creator'] = request_user.id
            validated_data['modifier'] = request_user.id
        except:
            pass

        # 保存数据
        return super().create(validated_data)


class FileViewSet(CustomModelViewSet):
    """
    文件管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = FileList.objects.all()
    serializer_class = FileSerializer
    filter_fields = ['name', ]
    permission_classes = []