# -*- coding: utf-8 -*-

"""
@Remark: 操作日志管理
"""

from sma.system.models.system import OperationLog
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet


class OperationLogSerializer(CustomModelSerializer):
    """
    日志-序列化器
    """

    class Meta:
        model = OperationLog
        fields = "__all__"
        read_only_fields = ["id"]

    def validate(self, attrs):
        # 检查 dept_belong_id 是否为空
        if not attrs.get('dept_belong_id'):
            attrs['dept_belong_id'] = 1  # 设置默认值

        # 处理其他可能为空的字段
        return attrs

class OperationLogCreateUpdateSerializer(CustomModelSerializer):
    """
    操作日志  创建/更新时的列化器
    """

    class Meta:
        model = OperationLog
        fields = '__all__'


class OperationLogViewSet(CustomModelViewSet):
    """
    操作日志接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = OperationLog.objects.order_by('-create_datetime')
    serializer_class = OperationLogSerializer
    # permission_classes = []
