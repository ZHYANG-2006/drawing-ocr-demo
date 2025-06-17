<template>
  <div>
    <a-button type="primary" @click="showAddModal">添加按钮</a-button>
    <a-table
      :columns="columns"
      :data-source="dataSource"
      row-key="id"
      :pagination="false"
      :scroll="{ y: '70vh' }"
      style="min-height: 70vh"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === 'index'">
          {{ index + 1 }}
        </template>
        <template v-if="column.key === 'method'">
          <a-tag
            :key="`${index}-${record.method}`"
            :color="getColor(record.method)"
          >
            {{ getMethodName(record.method).toUpperCase() }}
          </a-tag>
        </template>
        <template v-if="column.key === 'operation'">
          <span>
            <a-button type="primary" size="small" @click="editOper(record.id)">
              编辑
            </a-button>
            <a-popconfirm
              title="是否确认删除?"
              @confirm="deleteOper(record.id)"
            >
              <a-button type="primary" size="small" class="ml-2" danger>
                删除
              </a-button>
            </a-popconfirm>
          </span>
        </template>
      </template>
    </a-table>

    <!-- 添加/编辑对话框 -->
    <a-modal
      v-model:open="isModalVisible"
      title="添加/编辑菜单按钮"
      @ok="handleSubmit"
    >
      <a-form :model="formState">
        <a-form-item
          label="权限名称"
          name="name"
          :rules="[{ required: true, message: '请输入权限名称' }]"
        >
          <a-input
            v-model:value="formState.name"
            placeholder="请输入权限名称"
          />
        </a-form-item>
        <a-form-item
          label="权限值"
          name="value"
          :rules="[{ required: true, message: '请输入权限值' }]"
        >
          <a-input v-model:value="formState.value" placeholder="请输入权限值" />
        </a-form-item>
        <a-form-item
          label="请求方式"
          name="method"
          :rules="[{ required: true, message: '请选择请求方式' }]"
        >
          <a-select v-model:value="formState.method">
            <a-select-option value="0">GET</a-select-option>
            <a-select-option value="1">POST</a-select-option>
            <a-select-option value="2">PUT</a-select-option>
            <a-select-option value="3">DELETE</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item
          label="接口地址"
          name="api"
          :rules="[{ required: true, message: '请输入接口地址' }]"
        >
          <a-select
            v-model:value="formState.api"
            placeholder="请选择接口地址"
            allowClear
            showSearch
            :options="crud.apiOptions.value"
            :loading="crud.isApiOptionsLoading.value"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted, UnwrapRef } from 'vue';
  import { message, Modal } from 'ant-design-vue';
  import * as api from './api';
  import cloneDeep from 'lodash-es';
  import { createCrudOptions } from './crud';
  import { MenuTreeItemType } from '/@/views/system/menu/types';
  import type {
    DataNode,
    DirectoryTreeProps,
    EventDataNode,
  } from 'ant-design-vue/lib/tree';

  const crud = createCrudOptions();
  // 定义映射表
  const methodMap = {
    0: 'GET',
    1: 'POST',
    2: 'PUT',
    3: 'DELETE',
  };

  // 定义颜色分配逻辑
  const getColor = (method: number) => {
    switch (method) {
      case 0: // GET
        return 'green';
      case 1: // POST
        return 'blue';
      case 2: // PUT
        return 'orange';
      case 3: // DELETE
        return 'red';
      default:
        return 'default'; // 默认颜色
    }
  };

  // 方法名映射函数
  const getMethodName = (method: number) => {
    return methodMap[method as keyof typeof methodMap] || 'UNKNOWN';
  };

  // 表单数据
  interface FormState {
    id: string;
    name: string;
    menu: string;
    value: string;
    method: string;
    api: string;
  }

  const selectOptions = ref<{
    name: string | null;
    id: number | string | null;
  }>({
    name: null,
    id: null,
  });

  const formState: UnwrapRef<FormState> = reactive({
    id: '',
    menu: '',
    name: '',
    value: '',
    method: '',
    api: '',
  });

  const data: FormState[] = [];
  const dataSource = ref(data);
  const isModalVisible = ref(false);
  const editableData: UnwrapRef<Record<string, FormState>> = reactive({});

  const columns = [
    { title: '序号', dataIndex: 'index', key: 'index', width: 100 },
    { title: '权限名称', dataIndex: 'name', key: 'name' },
    { title: '权限值', dataIndex: 'value', key: 'value' },
    { title: '请求方式', dataIndex: 'method', key: 'method' },
    { title: '接口地址', dataIndex: 'api', key: 'api' },
    { title: '操作', key: 'operation', width: 300 },
  ];

  const fetchData = async () => {
    if (selectOptions.value.id) {
      const res = await api.GetList({ menu: selectOptions.value.id });
      dataSource.value = res.data;
      console.log('datasource', dataSource.value);
    }
  };

  const handleRefreshTable = (record?: DataNode) => {
    console.log("l'm here");
    if (record && !record.is_catalog && record.id && record.name) {
      // 将 record 的 name 和 id 赋值给 selectOptions
      selectOptions.value = {
        name: record.name, // 确保 name 是 string 类型
        id: record.id, // 确保 id 是 string 类型
      };

      // 手动触发表格数据刷新，比如重新获取数据
      fetchData();
    } else {
      // 清空表格数据
      dataSource.value = [];
    }
  };

  const showAddModal = () => {
    console.log('formstate', formState);
    Object.assign(formState, {
      menu: selectOptions.value.id,
      name: '',
      value: '',
      method: '',
      api: '',
    });
    isModalVisible.value = true;
  };

  const handleSubmit = async () => {
    const { id } = formState; // 提取 key 和表单数据
    console.log('formstate', formState);
    if (!id) {
      // 添加逻辑
      await crud.addData(formState); // 添加时传递完整表单数据
      message.success('添加成功');
    } else {
      // 更新逻辑，构造符合 EditReq 的数据格式
      await crud.editData(formState); // 更新时传递 row 和 form
      message.success('更新成功');
    }
    isModalVisible.value = false; // 关闭模态框
    fetchData(); // 刷新表格数据
  };

  const editOper = (key: string) => {
    const item = dataSource.value.find((item) => key === item.id);
    if (item) {
      Object.assign(formState, item); // 将选中行的数据复制到 formState
      isModalVisible.value = true; // 显示模态框
    }
  };
  /*
  const editOper = (key: string) => {
    const item = dataSource.value.find((item) => key === item.key);
    if (item) {
      // 使用 double-cast 解决类型不兼容的问题
      editableData[key] = cloneDeep(item) as unknown as FormState;
    }
  };*/

  const deleteOper = async (key: string) => {
    const itemIndex = dataSource.value.findIndex((item) => key === item.id); // 找到索引
    if (itemIndex !== -1) {
      try {
        // 调用后端删除 API
        await crud.delData({ id: key });

        // 从前端数据源中移除对应项
        dataSource.value.splice(itemIndex, 1);
      } catch (error) {
        console.error('删除失败:', error);
        message.error('删除失败，请重试');
      }
    } else {
      message.warning('未找到要删除的数据项');
    }
  };

  const saveOper = (key: string) => {
    Object.assign(
      dataSource.value.filter((item) => key === item.id)[0],
      editableData[key],
    );
    delete editableData[key];
  };

  const cancelOper = (key: string) => {
    delete editableData[key];
  };

  onMounted(() => {
    crud.loadApiOptions();
    fetchData();
  });
  defineExpose({ selectOptions, handleRefreshTable });
</script>
