<template>
  <div class="table-container">
    <a-table
      v-loading="config.loading"
      :data-source="data"
      :bordered="setBorder"
      :pagination="false"
      :row-key="'id'"
      row-selection="config.isSelection"
      :columns="setHeader"
      v-bind="$attrs"
      @change="onSelectionChange"
    >
      <template #bodyCell="{ text, column }">
        <template v-if="column.type === 'image'">
          <img :src="text" :width="column.width" :height="column.height" />
        </template>
        <template v-else>
          {{ text }}
        </template>
      </template>
    </a-table>

    <div class="table-footer mt15">
      <a-pagination
        :current="state.page.pageNum"
        :page-size="state.page.pageSize"
        :page-size-options="[10, 20, 30]"
        :total="config.total"
        show-quick-jumper
        show-size-changer
        @change="onHandleCurrentChange"
        @showSizeChange="onHandleSizeChange"
      />

      <div class="table-footer-tool">
        <CloudDownloadOutlined style="font-size: 22px" @click="onImportTable" />
        <ReloadOutlined style="font-size: 22px" @click="onRefreshTable" />
        <a-popover trigger="click" placement="topRight">
          <template #content>
            <div class="tool-box">
              <a-tooltip title="拖动进行排序">
                <BulbOutlined />
              </a-tooltip>
              <a-checkbox v-model="getConfig.isSerialNo">序号</a-checkbox>
              <a-checkbox v-model="getConfig.isSelection">多选</a-checkbox>
              <a-checkbox
                v-model="state.checkListAll"
                @change="onCheckAllChange"
              >
                列显示
              </a-checkbox>
              <a-checkbox-indeterminate
                :checked="state.checkListIndeterminate"
              />
            </div>
            <a-scroll>
              <div ref="toolSetRef" class="tool-sortable">
                <a-checkbox
                  v-for="v in header"
                  :key="v.key"
                  v-model="v.isCheck"
                  :label="v.title"
                  @change="onCheckChange"
                />
              </div>
            </a-scroll>
          </template>
          <template #trigger>
            <SettingOutlined style="font-size: 22px" />
          </template>
        </a-popover>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="netxTable">
  import { reactive, computed, nextTick, ref } from 'vue';
  import { message } from 'ant-design-vue';
  import table2excel from 'js-table2excel';
  import Sortable from 'sortablejs';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import '/@/theme/tableTool.scss';

  // 定义 header 项目的类型
  interface HeaderItem {
    title: string;
    key: string;
    isCheck: boolean;
    type?: string; // type 是可选项
  }

  // 定义 data 项目的类型
  interface DataItem {
    [key: string]: any; // data 中的项目是动态的，允许任意键值对
  }

  // 定义 config 的类型
  interface Config {
    isSelection?: boolean;
    isSerialNo?: boolean;
    isOperate?: boolean;
    isBorder?: boolean;
    total?: number;
    loading?: boolean; // 添加 loading 属性
  }

  // 定义父组件传过来的值
  const props = defineProps({
    data: {
      type: Array as () => DataItem[], // 将 data 定义为 DataItem 数组
      default: () => [],
    },
    header: {
      type: Array as () => HeaderItem[], // 将 header 定义为 HeaderItem 数组
      default: () => [],
    },
    config: {
      type: Object as () => Config, // 将 config 定义为 Config 对象
      default: () => ({}),
    },
  });

  const emit = defineEmits(['delRow', 'pageChange', 'sortHeader']);

  const toolSetRef = ref();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const state = reactive({
    page: {
      pageNum: 1,
      pageSize: 10,
    },
    selectlist: [],
    checkListAll: true,
    checkListIndeterminate: false,
  });

  const setBorder = computed(() => {
    return props.config.isBorder;
  });

  const getConfig = computed(() => {
    return props.config;
  });

  const setHeader = computed(() => {
    return props.header
      .filter((v) => v.isCheck)
      .map((v) => ({
        title: v.title,
        dataIndex: v.key,
        key: v.key,
        type: v.type || 'text',
      }));
  });

  const onCheckAllChange = (val: any) => {
    if (val) props.header.forEach((v) => (v.isCheck = true));
    else props.header.forEach((v) => (v.isCheck = false));
    state.checkListIndeterminate = false;
  };

  const onCheckChange = () => {
    const headers = props.header.filter((v) => v.isCheck).length;
    state.checkListAll = headers === props.header.length;
    state.checkListIndeterminate = headers > 0 && headers < props.header.length;
  };

  const onSelectionChange = (val: never[]) => {
    state.selectlist = val;
  };

  const onDelRow = (row: any) => {
    emit('delRow', row);
  };

  const onHandleSizeChange = (size: number) => {
    state.page.pageSize = size;
    emit('pageChange', state.page);
  };

  const onHandleCurrentChange = (page: number) => {
    state.page.pageNum = page;
    emit('pageChange', state.page);
  };

  const pageReset = () => {
    state.page.pageNum = 1;
    state.page.pageSize = 10;
    emit('pageChange', state.page);
  };

  const onImportTable = () => {
    if (state.selectlist.length <= 0)
      return message.warning('请先选择要导出的数据');
    table2excel(
      props.header,
      state.selectlist,
      `${themeConfig.value.globalTitle} ${new Date().toLocaleString()}`,
    );
  };

  const onRefreshTable = () => {
    emit('pageChange', state.page);
  };

  const onSetTable = () => {
    nextTick(() => {
      const sortable = Sortable.create(toolSetRef.value, {
        handle: '.handle',
        dataIdAttr: 'data-key',
        animation: 150,
        onEnd: () => {
          const headerList: any[] = [];
          sortable.toArray().forEach((val: any) => {
            props.header.forEach((v) => {
              if (v.key === val) headerList.push({ ...v });
            });
          });
          emit('sortHeader', headerList);
        },
      });
    });
  };

  defineExpose({
    pageReset,
  });
</script>

<style scoped lang="scss">
  .table-container {
    display: flex;
    flex-direction: column;
    .ant-table {
      flex: 1;
    }
    .table-footer {
      display: flex;
      .table-footer-tool {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        i {
          margin-right: 10px;
          cursor: pointer;
          &:last-of-type {
            margin-right: 0;
          }
        }
      }
    }
  }
</style>
