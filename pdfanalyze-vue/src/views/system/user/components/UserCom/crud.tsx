import { reactive, ref } from 'vue';
import * as api from './api';
import { message } from 'ant-design-vue';
import { AddReq, EditReq, DelReq } from '/@/types/crudTypes';
import { DefaultOptionType } from 'ant-design-vue/es/select';
import { LoadRoleOptions } from './api';
import XEUtils from 'xe-utils';

export const createCrudOptions = () => {
  interface DeptOption {
    id: number;
    name: string;
    parent: DeptOption | null;
    children?: DeptOption[]; // 子节点
  }

  const dataSource = ref([]);
  const roleOptions = ref<DefaultOptionType[]>([]); // 动态接口地址选项
  const isRoleOptionsLoading = ref(false); // 动态加载状态
  const deptOptions = ref<DeptOption[]>([]);
  const isDeptOptionsLoading = ref(false); // 动态加载状态
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
  const loadRoleOptions = async () => {
    isRoleOptionsLoading.value = true;
    try {
      const rst = await api.LoadRoleOptions();
      roleOptions.value = rst.data.map((item: { id: number; name: string }) => ({
        label: item.name, // 使用 name 作为显示文本
        value: item.id,   // 使用 id 作为绑定值
      }));
    } catch (error) {
      message.error('加载接口地址失败');
    } finally {
      isRoleOptionsLoading.value = false;
    }
  };

  const loadDeptOptions = async () => {
    isDeptOptionsLoading.value = true;
    try {
      const rst = await api.GetAllDept();
      const responseData = rst.data;
      console.log('responseData', responseData);
      const result = XEUtils.toArrayTree(responseData, {
        parentKey: 'parent',
        children: 'children',
      });
      // 创建一个 Map，以 ID 作为键，完整节点作为值
      const idMap = new Map<number, any>();
      responseData.forEach((node: any) => {
        idMap.set(node.id, node);
      });

      // 递归处理树形结构，将 parent 替换为对象
      const convertParentToObj = (node: any) => {
        if (node.parent !== null) {
          node.parent = idMap.get(node.parent) || null; // 将 parent ID 替换为对象
        }
        if (node.children) {
          node.children.forEach(convertParentToObj); // 递归处理子节点
        }
      };

      result.forEach(convertParentToObj);
      deptOptions.value = result;
      console.log('result with parent as object', result);
    } catch (error) {
      message.error('加载接口地址失败');
    } finally {
      isDeptOptionsLoading.value = false;
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
    roleOptions,
    isRoleOptionsLoading,
    loadRoleOptions,
    deptOptions,
    isDeptOptionsLoading,
    loadDeptOptions,
    addData,
    editData,
    delData,
  };
};
