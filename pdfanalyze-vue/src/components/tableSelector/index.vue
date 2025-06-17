<template>
  <a-select
    :value="data"
    dropdown-class-name="popperClass"
    class="tableSelector"
    :mode="props.tableConfig.isMultiple ? 'multiple' : ''"
    placeholder="请选择"
    @deselect="removeTag"
    @dropdownVisibleChange="visibleChange"
  >
    <template #dropdownRender>
      <div class="option">
        <a-input-search
          :value="search"
          placeholder="请输入关键词"
          allow-clear
          style="margin-bottom: 10px"
          @change="getDict"
          @clear="getDict"
        />
        <a-table
          ref="tableRef"
          :data-source="tableData"
          size="small"
          row-key="id"
          :scroll="{ y: 200 }"
          :pagination="false"
          :row-selection="props.tableConfig.isMultiple ? rowSelection : null"
          @change="handleTableChange"
        >
          <a-table-column title="#" type="index" width="50" />
          <a-table-column
            v-for="(item, index) in props.tableConfig.columns"
            :key="index"
            :data-index="item.prop"
            :title="item.label"
            :width="item.width"
          />
        </a-table>
        <a-pagination
          :current="pageConfig.page"
          :page-size="pageConfig.limit"
          style="margin-top: 10px"
          :total="pageConfig.total"
          :show-size-changer="false"
          @change="handlePageChange"
        />
      </div>
    </template>
  </a-select>
</template>

<script setup lang="ts">
  import { defineProps, reactive, ref, watch } from 'vue';
  import { request } from '/@/utils/service';
  import XEUtils from 'xe-utils';

  const props = defineProps({
    modelValue: {},
    tableConfig: {
      type: Object,
      default: () => ({
        url: null,
        label: null,
        value: null,
        isTree: false,
        data: [],
        isMultiple: false,
        columns: [],
      }),
    },
    displayLabel: {},
  });

  const emit = defineEmits(['update:modelValue']);

  // 数据定义
  const tableRef = ref();
  const data = ref();
  const multipleSelection = ref<any[]>([]); // 使用 any[] 类型
  const search = ref('');
  const tableData = ref([]);
  const pageConfig = reactive({
    page: 1,
    limit: 10,
    total: 0,
  });

  // 行选择配置
  const rowSelection = {
    onChange: (selectedRowKeys: any, selectedRows: any[]) => {
      multipleSelection.value = selectedRows;
      const { tableConfig } = props;
      const result = selectedRows.map((item: any) => {
        return item[tableConfig.value];
      });
      emit('update:modelValue', result);
    },
  };

  // 表格选择变化处理
  const handleTableChange = (
    pagination: { current: any },
    filters: any,
    sorter: any,
    extra: { action: string },
  ) => {
    if (extra.action === 'paginate') {
      handlePageChange(pagination.current);
    }
  };

  const handlePageChange = (page: number) => {
    pageConfig.page = page;
    getDict();
  };

  const getDict = async () => {
    const url = props.tableConfig.url;
    const params = {
      page: pageConfig.page,
      limit: pageConfig.limit,
      search: search.value,
    };
    const { data, page, limit, total } = await request({
      url,
      params,
    });
    pageConfig.page = page;
    pageConfig.limit = limit;
    pageConfig.total = total;
    tableData.value = props.tableConfig.isTree
      ? XEUtils.toArrayTree(data, {
          parentKey: 'parent',
          key: 'id',
          children: 'children',
        })
      : data;
  };

  const visibleChange = (visible: any) => {
    if (visible) {
      getDict();
    }
  };

  // 处理标签移除事件
  const removeTag = (removedValue: any) => {
    const { tableConfig } = props;
    const newData = data.value.filter((item: any) => item !== removedValue);
    data.value = newData;

    // 更新父组件的 v-model
    const result = newData.map((item: any) => item[tableConfig.value]);
    emit('update:modelValue', result);
  };

  watch(
    () => props.displayLabel, // 确保 props.displayLabel 是一个数组
    (value: any) => {
      // 检查 value 是否是数组
      if (Array.isArray(value)) {
        const result = value.map((item: any) => item[props.tableConfig.label]);
        data.value = result;
      } else {
        data.value = null;
      }
    },
    { immediate: true },
  );
</script>

<style scoped>
  .option {
    height: auto;
    line-height: 1;
    padding: 5px;
    background-color: #fff;
  }
</style>

<style lang="scss">
  .popperClass {
    height: 320px;
  }

  .tableSelector {
    .anticon,
    .ant-tag-close-icon {
      display: none;
    }
  }
</style>
