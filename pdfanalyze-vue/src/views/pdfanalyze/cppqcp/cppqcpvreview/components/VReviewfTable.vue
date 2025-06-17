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
  } from '/@/views/pdfanalyze/cppqcp/api/cppqcpvreview/reviewversion.js';
  import { useFileStore } from '/@/views/pdfanalyze/cppqcp/stores/fileStore.js'; // 根据实际路径调整
  import { message } from 'ant-design-vue';
  import { useRouter } from 'vue-router';
  import _ from 'lodash-es';
  import moment from 'moment';
  import useState from 'ant-design-vue/es/_util/hooks/useState.js';
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
    file_type: '',
    pfmea_type: '',
    is_universal: '',
    customer: '',
    material_number: '',
    lob: '',
    file_name: '',
    uploader_name: '',
    create_datetime_after: null,
    create_datetime_before: null,
    status: '',
    has_pfmea: '',
    pfmea_time_after: null,
    pfmea_time_before: null,
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

    // 文件类型字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">文件类型</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.file_type}  // 绑定值
            onInput={e => {
              filterValue.value.file_type = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'file_type',
      key: 'file_type',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.file_type.localeCompare(b.file_type);  // 按文件类型字段排序
      },
    },

    // PFMEA类别字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">PFMEA类别</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.pfmea_type}  // 绑定值
            onInput={e => {
              filterValue.value.pfmea_type = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'pfmea_type',
      key: 'pfmea_type',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.pfmea_type.localeCompare(b.pfmea_type);  // 按PFMEA类别排序
      },
    },

    // 是否通用字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">是否通用</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.is_universal}  // 绑定值
            onInput={e => {
              filterValue.value.is_universal = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'is_universal',
      key: 'is_universal',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.is_universal.localeCompare(b.is_universal);  // 按PFMEA类别排序
      },
    },

    // 客户字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">客户</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.customer}  // 绑定值
            onInput={e => {
              filterValue.value.customer = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'customer',
      key: 'customer',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.customer.localeCompare(b.customer);  // 按PFMEA类别排序
      },
    },

    // 料号字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">料号</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.material_number}  // 绑定值
            onInput={e => {
              filterValue.value.material_number = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'material_number',
      key: 'material_number',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.material_number.localeCompare(b.material_number);  // 按PFMEA类别排序
      },
    },

    // LOB字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">LOB</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
            value={filterValue.value.lob}  // 绑定值
            onInput={e => {
              filterValue.value.lob = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'lob',
      key: 'lob',
      filterDropdownVisible: true,
      width: 100,
      sorter: (a, b) => {
        return a.lob.localeCompare(b.lob);  // 按PFMEA类别排序
      },
    },

    // 文件名字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">文件名</span>
          <a-input
            placeholder=""
            style="width: 160px; height: 20px;"
            value={filterValue.value.file_name}  // 绑定值
            onInput={e => {
              filterValue.value.file_name = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'file_name',
      key: 'file_name',
      filterDropdownVisible: true,
      width: 200,
      sorter: (a, b) => {
        return a.file_name.localeCompare(b.file_name);  // 按PFMEA类别排序
      },
    },

    // 维护人字段
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">创建人</span>
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
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">是否发送PFMEA系统</span>
          <a-input
            placeholder=""
            style="width: 80px; height: 20px;"
            value={filterValue.value.has_pfmea}  // 绑定值
            onInput={e => {
              filterValue.value.has_pfmea = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'has_pfmea',
      key: 'has_pfmea',
      filterDropdownVisible: true,
      width: 120,
      sorter: (a, b) => {
        return a.has_pfmea.localeCompare(b.has_pfmea);  // 按PFMEA类别排序
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">发送PFMEA时间</span>
          <a-range-picker
            style="width: 340px; height: 20px;"
            value={filterValue.value.pfmea_time_after && filterValue.value.pfmea_time_before ? [
              moment(filterValue.value.pfmea_time_after),
              moment(filterValue.value.pfmea_time_before)
            ] : null}
            showTime
            format="YYYY-MM-DD HH:mm:ss"
            onChange={dates => {
              // 选择的时间范围
              if (dates) {
                filterValue.value.pfmea_time_after = dates[0].format('YYYY-MM-DD HH:mm:ss');
                filterValue.value.pfmea_time_before = dates[1].format('YYYY-MM-DD HH:mm:ss');
              } else {
                filterValue.value.pfmea_time_after = null;
                filterValue.value.pfmea_time_before = null;
              }
              debouncedFetchPdfFiles();  // 更新数据
            }}
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'pfmea_time',
      key: 'pfmea_time',
      filterDropdownVisible: true,
      width: 380,
      align: 'center',
      sorter: (a, b) => {
        // 使用 moment 进行日期比较
        return moment(a.pfmea_time).isBefore(moment(b.pfmea_time)) ? -1 : 1;
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
          file_type: vreview.file_type,
          pfmea_type: vreview.pfmea_type,
          is_universal: vreview.is_universal === 'Y' ? '是' : '否', // 转换为友好的显示
          customer: vreview.customer,
          material_number: vreview.material_number,
          lob: vreview.lob,
          file_name: vreview.file_name,
          uploader_name: vreview.uploader_name,
          create_datetime: vreview.create_datetime,
          status: vreview.status,
          has_pfmea: vreview.has_pfmea,
          pfmea_time: vreview.pfmea_time,
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

  const handleStartReview = (record) => {
    console.log('routtest', router);
    if (!record || !record.id) {
      message.error('记录 ID 不存在');
      return;
    }
    console.log('idprocess', record);
    fileStore.setFileId(record.id);
    fileStore.setProcess(record.process);
    fileStore.setPFMEA(record.PFMEA);
    // 跳转到目标页面，并传递 ID
    router.push({
      name: 'cppqcpviewr', // 路由名称
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
    /*
      if (filters.file_type) {
        filterParams.file_type = filters.file_type[0];
      }
      if (filters.is_universal) {
        filterParams.is_universal = filters.is_universal[0];
      }
  */
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

  const getIsOnGoing = (record) => {
    return computed({
      get() {
        return record.status === 'OnGoing';
      },
      set(value) {
        record.status = value ? 'OnGoing' : 'Closed';
      }
    });
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
