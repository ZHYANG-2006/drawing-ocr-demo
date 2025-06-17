<template>
  <!-- 外层表格 -->
  <a-table
    ref="containerRef"
    :columns="columns"
    :data-source="localReviewGroups"
    :bordered="true"
    :scroll="{ x: 3000, y: 600 }"
    :pagination="{
      current: current,
      pageSize: pageSize,
      total: total,
      showSizeChanger: false,
      showQuickJumper: true,
      position: ['bottomLeft'],
    }"
    :rowClassName="rowClassName"
    :expandedRowKeys="expandedRowKeys"
    :rowKey="(record) => record.id"
    style="padding-right: 10px"
    @expand="handleExpand"
    @change="handleTableChange"
  >
    <template #bodyCell="{ column, record }">
      <div :class="{ 'highlighted-row': record.key === highlightedRowKey }">
        <template v-if="column.key === 'operation'">
          <a-button
            type="primary"
            size="small"
            :disabled="record.status !== 'OnGoing'"
            @click="handleStartReview(record)"
          >
            添加
          </a-button>
        </template>
        <template v-if="column.key === 'id'">
          {{ record.id }}
        </template>
        <template v-if="column.key === 'last_status'">
          <a-tag :color="getStatusColor(record.last_status)">
            {{ record.last_status }}
          </a-tag>
        </template>
      </div>
    </template>

    <!-- 内层展开表格 -->
    <template #expandedRowRender="{ record }">
      <a-table
        :columns="innerColumns"
        :data-source="innerData[record.id]"
        :bordered="true"
        :pagination="false"
        :scroll="{ x: 1200, y: 400 }"
        :loading="innerDataLoading[record.id]"
        :class="{ 'highlighted-row': record.key === highlightedRowKey }"
        style="margin-right: 1px"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'operation'">
            <a-button
              type="primary"
              size="small"
              :disabled="record.status !== 'OnGoing'"
              danger
              @click="handleDelete(record)"
            >
              删除
            </a-button>
          </template>
          <template
            v-if="column.editable && column.dataIndex === 'meet_req'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.meet_req,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="meet_reqRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  :disabled="record.status !== 'OnGoing'"
                  class="needed-null"
                  :class="{ 'needed-null': record.meet_req === null }"
                  @blur="handleSave(record)"
                  @change="(value) => handleMeetRequirementChange(value, record)"
                >
                  <a-select-option
                    v-for="option in column.options"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-form>
          </template>
          <template
            v-if="
              column.editable && column.dataIndex === 'is_execute'
            "
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.is_execute,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="is_executeRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  :disabled="!isEditable(record) || record.status !== 'OnGoing'"
                  :class="{
                    'needed-null':
                      record.is_execute === '',
                  }"
                  @blur="handleSave(record)"
                >
                  <a-select-option
                    v-for="option in column.options"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-form>
          </template>
          <template v-if="column.editable && column.dataIndex === 'mflex_file'">
            <a-form
              :model="record"
              ref="mflex_fileRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-input
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  :disabled="
                    !isEditable(record) || record.status !== 'OnGoing'
                  "
                  :class="{
                    'needed-null':
                      record.meet_req === 'Y' && record.is_execute === '',
                  }"
                  @blur="handleSave(record)"
                />
              </a-form-item>
            </a-form>
          </template>
          <template v-if="column.editable && column.dataIndex === 'remark'">
            <a-form
              :model="record"
              ref="remarkRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-input
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  :disabled="
                    !isEditable(record) || record.status !== 'OnGoing'
                  "
                  @blur="handleSave(record)"
                />
              </a-form-item>
            </a-form>
          </template>
        </template>
      </a-table>
    </template>
  </a-table>
</template>

