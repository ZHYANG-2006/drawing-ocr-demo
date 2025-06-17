<template>
  <div style="height: 80vh; margin: 10px">
    <a-table
      :columns="columns"
      :data-source="iqaDirs"
      :loading="loading"
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
              @click="handleExport(record)"
            >
              导出Excel
            </a-button>
            <a-popconfirm
              title="是否确认删除?"
              @confirm="deleteIqaDir(record.id)"
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
  import { ref, onMounted, onUnmounted } from 'vue';
  import {
    deleteItem,
    getList,
    exportExcel,
  } from '/src/views/pdfanalyze/iqa/api/iqadir/iqaDir.js';
  import { message, Modal } from 'ant-design-vue';
  import useState from 'ant-design-vue/es/_util/hooks/useState.js';
  import _ from 'lodash-es';
  import moment from 'moment';
  // 响应式数据
  const iqaDirs = ref([]);
  const sorter_backend = ref();
  const loading = ref(false);
  const current = ref(1); // 当前页码
  const pageSize = ref(10);
  const total = ref(0);
  let pollingInterval = null;
  const [filterValue, setFilterValue] = useState({
    dir_type: '',      // 目录类型
    folder_name: '',    // 文件夹名
    path: '',     // 路径
    create_datetime_after: '', // 上传时间
    create_datetime_before: '', // 上传时间
    uploader_name: '', // 上传人
  });

  // 表格列定义
  const columns = [
    { title: '', dataIndex: 'id', key: 'id', width: 50, fixed: 'left' },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">类型</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
            value={filterValue.value.dir_type}  // 绑定值
            onInput={e => {
              filterValue.value.dir_type = e.target.value;
              debouncedFetchIqaDirs();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'dir_type',
      key: 'dir_type',
      filterDropdownVisible: true,
      width: 100,
      sorter: (a, b) => {
        return a.dir_type.localeCompare(b.dir_type);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">文件夹名</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
            value={filterValue.folder_name}  // 绑定值
            onInput={e => {
              filterValue.value.folder_name = e.target.value;
              debouncedFetchIqaDirs();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'folder_name',
      key: 'folder_name',
      filterDropdownVisible: true,
      width: 100,
      sorter: (a, b) => {
        return a.folder_name.localeCompare(b.folder_name);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">存储路径</span>
          <a-input
            placeholder=""
            style="width: 60px; height: 20px;"
            value={filterValue.value.path}  // 绑定值
            onInput={e => {
              filterValue.value.path = e.target.value;
              debouncedFetchIqaDirs();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'path',
      key: 'path',
      filterDropdownVisible: true,
      width: 100,
      sorter: (a, b) => {
        return a.path.localeCompare(b.path);
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
              debouncedFetchIqaDirs();
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
              debouncedFetchIqaDirs();  // 更新数据
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
    { title: '操作', key: 'operation', width: 250, fixed: 'right' },
  ];

  // 获取 Iqa目录列表
  const fetchIqaDirs = async () => {
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
        iqaDirs.value = response.data.map((dir) => ({
          id: dir.id,
          dir_type: dir.dir_type,
          folder_name: dir.folder_name,
          path: dir.path,
          uploader_name: dir.uploader_name,
          create_datetime: dir.create_datetime,
        }));
        total.value = response.data.length || 0; // 更新总数
      } else {
        console.warn('Unexpected response format:', response);
        iqaDirs.value = [];
      }
    } catch (error) {
      console.error('获取文件数据失败:', error);
    } finally {
      loading.value = false;
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
    fetchIqaDirs() // 获取对应页的数据
      .then(() => {
        console.log('Data fetch completed successfully.');
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  };

  // 删除 PDF 文件
  const deleteIqaDir = async (id) => {
    // 显示加载提示
    const loadingMessage = message.loading('正在删除...', 0); // 0 表示该消息不自动消失，直到手动关闭

    try {
      const response = await deleteItem(id); // 执行删除操作
      console.log('response', response);

      // 删除完成后，关闭加载提示，并显示成功信息
      loadingMessage(); // 手动关闭加载提示
      message.success('删除成功');
      await fetchIqaDirs();
    } catch (error) {
      // 删除失败时，关闭加载提示，并显示错误信息
      loadingMessage(); // 手动关闭加载提示
      message.error('删除失败');
      console.error('删除失败', error);
    }
  };

  const handleExport = async (record) => {
    const loadingMessage = message.loading('正在导出...', 0); // 0 表示该消息不自动消失，直到手动关闭
    try {
      // 1. 发请求获取 Excel 文件 (blob)
      const response = await exportExcel(record.id);
      // 2. response.data 就是一个 Blob 类型
      const blob = response.data;

      // 3. 创建一个下载链接
      const fileName = `导出数据-${record.id}.xlsx`;  // 你也可从后端的响应头或 record 中获取动态文件名
      const url = window.URL.createObjectURL(blob);

      // 4. 动态创建 <a> 标签触发下载
      const link = document.createElement('a');
      link.style.display = 'none';
      link.href = url;
      link.download = fileName; // 指定下载的文件名
      document.body.appendChild(link);
      link.click();

      // 5. 释放资源
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      loadingMessage(); // 手动关闭加载提示
      message.success('导出成功');
      await fetchIqaDirs(); // 如果需要刷新数据，可以保留，否则去掉

    } catch (error) {
      loadingMessage(); // 手动关闭加载提示
      message.error('导出失败');
      console.error('导出失败', error);
    }
  };


  const debouncedFetchIqaDirs = _.debounce(() => {
    fetchIqaDirs();
  }, 500);

  // 在组件挂载时初始化
  onMounted(() => {
    fetchIqaDirs();
  });

  defineExpose({
    fetchIqaDirs,
  });
</script>
