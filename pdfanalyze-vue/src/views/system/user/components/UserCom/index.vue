<template>
  <div>
    <a-button type="primary" @click="showAddModal">添加用户</a-button>
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
        <template v-if="column.key === 'role_info'">
          <span>
            <a-tag
              v-for="role in record.role_info"
              :key="role.id"
              :color="getTagColor(role.name)"
            >
              {{ role.name }}
            </a-tag>
          </span>
        </template>
        <template v-if="column.key === 'gender'">
          <a-tag :color="record.gender === 1 ? 'blue' : 'pink'">
            {{ record.gender === 1 ? '男' : '女' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'is_active'">
          <a-switch
            v-model:checked="record.is_active"
            @change="toggleStatus(record)"
          />
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
      title="添加/编辑用户"
      @ok="handleSubmit"
    >
      <a-form :model="formState">
        <a-form-item
          label="用户名"
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input
            v-model:value="formState.username"
            placeholder="请输入用户名"
          />
        </a-form-item>
        <a-form-item
          label="姓名"
          name="name"
          :rules="[{ required: true, message: '请输入姓名' }]"
        >
          <a-input v-model:value="formState.name" placeholder="请输入姓名" />
        </a-form-item>
        <a-form-item
          label="部门"
          name="dept"
          :rules="[{ required: true, message: '请选择部门' }]"
        >
          <a-tree-select
            v-model:value="formState.dept"
            :replace-fields="defaultTreeProps"
            :tree-data="crud.deptOptions.value"
            :placeholder="'请选择部门'"
            allow-clear
            style="width: 100%"
          >
            <template #title="{ key, name }">
              <span>{{ name }}</span>
            </template>
          </a-tree-select>
        </a-form-item>
        <a-form-item
          label="角色"
          name="role"
          :rules="[{ required: true, message: '请选择角色' }]"
        >
          <a-select
            v-model:value="formState.role"
            placeholder="请选择角色"
            allowClear
            showSearch
            :options="crud.roleOptions.value"
            :loading="crud.isRoleOptionsLoading.value"
            mode="multiple"
          />
        </a-form-item>
        <a-form-item
          label="密码"
          name="password"
          :rules="[
            { required: true, message: '请填写密码' },
            { min: 6, message: '密码长度至少为6位' },
          ]"
        >
          <a-input-password
            v-model:value="formState.password"
            placeholder="请输入密码"
            :visibilityToggle="false"
          />
        </a-form-item>
        <a-form-item
          label="性别"
          name="gender"
          :rules="[{ required: false, message: '请选择性别' }]"
        >
          <a-select v-model:value="formState.gender" placeholder="请选择性别">
            <a-select-option value="1">男</a-select-option>
            <a-select-option value="0">女</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item
          label="邮箱"
          name="email"
          :rules="[{ type: 'email', message: '请输入正确的邮箱地址' }]"
        >
          <a-input v-model:value="formState.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="状态" name="is_active">
          <a-switch v-model:checked="formState.is_active" />
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
  import MD5 from 'crypto-js/md5';

  import type {
    DataNode,
    DirectoryTreeProps,
    EventDataNode,
  } from 'ant-design-vue/lib/tree';

  interface DataSourceItem {
    id: string;
    username: string;
    name: string;
    password: string;
    gender: string;
    email: string;
    dept: string | null;
    role: string[];
    is_active: boolean;
  }

  const crud = createCrudOptions();

  const selectOptions = ref<{
    name: string | null;
    id: number | string | null;
  }>({
    name: null,
    id: null,
  });

  const formState = reactive({
    id: '',
    username: '',
    name: '',
    password: '',
    gender: '',
    email: '',
    dept: null,
    role: [],
    is_active: true,
  });
  const dataSource = ref<DataSourceItem[]>([]);
  const isModalVisible = ref(false);
  const deptOptions = ref([]);
  const defaultTreeProps: any = {
    value: 'id',
  };

  const predefinedColors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan'];

  // 获取颜色的方法
  const getTagColor = (name: string): string => {
    // 使用哈希方式生成颜色索引，确保同一名称的颜色一致
    const hash = Array.from(name).reduce(
      (acc, char) => acc + char.charCodeAt(0),
      0,
    );
    const index = hash % predefinedColors.length;
    return predefinedColors[index];
  };

  const columns = [
    { title: '序号', dataIndex: 'index', key: 'index', width: 100 },
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '姓名', dataIndex: 'name', key: 'name' },
    { title: '部门', dataIndex: 'dept_name', key: 'dept_name' },
    { title: '角色', dataIndex: 'role_info', key: 'role_info' },
    { title: '性别', dataIndex: 'gender', key: 'gender', width: 120 },
    { title: '邮箱', dataIndex: 'email', key: 'email' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 120 },
    { title: '操作', key: 'operation', width: 300 },
  ];

  // 显示添加模态框
  const showAddModal = () => {
    Object.assign(formState, {
      id: '',
      username: '',
      name: '',
      gender: '',
      email: '',
      dept: null,
      role: [],
      is_active: true,
    });
    isModalVisible.value = true;
  };

  // 提交表单
  const handleSubmit = async () => {
    //  formState.password = MD5(formState.password).toString();
    if (formState.id) {
      await crud.editData(formState);
      message.success('更新成功');
    } else {
      await crud.addData(formState);
      message.success('添加成功');
    }
    isModalVisible.value = false;
    fetchData();
  };

  // 编辑操作
  const editOper = (id: string) => {
    const item = dataSource.value.find((item) => item.id === id);
    console.log('object', formState);
    console.log('item', item);
    if (item) {
      Object.assign(formState, item);
      formState.gender = String(formState.gender);
      isModalVisible.value = true;
    }
  };

  // 删除操作
  const deleteOper = async (id: string) => {
    await crud.delData({ id });
    message.success('删除成功');
    fetchData();
  };

  const fetchData = async () => {
    const res = await api.GetList({ menu: selectOptions.value.id });
    dataSource.value = res.data;
    console.log('datasource', dataSource.value);
  };

  const toggleStatus = async (record: DataSourceItem) => {
    Object.assign(formState, record);
    // 切换状态
    formState.is_active = !formState.is_active;

    // 调用 editData 进行更新
    try {
      await crud.editData(formState);
      message.success('状态已更新');
    } catch (error) {
      message.error('状态更新失败，请重试');
      console.error(error);
    }
  };

  const handleRefreshTable = (record?: DataNode) => {
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

  onMounted(() => {
    crud.loadRoleOptions();
    crud.loadDeptOptions();
    fetchData();
  });
  defineExpose({ selectOptions, handleRefreshTable });
</script>
