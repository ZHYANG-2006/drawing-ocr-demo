<template>
  <div>
    <a-modal ref="modelRef" v-model:open="modelDialog" title="选择model">
      <div v-if="props.model">
        <a-tag>已选择: {{ props.model }}</a-tag>
      </div>
      <!-- 搜索输入框 -->
      <a-input
        v-model:value="searchQuery"
        placeholder="搜索模型..."
        style="margin-bottom: 10px"
      />
      <div class="model-card">
        <!-- 对请求回来的allModelData进行computed计算，返回搜索框匹配到的内容 -->
        <div
          v-for="(item, index) in filteredModelData"
          :key="index"
          @click="onModelChecked(item, index)"
        >
          <a-typography-text :type="modelCheckIndex === index ? 'primary' : ''">
            {{ item.app + '--' + item.title + '(' + item.key + ')' }}
          </a-typography-text>
        </div>
      </div>
      <template #footer>
        <a-button @click="modelDialog = false">取消</a-button>
        <a-button type="primary" @click="handleAutomatch">确定</a-button>
      </template>
    </a-modal>
    <div style="height: 80vh">
      <a-table :data-source="tableData" :columns="columns" />
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted, reactive, computed } from 'vue';
  import { message } from 'ant-design-vue';
  import { getModelList } from './api';
  import { MenuTreeItemType } from '/@/views/system/menu/types';
  import { successNotification, warningNotification } from '/@/utils/message';
  import { automatchColumnsData } from '/@/views/system/columns/components/ColumnsTableCom/api';
  import type {
    DataNode,
    DirectoryTreeProps,
    EventDataNode,
  } from 'ant-design-vue/lib/tree';

  const props = reactive({
    model: '',
    app: '',
    menu: '',
    role: '',
  });

  const selectOptions = ref<{
    name: string | null;
    id: number | string | null;
  }>({
    name: null,
    id: null,
  });
  // model 弹窗
  const modelDialog = ref(false);
  // 获取所有 model
  const allModelData = ref<any[]>([]);
  const modelCheckIndex = ref<null | number>(null);
  interface ModelRow {
    key: string;
    app: string;
    title: string;
  }

  const onModelChecked = (row: ModelRow, index: number) => {
    modelCheckIndex.value = index;
    props.model = row.key;
    props.app = row.app;
  };

  // 搜索处理
  const searchQuery = ref('');
  const filteredModelData = computed(() => {
    if (!searchQuery.value) {
      return allModelData.value;
    }
    const query = searchQuery.value.toLowerCase();
    return allModelData.value.filter(
      (item) =>
        item.app.toLowerCase().includes(query) ||
        item.title.toLowerCase().includes(query) ||
        item.key.toLowerCase().includes(query),
    );
  });

  // 表格数据
  const tableData = ref([]);
  const columns = ref([
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: '操作', key: 'action' },
  ]);

  /**
   * 自动匹配列
   */
  const handleAutomatch = async () => {
    if (selectOptions.value.id) {
      // 确保 selectOptions.value.id 是字符串
      props.menu = String(selectOptions.value.id);
      modelDialog.value = false;

      if (props.menu && props.model) {
        const res = await automatchColumnsData(props);
        if (res?.code === 2000) {
          successNotification('匹配成功');
        }
        // 模拟请求结果，更新表格数据
        tableData.value = res.data;
      } else {
        warningNotification('请选择角色和模型表！');
      }
    } else {
      warningNotification('菜单信息未选择！');
    }
  };

  const handleRefreshTable = (record?: DataNode) => {
    if (record && !record.is_catalog && record.id) {
      // 将 record 的 name 和 id 赋值给 selectOptions
      selectOptions.value = {
        name: record.name, // 确保 name 是 string 类型
        id: record.id, // 确保 id 是 string 类型
      };

      // 手动触发表格数据刷新，比如重新获取数据
      fetchTableData();
    } else {
      // 清空表格数据
      tableData.value = [];
    }
  };

  // 模拟获取表格数据的函数
  const fetchTableData = async () => {
    // 根据 selectOptions 中的条件查询数据
    const res = await getModelList();
    tableData.value = res.data;
  };

  /**
   * 页面加载时获取model数据
   */
  onMounted(async () => {
    const res = await getModelList();
    allModelData.value = res.data;
  });
  defineExpose({ selectOptions, handleRefreshTable });
</script>

<style scoped lang="scss">
  .model-card {
    margin-top: 10px;
    height: 30vh;
    overflow-y: scroll;

    div {
      margin: 15px 0;
      cursor: pointer;
    }
  }
</style>