<script setup>
  import { ref, onMounted, nextTick, computed, reactive, watch } from 'vue';
  import {
    getReview,
    saveReview,
    deleteItem,
  } from '/@/views/pdfanalyze/csrfile/api/viewer/viewer.js';
  import { useFileStore } from '/@/views/pdfanalyze/csrfile/stores/fileStore.js';
  import { message } from 'ant-design-vue';
  const emit = defineEmits(['select-cells']); // 添加 update-selected 事件
  const fileStore = useFileStore();
  const reviewId = fileStore.fileId;
  const containerRef = ref(null);

  const props = defineProps({
    reviewGroups: Array, // 接收父组件传递的 reviewGroups 数据
  });
  const localReviewGroups = reactive([...props.reviewGroups]);
  const expandedRowKeys = ref([]);

  const pagination = ref({
    current: 1,
    pageSize: 10, // 外层表格分页大小
  });
  const current = ref(1); // 当前页码
  const pageSize = ref(10);
  const total = ref(0);

  const meet_reqRef = ref(null);
  const is_executeRef = ref(null);
  const mflex_fileRef = ref(null);

  const fieldRequired = reactive({
    meet_req: true,
    is_execute: false,
    mflex_file: false,
    remark: false,
    group: false,
    create_datetime: false,
  });

  const columns = [
    {
      title: 'Operation', key: 'operation', align: 'left', width: 80, fixed: 'left',
    },
    {
      title: 'last_status',
      dataIndex: 'last_status',
      key: 'last_status',
      editable: true,
      width: 80,
      align: 'left',
      fixed: 'left',
    },
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      editable: true,
      width: 2000,
      align: 'left',
    },
  ];

  const innerColumns = computed(() => {
    const commonColumns = [
      { title: 'Operation', key: 'operation', align: 'left', width: 80, fixed: 'left', },
      {
        title: 'Meet requirement',
        dataIndex: 'meet_req',
        key: 'meet_req',
        editable: true,
        options: [
          { value: 'Y', label: '是' },
          { value: 'N', label: '否' },
        ],
        width: 150,
      },
    ];
    commonColumns.push(
      {
        title: '是否执行',
        dataIndex: 'is_execute',
        key: 'is_execute',
        editable: true,
        options: [
          { value: 'Y', label: '是' },
          { value: 'N', label: '否' },
        ],
        width: 150,
      },
      {
        title: 'MFLEX 内部文件+编号',
        dataIndex: 'mflex_file',
        key: 'mflex_file',
        editable: true,
        width: 150,
      },
      { title: 'Remark', dataIndex: 'remark', key: 'remark', editable: true, width: 100, },
      {
        title: '创建时间',
        dataIndex: 'create_datetime',
        key: 'create_datetime',
        width: 250,
      }
    );
    return commonColumns;
  });

  const highlightedRowKey = ref(null); // 当前高亮的行
  const rowClassName = (record) => {
    return record.key === highlightedRowKey.value ? 'highlighted-row' : '';
  };
  const innerData = ref({}); // 存储每个 ReviewGroup 的 ReviewResults 数据
  const innerDataLoading = ref({}); // 存储每个 ReviewGroup 的加载状态

  // 动态加载 ReviewResults 数据
  const fetchReviewResults = async (groupId) => {
    innerDataLoading.value[groupId] = true;
    const response = await getReview(groupId);

    // 处理并转换数据
    const processedData = response.data.map(item => {
      // 创建数据的浅拷贝以避免修改原始数据
      const newItem = { ...item };
      // numericFields.forEach(field => {
      //   if (newItem.hasOwnProperty(field)) {
      //     const value = newItem[field];
      //     // 检查值是否为字符串且可以转换为数字
      //     if (typeof value === 'string' && !isNaN(value)) {
      //       newItem[field] = Number(value);
      //     }
      //   }
      // });

      return newItem;
    });

    innerData.value[groupId] = processedData;
    innerData.value[groupId].sort((a, b) => {
      // 转换 create_datetime 为 Date 对象进行比较
      const dateA = new Date(a.create_datetime);
      const dateB = new Date(b.create_datetime);

      // 返回排序结果：升序（如果想降序，交换返回值）
      return dateB - dateA;  // 升序，若要降序，使用 `return dateB - dateA;`
    });
    innerDataLoading.value[groupId] = false;
  };

  const handleTableChange = (pagination) => {
    // 更新当前页和每页条数
    current.value = pagination.current;
    pageSize.value = pagination.pageSize;
  };

  const handleExpand = (expanded, record) => {
    fetchReviewResults(record.id);
    if (expanded) {
      handleCellSelect(record);
      highlightedRowKey.value = record.key;
      // 展开时，如果该行的ID不在 expandedRowKeys 中，则添加进去
      if (!expandedRowKeys.value.includes(record.key)) {
        expandedRowKeys.value = [...expandedRowKeys.value, record.key]; // 保持现有的展开行并添加当前展开的行
      }
    } else {
      // 收起时，移除该行的ID
      expandedRowKeys.value = expandedRowKeys.value.filter(
        (key) => key !== record.key,
      );
    }
    nextTick(() => {
      console.log('expandedRowKeys (after)', expandedRowKeys.value);
    });
  };

  const handleCellSelect = (record) => {
    emit('select-cells', record);
  };

  // 处理点击 "添加" 按钮
  const handleStartReview = async (record) => {
    const currentDate = new Date();

// 获取年、月、日、时、分、秒
    const year = currentDate.getFullYear();
    const month = String(currentDate.getMonth() + 1).padStart(2, '0'); // 月份是从0开始的，所以要加1
    const day = String(currentDate.getDate()).padStart(2, '0');
    const hours = String(currentDate.getHours()).padStart(2, '0');
    const minutes = String(currentDate.getMinutes()).padStart(2, '0');
    const seconds = String(currentDate.getSeconds()).padStart(2, '0');
// 格式化为 YYYY-MM-DD HH:MM:SS
    const formattedDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    // 向对应的子表格数据源中插入一行新数据
    const newRow = {
      meet_req: '',
      is_execute: '',
      mflex_file: '',
      remark: '',
      last_status: 'ERROR',
      status: 'OnGoing',
      group: record.id,
      create_datetime: formattedDate,
      key: Date,
    };
    if (!innerData.value[record.id]) {
      innerData.value[record.id] = []; // 初始化子表数据源
    }
    handleSave(newRow);
    // innerData.value[record.id].push(newRow);
    innerData.value[record.id].sort((a, b) => {
      // 转换 create_datetime 为 Date 对象进行比较
      const dateA = new Date(a.create_datetime);
      const dateB = new Date(b.create_datetime);

      // 返回排序结果：升序（如果想降序，交换返回值）
      return dateB - dateA;  // 升序，若要降序，使用 `return dateB - dateA;`
    });
    await handleExpand(true, record);
  };

  const handleDelete = async (record) => {
    const groupid = record.group;
    if (record.id && record.id !== '') {
      deleteItem(record.id)
        .then((response) => {
          if (!record.id) {
            fetchReviewResults(groupid);
          }
          message.success('保存成功');
          const targetRecord = localReviewGroups.find(rg => rg.id === groupid);

          if (!targetRecord) {
            console.error(`未找到 group ID 为 ${groupid} 的 targetRecord`);
            return;
          }
          if (
            innerData &&
            innerData.value &&
            Array.isArray(innerData.value[groupid])
          ) {
            innerData.value[groupid] = innerData.value[groupid].filter(
              (item) => item.id !== record.id
            );
            console.log(`成功删除 group ${groupid} 中 id 为 ${record.id} 的项。`);
          } else {
            console.error(`无法找到 group ${groupid} 或其不是一个数组。`);
          }

          const relatedInnerData = innerData.value[groupid];

          let newStatus;

          if (!relatedInnerData || relatedInnerData.length === 0) {
            // innerData 为空
            newStatus = 'EMPTY';
          } else if (relatedInnerData.every(item => item.last_status === 'SUCCESS')) {
            // 所有 innerData 的 last_status 都为 'SUCCESS'
            newStatus = 'SUCCESS';
          } else {
            // 其他情况
            newStatus = 'ERROR';
          }
          if (targetRecord.last_status !== newStatus) {
            targetRecord.last_status = newStatus;
          }
        })
        .catch((error) => {
          console.error('保存失败', error);
        });

    }
    fetchReviewResults(groupid);
  };

  const handleSave = (record) => {
    Object.keys(fieldRequired).forEach(key => {
      fieldRequired[key] = false;
    });
    fieldRequired.meet_req = true;
    /*
    try {
      record.standardValue = Number(record.standardValue) || null;
      record.limitUp = Number(record.limitUp) || null;
      record.limitDown = Number(record.limitDown) || null;
    } catch (error) {
      message.warn('请输入数字');
      record.last_status = 'ERROR';
    }*/
    // 可以在这里进行字段的验证、格式化等
    console.log('保存数据', record);
    let msg = '当前栏位';
    if (!record.meet_req || record.meet_req === '') {
      msg += '[Meet requirement]';
    }
    if (record.meet_req === 'Y') {
      if ((!record.is_execute || record.is_execute === '')) {
        record.is_execute = 'Y';
      }
      if (!record.mflex_file || record.mflex_file === '') {
        msg += '[MFLEX 内部文件+编号]';
        fieldRequired.mflex_file = true;
        record.last_status = 'ERROR';
      }
    } else if (record.meet_req === 'N') {
      if ((!record.is_execute || record.is_execute === '')) {
        record.is_execute = 'N';
      }
    }
    nextTick(() => {
      if (meet_reqRef.value) {
        meet_reqRef.value.validate().then(() => {
          console.log('1');
        });
      }
      if (is_executeRef.value) {
        is_executeRef.value.validate().then(() => {
          console.log('1');
        });
      }
      mflex_fileRef.value.validate().then(() => {
        console.log('1');
      });
    });

    if (msg !== '当前栏位') {
      // 显示警告消息
      message.warning(`${msg}须填写`);

      // 更新数据库中的记录
      updateDatabase(record)
        .then((response) => {
          if (!record.id) {
            fetchReviewResults(record.group);
          }
          const targetRecord = localReviewGroups.find(rg => rg.id === record.group);

          if (!targetRecord) {
            console.error(`未找到 group ID 为 ${record.group} 的 targetRecord`);
            return;
          }

          // 获取与 targetRecord 相关的 innerData
          // 假设 innerData 是一个对象，键是 targetRecord.id，值是数组
          const relatedInnerData = innerData.value[targetRecord.id];

          let newStatus;

          if (!relatedInnerData || relatedInnerData.length === 0) {
            // innerData 为空
            newStatus = 'EMPTY';
          } else if (relatedInnerData.every(item => item.last_status === 'SUCCESS')) {
            // 所有 innerData 的 last_status 都为 'SUCCESS'
            newStatus = 'SUCCESS';
          } else {
            // 其他情况
            newStatus = 'ERROR';
          }
          if (targetRecord.last_status !== newStatus) {
            targetRecord.last_status = newStatus;
          }
        })
        .catch((error) => {
          console.error('保存失败', error);
        });

      // 查找与当前记录相关的 targetRecord
      const targetRecord = localReviewGroups.find(rg => rg.id === record.group);

      if (!targetRecord) {
        console.error(`未找到 group ID 为 ${record.group} 的 targetRecord`);
        return;
      }

      // 获取与 targetRecord 相关的 innerData
      // 假设 innerData 是一个对象，键是 targetRecord.id，值是数组
      const relatedInnerData = innerData.value[targetRecord.id];

      let newStatus;

      if (!relatedInnerData || relatedInnerData.length === 0) {
        // innerData 为空
        newStatus = 'EMPTY';
      } else if (relatedInnerData.every(item => item.last_status === 'SUCCESS')) {
        // 所有 innerData 的 last_status 都为 'SUCCESS'
        newStatus = 'SUCCESS';
      } else {
        // 其他情况
        newStatus = 'ERROR';
      }

      if (targetRecord.last_status !== newStatus) {
        targetRecord.last_status = newStatus;
      }
    }
    else {
      record.last_status = 'SUCCESS';
      // 这里模拟同步操作，例如调用 API 保存数据到数据库
      updateDatabase(record)
        .then((response) => {
          if (!record.id) {
            fetchReviewResults(record.group);
          }
          message.success('保存成功');
          const targetRecord = localReviewGroups.find(rg => rg.id === record.group);

          if (!targetRecord) {
            console.error(`未找到 group ID 为 ${record.group} 的 targetRecord`);
            return;
          }

          // 获取与 targetRecord 相关的 innerData
          // 假设 innerData 是一个对象，键是 targetRecord.id，值是数组
          const relatedInnerData = innerData.value[targetRecord.id];

          let newStatus;

          if (!relatedInnerData || relatedInnerData.length === 0) {
            // innerData 为空
            newStatus = 'EMPTY';
          } else if (relatedInnerData.every(item => item.last_status === 'SUCCESS')) {
            // 所有 innerData 的 last_status 都为 'SUCCESS'
            newStatus = 'SUCCESS';
          } else {
            // 其他情况
            newStatus = 'ERROR';
          }
          if (targetRecord.last_status !== newStatus) {
            targetRecord.last_status = newStatus;
          }
        })
        .catch((error) => {
          console.error('保存失败', error);
        });
    }
  };

  // 示例：更新数据库的方法
  const updateDatabase = async (record) => {
    // 你可以使用 axios 或其他 HTTP 库向后端 API 发送请求
    try {
      const response = await saveReview({
        versionId: reviewId,
        record: record,
      });
      return response.data;
    } catch (error) {
      console.error('保存失败', error);
      throw error;
    }
  };

  // 添加滚动到指定内容的方法
  function scrollToSelectedContent(data) {
    if (data && data.review_group_id) {
      highlightedRowKey.value = data.review_group_id;

      // 获取目标行在所有数据中的索引
      const rowIndex = localReviewGroups.findIndex(
        (item) => item.key === data.review_group_id,
      );
      if (rowIndex === -1) return;
      // 根据每页的条目数计算目标行所在的页码
      const targetPage = Math.floor(rowIndex / pagination.value.pageSize) + 1;

      // 更新分页器的当前页码
      current.value = targetPage;

      // 延迟一段时间确保分页已经更新
      nextTick(() => {
        // 获取目标页的数据并滚动到该行
        const table = containerRef.value;
        const rowElement =
          table.$el.querySelectorAll('.ant-table-row')[
            rowIndex % pageSize.value
          ];
        if (rowElement) {
          rowElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          // rowElement.classList.add('highlighted-row'); // 添加一个高亮的CSS类
        }
        const targetRecord = localReviewGroups.find(rg => rg.id === data.review_group_id);
        handleExpand(true, targetRecord);
      });
    }
  }

  // 是否识别到特性的判断
  function isEditable(record) {
    return record.meet_req === 'Y' || record.meet_req === 'N';
  }

  const handleMeetRequirementChange = (selectedValue, record) => {
    if (selectedValue === 'N') {
      const resetValues = {
        is_execute: 'N',
        mflex_file: '',
        remark: '',
        last_status: 'SUCCESS',
      };
      Object.keys(resetValues).forEach(key => {
        record[key] = resetValues[key];
      });
    }
  };
  function getStatusColor(status) {
    switch (status) {
      case 'SUCCESS':
        return 'green';
      case 'EMPTY':
        return 'blue';
      case 'ERROR':
        return 'red';
      default:
        return 'default';
    }
  };
  watch(
    () => props.reviewGroups,
    (newGroups) => {
      // 清空并重新赋值
      localReviewGroups.splice(0, localReviewGroups.length, ...newGroups);
    }
  );
  defineExpose({ scrollToSelectedContent });

  // 初始化时获取数据
  onMounted(() => {
    total.value = localReviewGroups.length;
  });
</script>
<style>
  .highlighted-row {
    background-color: #90ee90 !important; /* 高亮样式 */
    transition: background-color 0.3s ease;
  }
  .needed-null {
    border-color: red !important; /* 设置边框颜色为红色 */
  }
</style>
