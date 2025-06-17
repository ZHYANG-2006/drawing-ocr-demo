<template>
  <table
    v-if="tableContent"
    style="
      width: 100%;
      table-layout: fixed;
      border-spacing: 5px;
      border-collapse: separate;
    "
    class="ocr-table"
    @click="handleTableClick"
  >
    <thead>
      <tr>
        <th>
          <div style="overflow-x: scroll">
            <table
              class="table table-bordered"
              style="
                font-size: 10px;
                border-spacing: 5px;
                border-collapse: separate;
              "
            >
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
                      :id="`content-${getCell(rowIndex, columnIndex).type}-${getCell(rowIndex, columnIndex).id}`"
                      :key="`content-${getCell(rowIndex, columnIndex).type}-${getCell(rowIndex, columnIndex).id}`"
                      :rowspan="getCell(rowIndex, columnIndex)?.rowSpan || 1"
                      :colspan="getCell(rowIndex, columnIndex)?.colSpan || 1"
                      :class="{ selected: isSelected(rowIndex, columnIndex) || isSelectedCells(rowIndex, columnIndex) }"
                      style="padding: 5px; cursor: pointer"
                      @click.stop="handleCellClick(rowIndex, columnIndex)"
                    >
                      <template
                        v-if="isImageCell(getCell(rowIndex, columnIndex))"
                      >
                        <img
                          :src="
                            'data:image/jpg;base64,' +
                            getCell(rowIndex, columnIndex).content
                          "
                          style="max-width: 90%; height: auto"
                          alt="Recognized Image"
                        />
                      </template>
                      <template v-else>
                        {{
                          getCell(rowIndex, columnIndex)?.content || ''
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
    selectedCells: Array,
    selectedContent: Object,
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
      tableContent.value?.value?.find(
        (cell) =>
          cell.rowIndex === rowIndex &&
          cell.columnIndex === columnIndex
      ) || null
    );
  }

  function getCellVirtual(rowIndex, columnIndex) {
    return (
      tableContent.value?.value.find(
        (cell) => cell.rowIndex === rowIndex && cell.columnIndex === columnIndex,
      ) || null
    );
  }

  function isImageCell(cell) {
    return cell && cell.image_base64;
  }

  function isSelected(rowIndex, columnIndex) {
    const cell = getCell(rowIndex, columnIndex);
    return (
      props.selectedContent?.id === cell.id &&
      props.selectedContent?.type === 'Cell' &&
      props.selectedContent.rowIndex === rowIndex &&
      props.selectedContent.columnIndex === columnIndex
    );
  }

  function isSelectedCells(rowIndex, columnIndex) {
    if (!props.selectedCells) return false;

    const cell = getCell(rowIndex, columnIndex);
    if (!cell) return false;

    const cellId = cell.id;
    const rowSpan = cell.row_span || 1; // 获取 rowSpan，默认值为 1

    // 如果 rowSpan 为 1，直接判断当前单元格
    if (rowSpan === 1) {
      return props.selectedCells.includes(cellId);
    }

    // 遍历所有受影响的行，检查是否有符合条件的单元格
    for (let i = 0; i < rowSpan; i++) {
      const affectedCell = getCellVirtual(rowIndex + i, columnIndex);
      if (affectedCell && props.selectedCells.includes(affectedCell.id)) {
        return true; // 如果找到符合条件的单元格，则返回 true
      }
    }

    // 如果没有符合条件的单元格，返回 false
    return false;
  }

  // 处理单元格点击事件
  function handleCellClick(rowIndex, columnIndex) {
    const cell = getCell(rowIndex, columnIndex);
    selectedCell.value.rowIndex = rowIndex;
    selectedCell.value.columnIndex = columnIndex;
    emit('update-selected', cell); // 发出 update-selected 事件
    emit('jump-to-page', {
      page: cell.boundingRegions[0].pageNumber,
      polygon: cell.boundingRegions[0].polygon,
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

  watch(
    () => props.selectedCells, // 监听 selectedCells 的变化
    (newSelectedCells, oldSelectedCells) => {
      console.log('selectedCells changed:', {
        newSelectedCells,
        oldSelectedCells,
      });
    },
    { deep: true } // 如果 selectedCells 是一个数组或对象，需要深度监听
  );
</script>

<style scoped>
  .selected {
    border: 3px solid rgb(0, 255, 0) !important; /* 高亮选中单元格 */
  }
  .ocr-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 5px;
  }
  .table-bordered td {
    border: 1px solid #ddd;
    padding: 8px;
  }
</style>
