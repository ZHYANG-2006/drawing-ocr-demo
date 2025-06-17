<template>
  <div style="height: 80vh; margin: 10px">
    <a-table
      :columns="columns"
      :data-source="reviewVersions"
      :loading="loading"
      :scroll="{ x: 2000, y: 700 }"
      :pagination="{
        current: current,
        pageSize: pageSize,
        total: total,
        showSizeChanger: true,
        showQuickJumper: true,
      }"
      bordered
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === 'id'">
          {{ (current - 1) * pageSize + index + 1 }}
        </template>
        <template v-if="column.key === 'status'">
          <a-switch
            v-if="record.status === 'OnGoing' || record.status === 'Closed'"
            :checked="record.status==='OnGoing'"
            @change="toggleStatus(record)"
            :disabled="record.status === 'Closed' || record.status === 'Cancel'"
          />
          <span v-else>{{ record.status }}</span>  <!-- 对于其他状态，直接显示 -->
        </template>
        <template v-if="column.key === 'operation'">
          <span>
            <a-button
              type="primary"
              size="small"
              :disabled="record.status === 'Closed' || record.status === 'Cancel'"
              @click="handleStartReview(record)"
            >
              编辑
            </a-button>
            <a-button
              type="primary"
              size="small"
              @click="handleStartReview(record)"
            >
              查看
            </a-button>
            <a-button
              type="primary"
              size="small"
              @click="handleExportExcel(record)"
            >
              导出Excel
            </a-button>
            <a-popconfirm
              title="是否确认删除?"
              @confirm="deleteOper(record.id)"
            >
              <a-button type="primary" size="small" :disabled="record.status === 'Closed' || record.status === 'Cancel'" class="ml-2" danger>
                删除
              </a-button>
            </a-popconfirm>
          </span>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="jsx">
  import { ref, onMounted, onUnmounted, computed } from 'vue';
  import {
    closeStatus,
    deleteItem,
    getList,
    exportExcel,
  } from '/@/views/pdfanalyze/csrfile/api/csrfilevreview/reviewversion.js';
  import { useFileStore } from '/@/views/pdfanalyze/csrfile/stores/fileStore.js'; // 根据实际路径调整
  import { useRouter } from 'vue-router';
  import _ from 'lodash-es';
  import * as XLSX from "xlsx";
  import moment from 'moment';
  import useState from 'ant-design-vue/es/_util/hooks/useState.js';
  import { message } from 'ant-design-vue';
  // 响应式数据
  const reviewVersions = ref([]);
  const loading = ref(false);
  const current = ref(1); // 当前页码
  const pageSize = ref(10);
  const total = ref(0);
  let pollingInterval = null;
  const router = useRouter();
  const fileStore = useFileStore();
  const sorter_backend = ref();
  const [filterValue, setFilterValue] = useState({
    process: '',
    customer_file_name: '',
    customer_file_code: '',
    customer_file_version: '',
    uploader_name: '',
    create_datetime_after: null,
    create_datetime_before: null,
    status: '',
  });

  // 表格列定义
  const columns = [
    { title: '', dataIndex: 'id', key: 'id', width: 50, fixed: 'left' },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">制程</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
            value={filterValue.value.process}  // 绑定值
            onInput={e => {
              filterValue.value.process = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'process',
      key: 'process',
      filterDropdownVisible: true,
      width: 100,
      sorter: (a, b) => {
        return a.process.localeCompare(b.process);  // 按制程字段排序
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">客户文件名称</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.customer_file_name}  // 绑定值
            onInput={e => {
              filterValue.value.customer_file_name = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'customer_file_name',
      key: 'customer_file_name',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.customer_file_name.localeCompare(b.customer_file_name);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">客户文件编号</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.customer_file_code}  // 绑定值
            onInput={e => {
              filterValue.value.customer_file_code = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'customer_file_code',
      key: 'customer_file_code',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.customer_file_code.localeCompare(b.customer_file_code);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">客户文件版本</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.customer_file_version}
            onInput={e => {
              filterValue.value.customer_file_version = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      ),
      dataIndex: 'customer_file_version',
      key: 'customer_file_version',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.customer_file_version.localeCompare(b.customer_file_version);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">确认人</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.uploader_name}  // 绑定值
            onInput={e => {
              filterValue.value.uploader_name = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'uploader_name',
      key: 'uploader_name',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.uploader_name.localeCompare(b.uploader_name);  // 按PFMEA类别排序
      },
    },

    // 维护时间字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">创建时间</span>
          <a-range-picker
            style="width: 340px; height: 20px;"
            value={filterValue.value.create_datetime_after && filterValue.value.create_datetime_before ? [
              moment(filterValue.value.create_datetime_after),
              moment(filterValue.value.create_datetime_before)
            ] : null}
            showTime
            format="YYYY-MM-DD HH:mm:ss"
            onChange={dates => {
              // 选择的时间范围
              if (dates) {
                filterValue.value.create_datetime_after = dates[0].format('YYYY-MM-DD HH:mm:ss');
                filterValue.value.create_datetime_before = dates[1].format('YYYY-MM-DD HH:mm:ss');
              } else {
                filterValue.value.create_datetime_after = null;
                filterValue.value.create_datetime_before = null;
              }
              debouncedFetchPdfFiles();  // 更新数据
            }}
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'create_datetime',
      key: 'create_datetime',
      filterDropdownVisible: true,
      width: 380,
      align: 'center',
      sorter: (a, b) => {
        // 使用 moment 进行日期比较
        return moment(a.create_datetime).isBefore(moment(b.create_datetime)) ? -1 : 1;
      },
      defaultSortOrder: 'descend',
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">状态</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.status}  // 绑定值
            onInput={e => {
              filterValue.value.status = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'status',
      key: 'status',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.status.localeCompare(b.status);  // 按PFMEA类别排序
      },
    },
    {
      title: '操作',
      key: 'operation',
      width: 250,
      fixed: 'right',
    },
  ];

  // 获取 PDF 文件列表
  const fetchReviewVersions = async () => {
    loading.value = true;
    try {
      const response = await getList({
        page: current.value,
        limit: pageSize.value,
        ...filterValue.value,
        ordering: sorter_backend.value,
      });
      total.value = response.data.length;
      if (response && Array.isArray(response.data)) {
        reviewVersions.value = response.data.map((vreview) => ({
          id: vreview.id,
          process: vreview.process,
          customer_file_name: vreview.customer_file_name,
          customer_file_code: vreview.customer_file_code,
          customer_file_version: vreview.customer_file_version,
          uploader_name: vreview.uploader_name,
          create_datetime: vreview.create_datetime,
          status: vreview.status,
        }));
        total.value = response.data.length || 0; // 更新总数
      } else {
        console.warn('Unexpected response format:', response);
        reviewVersions.value = [];
      }
    } catch (error) {
      console.error('获取文件数据失败:', error);
    } finally {
      loading.value = false;
    }
  };

  const handleExportExcel = async (record) => {
    if (!record || !record.id) {
      message.error('记录 ID 不存在');
      return;
    }
    try {
      // 假设 exportExcel 返回的是一个 JSON 对象，而不是直接的二进制文件
      const response = await exportExcel({ id: record.id });
      if (response.code !== 2000) {
        message.error(`导出失败：${response.msg}`);
        return;
      }

      const data = response.data; // 这就是你要转成表格的数组
      const ws = XLSX.utils.json_to_sheet(data.map(item => ({
        "制程": item.process,
        "客户": item.customer,
        "客户文件名称": item.customer_file_name,
        "客户文件编号": item.customer_file_code,
        "客户文件版本": item.customer_file_version,
        "确认人": item.uploader_name,
        "Meet requirement": item.meet_req,
        "是否执行": item.is_execute,
        "MFLEX内部文件+编号": item.mflex_file,
        "Remark": item.remark,
      })));
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Results");
      const wbout = XLSX.write(wb, { bookType: "xlsx", type: "array" });
      const blob = new Blob([wbout], { type: "application/octet-stream" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "search_results.xlsx";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      message.error('导出时发生异常');
    }
  };

  const handleStartReview = (record) => {
    if (!record || !record.id) {
      message.error('记录 ID 不存在');
      return;
    }
    fileStore.setFileId(record.id);
    fileStore.setProcess(record.process);
    // 跳转到目标页面，并传递 ID
    router.push({
      name: 'csrfileviewr', // 路由名称
    });
  };

  // 处理表格分页和排序变化
  const handleTableChange = async (pagination, filters, sorter) => {
    const filterParams = {};
    if (!pagination) {
      return;
    }
    current.value = pagination.current;
    pageSize.value = pagination.pageSize;
    // 获取筛选条件
    if (filters.process) {
      filterParams.process = filters.process[0]; // 假设选择了单个值
    }
    fetchReviewVersions() // 获取对应页的数据
      .then(() => {
        console.log('Data fetch completed successfully.');
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  };

  // 启动轮询
  const startPolling = () => {
    pollingInterval = setInterval(async () => {}, 5000); // 每5秒轮询一次s
  };

  // 停止轮询
  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  };

  // toggleStatus 方法处理状态切换
  const toggleStatus = async (record) => {
    try {
      if (record.status === 'OnGoing') {
        record.status = 'Closed'; // 切换到 'Closed'
        const response = await closeStatus(record.id);
        message.success(response.msg);
        await fetchReviewVersions();
      }
    }
    catch (error) {
      await fetchReviewVersions();
    }
  };

  const deleteOper = async (id) => {
    // 显示加载提示
    const loadingMessage = message.loading('正在删除...', 0); // 0 表示该消息不自动消失，直到手动关闭

    try {
      const response = await deleteItem(id); // 执行删除操作
      console.log('response', response);

      // 请求删除后重新获取数据
      await fetchReviewVersions();

      // 删除完成后，关闭加载提示，并显示成功信息
      loadingMessage(); // 手动关闭加载提示
      message.success('删除成功');
    } catch (error) {
      // 删除失败时，关闭加载提示，并显示错误信息
      loadingMessage(); // 手动关闭加载提示
      message.error('删除失败');
      console.error('删除失败', error);
    }
  };

  const debouncedFetchPdfFiles = _.debounce(() => {
    fetchReviewVersions();
  }, 500);

  // 在组件挂载时初始化
  onMounted(() => {
    fetchReviewVersions({});
    startPolling();
  });

  onUnmounted(() => {
    stopPolling();
  });

  defineExpose({
    fetchReviewVersions,
  });
</script>
