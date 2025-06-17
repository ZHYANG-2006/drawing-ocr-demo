<template>
  <div style="height: 80vh">
    <a-table
      :columns="columns"
      :data-source="pdfFiles"
      :loading="loading"
      :scroll="{ x: 4000 }"
      :pagination="{
        current: currentPage,
        pageSize: pageSize,
        total: total,
        showSizeChanger: true,
        showQuickJumper: true,
      }"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === 'id'">
          {{ index + 1 }}
        </template>
        <template v-if="column.key === 'operation'">
          <span>
            <a-button
              type="primary"
              size="small"
              @click="handleAnalyze(record)"
            >
              解析
            </a-button>
            <a-button
              type="primary"
              size="small"
              @click="handleAnalyze(record)"
            >
              新增Review
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
  </div>
</template>

<script setup>
  import { ref, onMounted, onUnmounted } from 'vue';
  import { getList, getTask } from '/@/views/pdfanalyze/cppqcp/api/cppqcpfile/pdfFile.js';
  import { message } from 'ant-design-vue';

  // 响应式数据
  const pdfFiles = ref([]);
  const loading = ref(false);
  const currentPage = ref(1); // 当前页码
  const pageSize = ref(10);
  const total = ref(0);
  let pollingInterval = null;

  // 表格列定义
  const columns = [
    { title: '序号', dataIndex: 'id', key: 'id', width: 100, fixed: 'left' },
    { title: '制程', dataIndex: 'process', key: 'process' },
    { title: '文件类型', dataIndex: 'file_type', key: 'file_type' },
    { title: '客户', dataIndex: 'customer', key: 'customer' },
    { title: '是否通用', dataIndex: 'is_universal', key: 'is_universal' },
    { title: '料号', dataIndex: 'material_number', key: 'material_number' },
    { title: 'LOB', dataIndex: 'lob', key: 'lob' },
    { title: 'PFMEA类别', dataIndex: 'pfmea_type', key: 'pfmea_type' },
    { title: 'SITE', dataIndex: 'branch', key: 'branch' },
    { title: '文件名', dataIndex: 'name', key: 'name' },
    { title: '解析队列', dataIndex: 'queue_order', key: 'queue_order' },
    { title: '解析版本', dataIndex: 'analyze_version', key: 'analyze_version' },
    {
      title: '解析开始时间',
      dataIndex: 'start_analyze_time',
      key: 'start_analyze_time',
    },
    {
      title: '解析结束时间',
      dataIndex: 'finish_analyze_time',
      key: 'finish_analyze_time',
    },
    {
      title: '过期标识',
      dataIndex: 'has_expired',
      key: 'has_expired',
    },
    { title: '上传人', dataIndex: 'creator_name', key: 'creator_name' },
    { title: '上传时间', dataIndex: 'create_datetime', key: 'create_datetime' },
    { title: '操作', key: 'operation', width: 250, fixed: 'right' },
  ];

  // 获取 PDF 文件列表
  const fetchPdfFiles = async (params) => {
    loading.value = true;
    try {
      const response = await getList({
        page: params.page || currentPage.value,
        limit: params.pageSize || pageSize.value,
      });
      if (response && Array.isArray(response.data)) {
        pdfFiles.value = response.data.map((file) => ({
          id: file.id,
          name: file.name,
          branch: file.branch,
          phase: file.phase,
          process: file.process,
          file_type: file.file_type,
          is_universal: file.is_universal === 'Y' ? '是' : '否', // 转换为友好的显示
          customer: file.customer,
          material_number: file.material_number,
          lob: file.lob,
          pfmea_type: file.pfmea_type,
          queue_order:
            file.queue_order === 0
              ? '已完成'
              : file.queue_order === -1
                ? '未解析'
                : file.queue_order === -2
                  ? '解析失败'
                  : file.queue_order === 1
                    ? '解析中'
                    : `当前解析队列等待中`,
          analyze_version: file.analyze_version,
          start_analyze_time: file.start_analyze_time,
          finish_analyze_time: file.finish_analyze_time,
          has_expired: file.has_expired,
          creator_name: file.creator_name,
          create_datetime: file.create_datetime,
        }));
        console.log('response#', response);
        total.value = response.data.length || 0; // 更新总数
      } else {
        console.warn('Unexpected response format:', response);
        pdfFiles.value = [];
      }
    } catch (error) {
      console.error('获取文件数据失败:', error);
    } finally {
      loading.value = false;
    }
  };

  const handleAnalyze = async (record) => {
    try {
      console.log('record', record);
      // 检查 record 是否存在有效的 ID
      if (!record || !record.id) {
        throw new Error('文件 ID 不存在');
      }

      // 调用调度接口
      const response = await getTask(record.id);
      if (response.code === 2000) {
        console.log('success', response);
        message.success(response.msg);
      } else {
        message.error('文件解析失败');
      }

      // 刷新表格
      fetchPdfFiles({});
    } catch (error) {
      console.error('解析任务出错:', error);
      message.error('解析任务出错，请检查日志或稍后重试');
    }
  };

  // 处理表格分页和排序变化
  const handleTableChange = (pagination) => {
    const { current, limit } = pagination;
    if (!current || !pageSize) {
      return;
    }
    currentPage.value = current; // 更新当前页码
    pageSize.value = limit; // 更新每页条数
    fetchPdfFiles({ page: current, limit: pageSize }) // 获取对应页的数据
      .then(() => {
        console.log('Data fetch completed successfully.');
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  };

  // 删除 PDF 文件
  const deletePdf = async (id) => {
    try {
      await deletePdfFile(id);
      fetchPdfFiles({}); // 刷新列表
    } catch (error) {
      console.error('删除失败:', error);
    }
  };

  // 启动轮询
  const startPolling = () => {
    pollingInterval = setInterval(async () => {
      try {
        const response = await getList({
          page: currentPage.value,
          limit: pageSize.value,
        });
        if (response && Array.isArray(response.data)) {
          response.data.forEach((file) => {
            const existingFile = pdfFiles.value.find(
              (item) => item.id === file.id,
            );
            if (existingFile) {
              // 仅更新变化的数据
              existingFile.queue_order =
                file.queue_order === 0
                  ? '已完成'
                  : file.queue_order === -1
                    ? '未解析'
                    : file.queue_order === -2
                      ? '解析失败'
                      : file.queue_order === 1
                        ? '解析中'
                        : `当前解析队列等待中`;
              existingFile.progress = file.progress || '0%';
            }
          });
        }
      } catch (error) {
        console.error('轮询数据失败:', error);
      }
    }, 5000); // 每5秒轮询一次s
  };

  // 停止轮询
  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  };

  // 在组件挂载时初始化
  onMounted(() => {
    fetchPdfFiles({});
    startPolling();
  });

  onUnmounted(() => {
    stopPolling();
  });

  defineExpose({
    fetchPdfFiles,
  });
</script>

