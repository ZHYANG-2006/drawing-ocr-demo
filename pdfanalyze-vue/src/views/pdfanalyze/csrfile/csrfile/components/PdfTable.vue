<template>
  <div style="height: 80vh; margin: 10px">
    <a-table
      :columns="columns"
      :data-source="pdfFiles"
      :loading="props.loading"
      bordered
      :scroll="{ x: 2000, y: 700 }"
      :pagination="{
        current: current,
        pageSize: pageSize,
        total: total,
        showSizeChanger: true,
        showQuickJumper: true,
      }"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === 'id'">
          {{ (current - 1) * pageSize + index + 1 }}
        </template>
        <template v-if="column.key === 'operation'">
          <span>
            <a-button
              type="primary"
              size="small"
              :disabled="
                record.queue_order === '已完成' ||
                record.queue_order === '解析中'
              "
              @click="handleAnalyze(record)"
            >
              解析
            </a-button>
            <a-button
              type="primary"
              size="small"
              @click="handleCreateReview(record)"
            >
              新增Review
            </a-button>
            <a-popconfirm
              title="是否确认删除?"
              @confirm="deletePdf(record.id)"
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

<script setup lang="jsx">
  import { defineProps, ref, onMounted, onUnmounted, defineEmits } from 'vue';
  import {
    deleteItem,
    getList,
    getTask,
  } from '/@/views/pdfanalyze/csrfile/api/csrfile/pdfFile.js';
  import { message, Modal } from 'ant-design-vue';
  import { createReview } from '/@/views/pdfanalyze/csrfile/api/csrfilevreview/reviewversion.js';
  import useState from 'ant-design-vue/es/_util/hooks/useState.js';
  import _ from 'lodash-es';
  import moment from 'moment';
  // 响应式数据
  const pdfFiles = ref([]);
  const sorter_backend = ref();
  const props = defineProps({
    loading: Boolean  // 声明 loading 作为父组件传递的属性
  });
  const emit = defineEmits(['update:loading']); // 定义事件
  const current = ref(1); // 当前页码
  const pageSize = ref(10);
  const total = ref(0);
  let pollingInterval = null;
  const [filterValue, setFilterValue] = useState({
    process: '',
    customer: '',
    customer_file_name: '',
    customer_file_code: '',
    customer_file_version: '',
    queue_order: '',  // 解析队列
    start_analyze_time: '', // 解析开始时间
    finish_analyze_time: '', // 解析结束时间
    has_expired: '',  // 过期标识
    uploader_name: '', // 上传人
    create_datetime_after: '', // 上传时间
    create_datetime_before: '', // 上传时间
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
        return a.file_type.localeCompare(b.file_type);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">客户</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
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
      width: 100,
      sorter: (a, b) => {
        return a.customer.localeCompare(b.customer);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">客户文件名称</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
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
      width: 100,
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
            style="width: 60px; height: 20px;"
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
      width: 100,
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
            style="width: 60px; height: 20px;"
            value={filterValue.value.customer_file_version}  // 绑定值
            onInput={e => {
              filterValue.value.customer_file_version = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'customer_file_version',
      key: 'customer_file_version',
      filterDropdownVisible: true,
      width: 100,
      sorter: (a, b) => {
        return a.customer_file_version.localeCompare(b.customer_file_version);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">上传人</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
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
      width: 100,
      sorter: (a, b) => {
        return a.uploader_name.localeCompare(b.uploader_name);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">上传时间</span>
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
          <span style="display: block;">解析队列</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
            value={filterValue.value.queue_order}  // 绑定值
            onInput={e => {
              filterValue.value.queue_order = e.target.value;
              debouncedFetchPdfFiles();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'queue_order',
      key: 'queue_order',
      filterDropdownVisible: true,
      width: 100,
      sorter: (a, b) => {
        return a.queue_order.localeCompare(b.queue_order);
      },
    },
    { title: '操作', key: 'operation', width: 250, fixed: 'right' },
  ];

  // 获取 PDF 文件列表
  const fetchPdfFiles = async () => {
    emit('update:loading', true);
    // loading.value = true;
    try {
      const response = await getList({
        page: current.value,
        limit: pageSize.value,
        ...filterValue.value,
        ordering: sorter_backend.value,
      });
      total.value = response.data.length;
      if (response && Array.isArray(response.data)) {
        pdfFiles.value = response.data.map((file) => ({
          id: file.id,
          process: file.process,
          customer: file.customer,
          customer_file_name: file.customer_file_name,
          customer_file_code: file.customer_file_code,
          customer_file_version: file.customer_file_version,
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
          start_analyze_time: file.start_analyze_time,
          finish_analyze_time: file.finish_analyze_time,
          has_expired: file.has_expired,
          uploader_name: file.uploader_name,
          create_datetime: file.create_datetime,
        }));
        total.value = response.data.length || 0; // 更新总数
        const filesToAnalyze = response.data.filter(file => file.queue_order === -1);
        for (const file of filesToAnalyze) {
          await handleAnalyze(file);
        }
      } else {
        console.warn('Unexpected response format:', response);
        pdfFiles.value = [];
      }
    } catch (error) {
      console.error('获取文件数据失败:', error);
    } finally {
      emit('update:loading', false);
      // loading.value = false;
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
        message.success(response.msg);
      } else {
        message.error('文件解析失败');
      }

      // 刷新表格
      await fetchPdfFiles();
    } catch (error) {
      message.error('解析任务出错，请检查日志或稍后重试');
    }
  };

  // 处理表格分页和排序变化
  const handleTableChange = async (pagination, filters, sorter) => {
    const filterParams = {};
    if (!pagination) {
      return;
    }
    current.value = pagination.current; // 更新当前页码
    pageSize.value = pagination.pageSize; // 更新每页条数
    let sortOrder = null;

    if (sorter.field) {
      // 判断当前排序的字段和顺序
      sortOrder = sorter.order === 'ascend' ? sorter.field : sorter.order === 'descend' ? `-${sorter.field}` : null;
    }
    sorter_backend.value = sortOrder;
    fetchPdfFiles() // 获取对应页的数据
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
      await fetchPdfFiles(); // 刷新列表
    } catch (error) {
      console.error('删除失败:', error);
    }
  };

  const handleCreateReview = async (record) => {
    // 打开一个全屏遮罩的 modal
    const modal = Modal.info({
      title: '正在创建审核...',
      content: '请稍等，正在进行操作...',
      icon: null, // 不显示图标
      okButtonProps: { style: { display: 'none' } }, // 隐藏OK按钮
      closable: false, // 禁止关闭
      maskClosable: false, // 遮罩不可点击关闭
    });

    try {
      const response = await createReview(record.id); // 执行创建操作
      console.log('responserst', response);

      if (response.code === 2000) {
        // 关闭 Modal 并显示成功消息
        modal.destroy();
        message.success(response.msg);
      } else {
        // 关闭 Modal 并显示错误消息
        modal.destroy();
        message.error(response.msg);
      }
    } catch (error) {
      // 捕获异常时关闭 Modal，并显示错误信息
      modal.destroy();
      console.error('创建失败:', error);
      message.error('创建失败，请检查review status' + error);
    }
  };

  const deletePdfFile = async (id) => {
    // 显示加载提示
    const loadingMessage = message.loading('正在删除...', 0); // 0 表示该消息不自动消失，直到手动关闭

    try {
      const response = await deleteItem(id); // 执行删除操作
      console.log('response', response);

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

  // 启动轮询
  const startPolling = () => {
    pollingInterval = setInterval(async () => {
      try {
        const response = await getList({
          page: current.value,
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

  const debouncedFetchPdfFiles = _.debounce(() => {
    fetchPdfFiles();
  }, 500);

  // 在组件挂载时初始化
  onMounted(() => {
    fetchPdfFiles();
    startPolling();
  });

  onUnmounted(() => {
    stopPolling();
  });

  defineExpose({
    fetchPdfFiles,
  });
</script>
