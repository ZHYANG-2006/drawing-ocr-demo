<template>
  <table
    v-if="tableContent"
    style="width: 100%; table-layout: fixed"
    class="ocr-table"
    @click="handleTableClick"
  >
    <thead>
      <tr>
        <th>
          <div style="overflow-x: scroll">
            <table class="table table-bordered" style="font-size: 10px">
              <tr
                v-for="(row, rowIndex) in Array.from({
                  length: tableContent.rows_num,
                })"
                :key="rowIndex"
              >
                <template
                  v-for="(col, columnIndex) in Array.from({
                    length: tableContent.cols_num,
                  })"
                >
                  <template v-if="getCell(rowIndex, columnIndex)">
                    <td
                      :key="columnIndex"
                      :rowspan="getCell(rowIndex, columnIndex)?.row_span || 1"
                      :colspan="getCell(rowIndex, columnIndex)?.col_span || 1"
                      :class="{ selected: isSelected(rowIndex, columnIndex) }"
                      style="padding: 1px; cursor: pointer"
                      @click.stop="handleCellClick(rowIndex, columnIndex)"
                    >
                      <template
                        v-if="isImageCell(getCell(rowIndex, columnIndex))"
                      >
                        <img
                          :src="
                            'data:image/jpg;base64,' +
                            getCell(rowIndex, columnIndex).image_base64
                          "
                          style="max-width: 90%; height: auto"
                          alt="Recognized Image"
                        />
                      </template>
                      <template v-else>
                        {{
                          getCell(rowIndex, columnIndex)?.has_strike_through ||
                          getCell(rowIndex, columnIndex)?.has_xbar
                            ? getCell(rowIndex, columnIndex)?.true_thai_value
                            : getCell(rowIndex, columnIndex)?.thai_value || ''
                        }}
                      </template>
                    </td>
                  </template>
                </template>
              </tr>
            </table>
          </div>
        </th>
      </tr>
    </thead>
  </table>
</template>

<script setup>
  import { computed, ref, watch } from 'vue';

  const props = defineProps({
    content: Object,
    isSelected: Boolean, // 用于接收父组件是否选中表格
  });

  const emit = defineEmits(['jump-to-page', 'update-selected']); // 添加 update-selected 事件

  const tableContent = computed(() => {
    if (
      props.content &&
      typeof props.content.rows_num === 'number' &&
      typeof props.content.cols_num === 'number'
    ) {
      return props.content;
    }
    return { rows_num: 0, cols_num: 0, value: [] };
  });

  // 定义一个 ref 用于跟踪选中的单元格
  const selectedCell = ref({ rowIndex: null, columnIndex: null });

  function getCell(rowIndex, columnIndex) {
    return (
      tableContent.value?.cells?.find(
        (cell) => cell.row_index === rowIndex && cell.col_index === columnIndex && !cell.is_virtual,
      ) || null
    );
  }

  function isImageCell(cell) {
    return cell && cell.image_base64;
  }

  function isSelected(rowIndex, columnIndex) {
    return (
      selectedCell.value.rowIndex === rowIndex &&
      selectedCell.value.columnIndex === columnIndex
    );
  }

  // 处理单元格点击事件
  function handleCellClick(rowIndex, columnIndex) {
    const cell = getCell(rowIndex, columnIndex);
    emit('update-selected', props.content); // 发出 update-selected 事件
    emit('jump-to-page', {
      page: cell.page,
      polygon: cell.polygon,
      review_group_id: cell.review_group_id,
    });
  }

  // 监听 isSelected，取消单元格的选中状态
  watch(
    () => props.isSelected,
    (newIsSelected) => {
      if (!newIsSelected) {
        selectedCell.value = { rowIndex: null, columnIndex: null };
      }
    },
  );
</script>

<style scoped>
  .selected {
    border: 1px solid rgb(0, 255, 0) !important; /* 高亮选中单元格 */
  }
  .ocr-table {
    width: 100%;
    border-collapse: collapse;
  }
  .table-bordered td {
    border: 1px solid #ddd;
    padding: 8px;
  }
</style>
