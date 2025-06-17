import { reactive, ref } from 'vue';
import * as api from './api';
import { message } from 'ant-design-vue';
import { AddReq, EditReq, DelReq } from '/@/types/crudTypes';
import { DefaultOptionType } from 'ant-design-vue/es/select';

export const createCrudOptions = () => {
  const dataSource = ref([]);
  const apiOptions = ref<DefaultOptionType[]>([]); // 动态接口地址选项
  const isApiOptionsLoading = ref(false); // 动态加载状态
  const pagination = reactive({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  const fetchData = async () => {
    const res = await api.GetList({
      page: {
        pageNumber: pagination.current,
        pageSize: pagination.pageSize,
      },
    });
    dataSource.value = res.data;
    pagination.total = res.total;
  };

  // 动态加载接口地址选项
  const loadApiOptions = async () => {
    isApiOptionsLoading.value = true;
    try {
      apiOptions.value = await api.LoadApiOptions();
    } catch (error) {
      message.error('加载接口地址失败');
    } finally {
      isApiOptionsLoading.value = false;
    }
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
    fetchData,
    apiOptions,
    isApiOptionsLoading,
    loadApiOptions,
    addData,
    editData,
    delData,
  };
};
