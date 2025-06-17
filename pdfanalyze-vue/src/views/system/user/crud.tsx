import { ref, reactive } from 'vue';
import * as api from './api';
import { message } from 'ant-design-vue';
import { AddReq, DelReq, EditReq } from '/@/types/crudTypes';

export const createCrudOptions = () => {
    const dataSource = ref([]);
    const pagination = reactive({
        current: 1,
        pageSize: 10,
        total: 0,
    });
    const form = reactive({
        id: '',
        username: '',
        name: '',
        dept: null,
        role: [],
        gender: '',
        email: '',
        is_active: true,
    });

    const deptOptions = ref([]);
    const roleOptions = ref([]);

    // 获取部门和角色选项
    const getDeptOptions = async () => {
        const res = await api.GetDept({
            page: {
                pageNumber: pagination.current,
                pageSize: pagination.pageSize,
            },
        });
        if (res.code === 2000) {
            deptOptions.value = res.data;
        }
    };

    const getRoleOptions = async (id: number) => {
        const res = await api.GetRoles(id);
        if (res.code === 2000) {
            roleOptions.value = res.data;
        }
    };

    const fetchData = async (query = {}) => {
        const res = await api.GetList({
            page: {
                pageNumber: pagination.current,
                pageSize: pagination.pageSize,
            },
        });
        dataSource.value = res.data;
        pagination.total = res.total;
    };

    const addData = async (form: AddReq) => {
        await api.AddObj(form);
        message.success('添加成功');
        fetchData();
    };

    const editData = async (form: EditReq) => {
        await api.UpdateObj(form);
        message.success('更新成功');
        fetchData();
    };

    const delData = async (id: DelReq) => {
        await api.DelObj(id);
        message.success('删除成功');
        fetchData();
    };

    return {
        dataSource,
        pagination,
        form,
        deptOptions,
        roleOptions,
        fetchData,
        addData,
        editData,
        delData,
        getDeptOptions,
        getRoleOptions,
    };
};
