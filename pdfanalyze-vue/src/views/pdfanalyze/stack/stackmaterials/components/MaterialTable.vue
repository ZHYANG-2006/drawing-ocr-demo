<template>
  <div style="height: 80vh; margin: 10px">
    <a-table
      :columns="columns"
      :data-source="materials"
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
<!--            <a-button-->
<!--              type="primary"-->
<!--              size="small"-->
<!--              :disabled="-->
<!--                record.queue_order === '' ||-->
<!--                record.queue_order === '解析中'-->
<!--              "-->
<!--              @click="handleStartReview(record)"-->
<!--            >-->
<!--              查看-->
<!--            </a-button>-->
            <a-popconfirm
              title="是否确认删除?"
              @confirm="deleteMaterial(record.id)"
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
  } from '/@/views/pdfanalyze/stack/api/stackmaterials/material.js';
  import { message, Modal } from 'ant-design-vue';
  import useState from 'ant-design-vue/es/_util/hooks/useState.js';
  import { useRouter } from 'vue-router';
  import _ from 'lodash-es';
  import moment from 'moment';
  import { useFileStore } from '/@/views/pdfanalyze/stack/stores/fileStore.js';
  const props = defineProps({
    loading: Boolean  // 声明 loading 作为父组件传递的属性
  });
  const emit = defineEmits(['update:loading']); // 定义事件
  // 响应式数据
  const materials = ref([]);
  const sorter_backend = ref();
  const current = ref(1); // 当前页码
  const pageSize = ref(10);
  const total = ref(0);
  const router = useRouter();
  let pollingInterval = null;
  const fileStore = useFileStore();
  const [filterValue, setFilterValue] = useState({
    number: '',
    name: '',
    create_datetime_after: '', // 上传时间
    create_datetime_before: '', // 上传时间
  });

  // 表格列定义
  const columns = [
    { title: '', dataIndex: 'id', key: 'id', width: 50, fixed: 'left' },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">材料号</span>
          <a-input
            placeholder=""
            style="width: 120px; height: 20px;"
            value={filterValue.value.number}  // 绑定值
            onInput={e => {
              filterValue.value.number = e.target.value;
              debouncedFetchMaterials();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'number',
      key: 'number',
      filterDropdownVisible: true,
      width: 160,
      sorter: (a, b) => {
        return a.number.localeCompare(b.number);
      },
    },
    {
      title: () => (
        <div style="text-align: center;">
          <span style="display: block;">材料</span>
          <a-input
            placeholder=""
            style="width: 120px; height: 20px;"
            value={filterValue.value.name}  // 绑定值
            onInput={e => {
              filterValue.value.name = e.target.name;
              debouncedFetchMaterials();
            }} // 更新 filterValue
            onClick={(e) => e.stopPropagation()}  // 防止点击时触发排序
          />
        </div>
      ),
      dataIndex: 'name',
      key: 'name',
      filterDropdownVisible: true,
      width: 160,
      sorter: (a, b) => {
        return a.name.localeCompare(b.name);
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
    { title: '操作', key: 'operation', width: 250, fixed: 'right' },
  ];

  const fetchMaterials = async () => {
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
      console.log('responsedatadara',response.data);
      if (response && Array.isArray(response.data)) {
        materials.value = response.data.map((material) => ({
          id: material.id,
          number: material.number,
          name: material.name,
          uploader_name: material.uploader_name,
          create_datetime: material.create_datetime,
        }));
        total.value = response.data.length || 0; // 更新总数
      } else {
        console.warn('Unexpected response format:', response);
        materials.value = [];
      }
    } catch (error) {
      console.error('获取文件数据失败:', error);
    } finally {
      emit('update:loading', false);
      // loading.value = false;
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
    fetchMaterials() // 获取对应页的数据
      .then(() => {
        console.log('Data fetch completed successfully.');
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  };

  // 删除 PDF 文件
  const deleteMaterial = async (id) => {
    try {
      await deleteM(id);
      await fetchMaterials(); // 刷新列表
    } catch (error) {
      console.error('删除失败:', error);
    }
  };

  const deleteM = async (id) => {
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

  const debouncedFetchMaterials = _.debounce(() => {
    fetchMaterials();
  }, 500);

  // 在组件挂载时初始化
  onMounted(() => {
    fetchMaterials();
  });

  defineExpose({
    fetchMaterials,
  });
</script>
