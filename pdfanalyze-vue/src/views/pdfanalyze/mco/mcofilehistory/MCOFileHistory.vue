<template>
  <a-card>
    <div class="toolbar">
      <a-input-search
        v-model:value="search"
        placeholder="搜索文件名/图号/版本"
        @search="onSearch"
        style="width: 300px; margin-right: 8px;"
      />
      <a-button type="primary" @click="onSync" :loading="syncing">
        同步文件
      </a-button>
    </div>
    <a-table
      :columns="columns"
      :data-source="data"
      :pagination="pagination"
      :loading="loading"
      @change="handleTableChange"
      rowKey="id"
    >
      <template #create_datetime="{ text }">
        {{ new Date(text).toLocaleString() }}
      </template>
    </a-table>
  </a-card>
</template>

<script setup>
  import { ref, reactive, onMounted } from 'vue';
  import { message } from 'ant-design-vue';
  import { getFileHistory, syncFileHistory } from "/@/views/pdfanalyze/mco/api/mcofilehistory/mcoFileHistory.js";

  const data = ref([]);
  const loading = ref(false);
  const syncing = ref(false);
  const search = ref('');
  const pagination = reactive({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  const columns = [
    { title: '文件名', dataIndex: 'file_name' },
    { title: '图号', dataIndex: 'drawing_number' },
    { title: '版本', dataIndex: 'rev' },
    {
      title: '创建时间',
      dataIndex: 'create_datetime',
      slots: { customRender: 'create_datetime' },
    },
  ];

  async function fetchList() {
    loading.value = true;
    try {
      const res = await getFileHistory({
        search: search.value || undefined,
        page: pagination.current,
        page_size: pagination.pageSize,
      });
      data.value = res.data.data;
      pagination.total = res.data.pagination.total;
    } catch {
      message.error('获取列表失败');
    } finally {
      loading.value = false;
    }
  }

  function onSearch() {
    pagination.current = 1;
    fetchList();
  }

  function handleTableChange(p) {
    pagination.current = p.current || 1;
    pagination.pageSize = p.pageSize || 10;
    fetchList();
  }

  async function onSync() {
    syncing.value = true;
    try {
      const res = await syncFileHistory();
      message.success(res.data.msg || '同步成功');
      fetchList();
    } catch {
      message.error('同步失败');
    } finally {
      syncing.value = false;
    }
  }

  onMounted(fetchList);
</script>

<style scoped>
  .toolbar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 16px;
  }
</style>
