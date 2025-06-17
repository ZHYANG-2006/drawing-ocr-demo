# -*- coding: utf-8 -*-


from rest_framework.decorators import action

from sma.system.models.system import RoleMenuPermission
from sma.utils.json_response import DetailResponse, ErrorResponse
from sma.utils.serializers import CustomModelSerializer
from sma.utils.viewset import CustomModelViewSet


class RoleMenuPermissionSerializer(CustomModelSerializer):
    """
    菜单按钮-序列化器
    """

    class Meta:
        model = RoleMenuPermission
        fields = "__all__"
        read_only_fields = ["id"]

    def validate_role_id(self, value):
        if value == '' or value is None:
            return 1
        return value

    def validate_menu_id(self, value):
        if value == '' or value is None:
            return 1
        return value

    def validate_dept_belong_id(self, value):
        if value == '' or value is None:
            return 1
        return value

    def validate_creator_id(self, value):
        if value == '' or value is None:
            return 1
        return value

class RoleMenuPermissionInitSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """

    class Meta:
        model = RoleMenuPermission
        fields = "__all__"
        read_only_fields = ["id"]

class RoleMenuPermissionCreateUpdateSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """

    class Meta:
        model = RoleMenuPermission
        fields = "__all__"
        read_only_fields = ["id"]


class RoleMenuPermissionViewSet(CustomModelViewSet):
    """
    菜单按钮接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = RoleMenuPermission.objects.all()
    serializer_class = RoleMenuPermissionSerializer
    create_serializer_class = RoleMenuPermissionCreateUpdateSerializer
    update_serializer_class = RoleMenuPermissionCreateUpdateSerializer
    extra_filter_class = []

    @action(methods=['post'],detail=False)
    def save_auth(self,request):
        """
        保存页面菜单授权
        :param request:
        :return:
        """
        body = request.data
        role_id = body.get('role',None)
        if role_id is None:
            return ErrorResponse(msg="未获取到角色参数")
        menu_list = body.get('menu',None)
        if menu_list is None:
            return ErrorResponse(msg="未获取到菜单参数")
        obj_list = RoleMenuPermission.objects.filter(role__id=role_id).values_list('menu__id',flat=True)
        old_set = set(obj_list)
        new_set = set(menu_list)
        #need_update = old_set.intersection(new_set) # 需要更新的
        need_del = old_set.difference(new_set) # 需要删除的
        need_add = new_set.difference(old_set) # 需要新增的
        RoleMenuPermission.objects.filter(role__id=role_id,menu__in=list(need_del)).delete()
        data = [{"role": role_id, "menu": item} for item in list(need_add)]
        serializer = RoleMenuPermissionSerializer(data=data,many=True,request=request)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return DetailResponse(msg="保存成功",data=serializer.data)
