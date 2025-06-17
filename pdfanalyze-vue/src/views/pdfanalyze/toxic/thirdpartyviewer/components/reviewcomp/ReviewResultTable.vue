<template>
  <!-- 外层表格 -->
  <a-table
    ref="containerRef"
    :columns="columns"
    :data-source="props.reviewGroups"
    :bordered="true"
    :scroll="{ x: 3000, y: 600 }"
    :pagination="{
      current: current,
      pageSize: pageSize,
      total: total,
      showSizeChanger: true,
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
            @click="handleStartReview(record)"
          >
            添加
          </a-button>
        </template>
        <template v-if="column.key === 'id'">
          {{ record.id }}
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
        :loading="innerDataLoading[record.id]"
        :class="{ 'highlighted-row': record.key === highlightedRowKey }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'operation'">
            <a-button
              type="primary"
              size="small"
              danger
              @click="handleDelete(record)"
            >
              删除
            </a-button>
          </template>
          <template
            v-if="column.editable && column.dataIndex === 'feature_recognized'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.feature_recognized,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="feature_recognizedRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  class="needed-null"
                  :class="{ 'needed-null': record.feature_recognized === null }"
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
          <template
            v-if="
              column.editable && column.dataIndex === 'plm_standard_process'
            "
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.plm_standard_process,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="plm_standard_processRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record)"
                  :class="{
                    'needed-null':
                      record.plm_standard_process === '' && process === 'FPC',
                  }"
                  @change="handleCustomInput"
                  @blur="handleSave(record)"
                >
                  <a-select-option
                    v-for="option in options_plm"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.value }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-form>
          </template>
          <template
            v-if="column.editable && column.dataIndex === 'plm_device_type'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.plm_device_type,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="plm_device_typeRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record)"
                  :class="{
                    'needed-null':
                      record.plm_device_type === null && process === 'FPC',
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
          <template
            v-if="column.editable && column.dataIndex === 'plm_procedure'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.plm_procedure,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="plm_procedureRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :class="{
                    'needed-null':
                      record.plm_procedure === null && process === 'FPC',
                  }"
                  :disabled="!isEditable(record)"
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
          <template v-if="column.editable && column.dataIndex === 'function22'">
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.function22,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="function22Ref"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record)"
                  :class="{
                    'needed-null': record.function22 === null && PFMEA === 'FMEA5',
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
          <template v-if="column.editable && column.dataIndex === 'function23'">
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.function23,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="function23Ref"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record)"
                  :class="{
                    'needed-null': record.function23 === null && PFMEA === 'FMEA5',
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
          <template
            v-if="column.editable && column.dataIndex === 'feature_category'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.feature_category,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="feature_categoryRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record)"
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
          <template
            v-if="column.editable && column.dataIndex === 'checkCategory'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.checkCategory,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="checkCategoryRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record)"
                  @blur="handleSave(record)"
                >
                  <a-select-option
                    v-for="option in column.options"
                    :key="option.value"
                    :title="option.remark"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-form>
          </template>
          <template
            v-if="column.editable && column.dataIndex === 'checkedQuest'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.checkedQuest,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="checkedQuestRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  mode="tags"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record)"
                  @blur="handleSave(record)"
                  @change="(value) => handleSelectChange(value, record)"
                >
                  <a-select-option
                    v-for="option in options_checkitem.filter(option => {
                      const checkCategory = record.checkCategory === ''
                        ? true
                        : (record.checkCategory === 'VAR' || record.checkCategory === 'VAR-REF')
                          ? option.checkCategory === 'VAR'
                          : option.checkCategory === record.checkCategory;
                      return checkCategory;
                    })"
                    :key="option.ID"
                    :value="option.checkedQuest"
                  >
                    {{ option.checkedQuest }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-form>
          </template>
          <template v-if="column.editable && column.dataIndex === 'checkRule'">
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.checkRule,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="checkRuleRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-input
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  :disabled="
                    !isEditable(record) ||
                    record.checkCategory === 'VAR' ||
                    record.checkCategory === 'VAR-REF' ||
                    isVIS(record)
                  "
                  @blur="handleSave(record)"
                />
              </a-form-item>
            </a-form>
          </template>
          <template v-if="column.editable && column.dataIndex === 'limitType'">
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.limitType,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="limitTypeRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record) || isVIS(record) || isATT(record)"
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
          <template
            v-if="column.editable && column.dataIndex === 'standardValue'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.standardValue,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="standardValueRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-input
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  :disabled="!isEditable(record) || isVIS(record) || isATT(record)"
                  @blur="handleSave(record)"
                />
              </a-form-item>
            </a-form>
          </template>
          <template v-if="column.editable && column.dataIndex === 'limitUp'">
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    type: 'number',
                    min: 0,
                    message: '请输入大于或等于0的数字',
                    trigger: 'blur',
                  },
                  {
                    required: fieldRequired.limitUp,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="limitUpRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-input
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  :disabled="
                    !isEditable(record) ||
                    isVar_Limitdown(record) ||
                    isVIS(record) ||
                    isATT(record)
                  "
                  @blur="handleSave(record)"
                />
              </a-form-item>
            </a-form>
          </template>
          <template
            v-if="column.editable && column.dataIndex === 'containLimitUp'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.containLimitUp,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="containLimitUpRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="
                    !isEditable(record) ||
                    isVar_Limitdown(record) ||
                    isVIS(record) ||
                    isATT(record)
                  "
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
          <template v-if="column.editable && column.dataIndex === 'limitDown'">
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    type: 'number',
                    max: 0,
                    message: '请输入小于或等于0的数字',
                    trigger: 'blur',
                  },
                  {
                    required: fieldRequired.limitDown,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="limitDownRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-input
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  :disabled="
                    !isEditable(record) ||
                    isVar_Limitup(record) ||
                    isVIS(record) ||
                    isATT(record)
                  "
                  @blur="handleSave(record)"
                />
              </a-form-item>
            </a-form>
          </template>
          <template
            v-if="column.editable && column.dataIndex === 'containLimitDown'"
          >
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.containLimitDown,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="containLimitDownRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="
                    !isEditable(record) ||
                    isVar_Limitup(record) ||
                    isVIS(record) ||
                    isATT(record)
                  "
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
          <template v-if="column.editable && column.dataIndex === 'unitCode'">
            <a-form
              :model="record"
              :rules="{
                [column.dataIndex]: [
                  {
                    required: fieldRequired.unitCode,
                    trigger: 'blur',
                    message: '必填',
                  },
                ],
              }"
              ref="unitCodeRef"
            >
              <a-form-item :name="column.dataIndex">
                <a-select
                  v-model:value="record[column.dataIndex]"
                  mode="tags"
                  style="width: 100%"
                  show-search
                  allow-clear
                  :disabled="!isEditable(record) || isVIS(record) || isATT(record)"
                  @blur="handleSave(record)"
                  @change="(value) => handleSelectChangeUnit(value, record)"
                >
                  <a-select-option
                    v-for="option in options_checkitem_unit"
                    :key="option.ID"
                    :value="option.unitCode"
                  >
                    {{ option.unitCode }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-form>
          </template>
        </template>
      </a-table>
    </template>
  </a-table>
</template>

<script setup>
  import { ref, onMounted, nextTick, computed, reactive } from 'vue';
  import {
    getReview,
    saveReview,
    getPLMStandard,
    getCheckItem,
    deleteItem,
  } from '/@/views/pdfanalyze/cppqcp/api/viewer/viewer.js';
  import { useFileStore } from '/@/views/pdfanalyze/cppqcp/stores/fileStore.js';
  import { message } from 'ant-design-vue';
  const emit = defineEmits(['select-cells']); // 添加 update-selected 事件
  const fileStore = useFileStore();
  const reviewId = fileStore.fileId;
  const process = fileStore.process;
  const PFMEA = fileStore.PFMEA;
  const containerRef = ref(null);

  const props = defineProps({
    reviewGroups: Array, // 接收父组件传递的 reviewGroups 数据
  });
  const selectedValue_plm = ref(null);
  const options_plm = ref([]);
  const options_checkitem = ref([]);
  const options_checkitem_unit = ref([]);

  const expandedRowKeys = ref([]);

  const pagination = ref({
    current: 1,
    pageSize: 10, // 外层表格分页大小
  });
  const current = ref(1); // 当前页码
  const pageSize = ref(10);
  const total = ref(0);

  const feature_recognizedRef = ref(null);
  const plm_standard_processRef = ref(null);
  const plm_device_typeRef = ref(null);
  const plm_procedureRef = ref(null);
  const function22Ref = ref(null);
  const function23Ref = ref(null);
  const feature_categoryRef = ref(null);
  const checkCategoryRef = ref(null);
  const checkedQuestRef = ref(null);
  const checkRuleRef = ref(null);
  const limitTypeRef = ref(null);
  const standardValueRef = ref(null);
  const limitUpRef = ref(null);
  const containLimitUpRef = ref(null);
  const limitDownRef = ref(null);
  const containLimitDownRef = ref(null);
  const unitCodeRef = ref(null);

  const fieldRequired = reactive({
    feature_recognized: true,
    plm_standard_process: false,
    plm_device_type: false,
    plm_procedure: false,
    function22: false,
    function23: false,
    feature_category: false,
    checkCategory: false,
    checkedQuest: false,
    checkRule: false,
    limitType: false,
    standardValue: false,
    limitUp: false,
    containLimitUp: false,
    limitDown: false,
    containLimitDown: false,
    unitCode: false,
    group_id: false,
    create_datetime: false,
  });

  const columns = [
    {
      title: 'Operation', key: 'operation', align: 'left', width: 80,
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
      { title: 'Operation', key: 'operation', align: 'left', width: 80, },
      {
        title: '是否识别到特性',
        dataIndex: 'feature_recognized',
        key: 'feature_recognized',
        editable: true,
        options: [
          { value: 'Y', label: '是' },
          { value: 'N', label: '否' },
        ],
        width: 150,
      },
      {
        title: 'PLM标准工序',
        dataIndex: 'plm_standard_process',
        key: 'plm_standard_process',
        editable: true,
        width: 150,
      },
    ];
    if (process === 'FPC') {
      commonColumns.push({
        title: '设备类别',
        dataIndex: 'plm_device_type',
        key: 'plm_device_type',
        editable: true,
        width: 150,
      });
      commonColumns.push({
        title: '步骤',
        dataIndex: 'plm_procedure',
        key: 'plm_procedure',
        editable: true,
        width: 150,
      });
    }
    if (PFMEA === 'FMEA5') {
      commonColumns.push({
        title: '2.2功能',
        dataIndex: 'function22',
        key: 'function22',
        editable: true,
        width: 150,
      });
      commonColumns.push({
        title: '2.3功能',
        dataIndex: 'function23',
        key: 'function23',
        editable: true,
        width: 150,
      });
    }
    commonColumns.push(
      {
        title: '特性类别',
        dataIndex: 'feature_category',
        key: 'feature_category',
        editable: true,
        options: [
          { value: '产品特性', label: '产品特性' },
          { value: '过程特性', label: '过程特性' },
        ],
        width: 100,
      },
      {
        title: '特性类型',
        dataIndex: 'checkCategory',
        key: 'checkCategory',
        editable: true,
        options: [
          { value: 'VAR', label: 'VAR', remark: '计量数据，管控data在spec內' },
          {
            value: 'VAR-REF',
            label: 'VAR-REF',
            remark: '计量数据，不管控data在spec內，仅收集data',
          },
          {
            value: 'ATT',
            label: 'ATT',
            remark: '计数型数据，管控是否符合要求',
          },
          { value: 'VIS', label: 'VIS', remark: '目视型' },
          {
            value: 'TEXT',
            label: 'TEXT',
            remark: 'data可维护文本或数据，仅记录',
          },
        ],
        width: 150,
      },
      {
        title: '特性名称',
        dataIndex: 'checkedQuest',
        key: 'checkedQuest',
        editable: true,
        width: 300,
      },
      {
        title: 'ATT描述',
        dataIndex: 'checkRule',
        key: 'checkRule',
        editable: true,
        width: 150,
      },
      {
        title: '公差类型',
        dataIndex: 'limitType',
        key: 'limitType',
        editable: true,
        options: [
          { value: '单边上公差', label: '单边上公差' },
          { value: '单边下公差', label: '单边下公差' },
          { value: '双边公差', label: '双边公差' },
        ],
        width: 150,
      },
      {
        title: '目标值',
        dataIndex: 'standardValue',
        key: 'standardValue',
        editable: true,
        width: 100,
      },
      { title: '上公差', dataIndex: 'limitUp', key: 'limitUp', editable: true, width: 100, },
      {
        title: '上公差包含',
        dataIndex: 'containLimitUp',
        key: 'containLimitUp',
        editable: true,
        options: [
          { value: 'Y', label: '是' },
          { value: 'N', label: '否' },
        ],
        width: 100,
      },
      {
        title: '下公差',
        dataIndex: 'limitDown',
        key: 'limitDown',
        editable: true,
        width: 100,
      },
      {
        title: '下公差包含',
        dataIndex: 'containLimitDown',
        key: 'containLimitDown',
        editable: true,
        options: [
          { value: 'Y', label: '是' },
          { value: 'N', label: '否' },
        ],
        width: 100,
      },
      { title: '单位', dataIndex: 'unitCode', key: 'unitCode', editable: true, width: 100, },
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
    console.log('response12313sada', response);
    innerData.value[groupId] = response.data;
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
    if (expanded) {
      console.log('element_ids', record.element_ids);
      handleCellSelect(record);
      highlightedRowKey.value = record.key;
      // 展开时，如果该行的ID不在 expandedRowKeys 中，则添加进去
      if (!expandedRowKeys.value.includes(record.key)) {
        expandedRowKeys.value = [...expandedRowKeys.value, record.key]; // 保持现有的展开行并添加当前展开的行
      }

      // 如果没有加载过数据，则加载数据
      if (!innerData.value[record.id]) {
        fetchReviewResults(record.id);
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

  // 处理用户输入或选择
  const handleCustomInput = (selectedValue) => {
    // 如果用户选择的值不在 options 中，则动态添加
    if (
      selectedValue &&
      !options.value.some((opt) => opt.value === selectedValue)
    ) {
      options.value.push({ value: selectedValue, label: selectedValue });
    }
  };

  // 处理点击 "添加" 按钮
  const handleStartReview = (record) => {
    console.log('添加子表格行', record);
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
      feature_recognized: '', // 是否识别到特性
      plm_standard_process: '', // PLM标准工序
      plm_device_type: '', // 设备类别
      plm_procedure: '', // 步骤
      function22: '', // 2.2功能
      function23: '', // 2.3功能
      feature_category: '', // 特性类别
      checkCategory: '', // 特性类型
      checkedQuest: '', // 特性名称
      checkRule: '', // ATT描述
      limitType: '', // 公差类型
      standardValue: null, // 目标值
      limitUp: null, // 上公差
      containLimitUp: '', // 上公差包含
      limitDown: null, // 下公差
      containLimitDown: '', // 下公差包含
      unitCode: '', // 单位
      group_id: record.id,
      create_datetime: formattedDate,
      key: Date,
    };
    if (!innerData.value[record.id]) {
      innerData.value[record.id] = []; // 初始化子表数据源
    }

    innerData.value[record.id].push(newRow);
    innerData.value[record.id].sort((a, b) => {
      // 转换 create_datetime 为 Date 对象进行比较
      const dateA = new Date(a.create_datetime);
      const dateB = new Date(b.create_datetime);

      // 返回排序结果：升序（如果想降序，交换返回值）
      return dateB - dateA;  // 升序，若要降序，使用 `return dateB - dateA;`
    });
  };

  const handleDelete = async (record) => {
    const groupid = record.group_id;
    if (record.id && record.id !== '') await deleteItem(record.id);
    delete innerData.value[record.key];
    fetchReviewResults(groupid);
  };

  const handleSave = (record) => {
    Object.keys(fieldRequired).forEach(key => {
      fieldRequired[key] = false;
    });
    fieldRequired.feature_recognized = true;
    try {
      record.standardValue = Number(record.standardValue) || null;
      record.limitUp = Number(record.limitUp) || null;
      record.limitDown = Number(record.limitDown) || null;
    } catch (error) {
      message.warn('请输入数字');
    }
    // 可以在这里进行字段的验证、格式化等
    console.log('保存数据', record);
    let msg = '当前栏位';
    if (!record.feature_recognized || record.feature_recognized === '') {
      msg += '[是否识别到特性]';
    }
    if (record.feature_recognized === 'Y') {
      if ((record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (record.limitType === '单边上公差' ||
          record.limitType === '双边公差')) {
        record.containLimitUp = 'Y';
      }
      if ((record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (record.limitType === '单边下公差' ||
          record.limitType === '双边公差')) {
        record.containLimitDown = 'Y';
      }

      if (!record.plm_standard_process || record.plm_standard_process === '') {
        msg += '[PLM标准工序]';
        fieldRequired.plm_standard_process = true;
      }
      if (
        process === 'FPC' &&
        (!record.plm_device_type || record.plm_device_type === '')
      ) {
        msg += '[设备类别]';
        fieldRequired.plm_device_type = true;
      }
      if (
        process === 'FPC' &&
        (!record.plm_procedure || record.plm_procedure === '')
      ) {
        msg += '[步骤]';
        fieldRequired.plm_procedure = true;
      }
      if (
        PFMEA === 'FMEA5' &&
        (!record.function22 || record.function22 === '')
      ) {
        msg += '[2.2功能]';
        fieldRequired.function22 = true;
      }
      if (
        PFMEA === 'FMEA5' &&
        (!record.function23 || record.function23 === '')
      ) {
        msg += '[2.3功能]';
        fieldRequired.function23 = true;
      }
      if (!record.feature_category || record.feature_category === '') {
        msg += '[特性类别]';
        fieldRequired.feature_category = true;
      }
      if (!record.checkCategory || record.checkCategory === '') {
        msg += '[特性类型]';
        fieldRequired.checkCategory = true;
      }
      if (!record.checkedQuest || record.checkedQuest === '') {
        msg += '[特性名称]';
        fieldRequired.checkedQuest = true;
      }
      if (
        record.checkCategory === 'ATT' &&
        (!record.checkRule || record.checkRule === '')
      ) {
        msg += '[ATT描述]';
        fieldRequired.checkRule = true;
      }
      if (
        (record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (!record.limitType || record.limitType === '')
      ) {
        msg += '[公差类型]';
        fieldRequired.limitType = true;
      }
      if (
        (record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (record.limitType === '单边上公差' ||
          record.limitType === '单边下公差' ||
          record.limitType === '双边公差') &&
        (!record.standardValue || record.standardValue === '')
      ) {
        msg += '[目标值]';
        fieldRequired.standardValue = true;
      }
      if (
        (record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (record.limitType === '单边上公差' ||
          record.limitType === '双边公差') &&
        (!record.limitUp || record.limitUp === '')
      ) {
        msg += '[上公差]';
        fieldRequired.limitUp = true;
      }
      if (
        (record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (record.limitType === '单边上公差' ||
          record.limitType === '双边公差') &&
        (!record.containLimitUp || record.containLimitUp === '')
      ) {
        msg += '[上公差包含]';
        fieldRequired.containLimitUp = true;
      }
      if (
        (record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (record.limitType === '单边下公差' ||
          record.limitType === '双边公差') &&
        (!record.limitDown || record.limitDown === '')
      ) {
        msg += '[上公差]';
        fieldRequired.limitDown = true;
      }
      if (
        (record.checkCategory === 'VAR' ||
          record.checkCategory === 'VAR-REF') &&
        (record.limitType === '单边下公差' ||
          record.limitType === '双边公差') &&
        (!record.containLimitDown || record.containLimitDown === '')
      ) {
        msg += '[下公差包含]';
        fieldRequired.containLimitDown = true;
      }
    }
    nextTick(() => {
      if (feature_recognizedRef.value) {
        feature_recognizedRef.value.validate().then(() => {
          console.log('1');
        });
      }
      if (plm_standard_processRef.value) {
        plm_standard_processRef.value.validate().then(() => {
          console.log('1');
        });
      }
      if (plm_device_typeRef.value) {
        plm_device_typeRef.value.validate().then(() => {
          console.log('1');
        });
      }
      if (plm_procedureRef.value) {
        plm_procedureRef.value.validate().then(() => {
          console.log('1');
        });
      }
      if (function22Ref.value) {
        function22Ref.value.validate().then(() => {
          console.log('1');
        });
      }
      if (function23Ref.value) {
        function23Ref.value.validate().then(() => {
          console.log('1');
        });
      }
      if (feature_categoryRef.value) {
        feature_categoryRef.value.validate().then(() => {
          console.log('1');
        });
      }
      if (checkCategoryRef.value) {
        checkCategoryRef.value.validate().then(() => {
          console.log('1');
        });
      }
      if (checkCategoryRef.value) {
        checkedQuestRef.value.validate().then(() => {
          console.log('1');
        });
      }
      checkRuleRef.value.validate().then(() => {
        console.log('1');
      });;
      limitTypeRef.value.validate().then(() => {
        console.log('1');
      });;
      standardValueRef.value.validate().then(() => {
        console.log('1');
      });;
      limitUpRef.value.validate();
      containLimitUpRef.value.validate();
      limitDownRef.value.validate();
      containLimitDownRef.value.validate();
      unitCodeRef.value.validate();
    });


    if (msg !== '当前栏位') message.warning(msg + '须填写')
    else {
      // 这里模拟同步操作，例如调用 API 保存数据到数据库
      updateDatabase(record)
        .then((response) => {
          if (!record.id) {
            fetchReviewResults(record.group_id);
          }
          message.success('保存成功');
          console.log('数据保存成功', response);
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
      const rowIndex = props.reviewGroups.findIndex(
        (item) => item.key === data.review_group_id,
      );
      if (rowIndex === -1) return;
      console.log('rowIndex', rowIndex);
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
      });
    }
  }

  // 是否识别到特性的判断
  function isEditable(record) {
    return record.feature_recognized === 'Y';
  }

  function isVar_Limitup(record) {
    return (
      (record.checkCategory === 'VAR' || record.checkCategory === 'VAR-REF') &&
      record.limitType === '单边上公差'
    );
  }

  function isVar_Limitdown(record) {
    return (
      (record.checkCategory === 'VAR' || record.checkCategory === 'VAR-REF') &&
      record.limitType === '单边下公差'
    );
  }

  function isVar_Double(record) {
    return (
      (record.checkCategory === 'VAR' || record.checkCategory === 'VAR-REF') &&
      record.limitType === '双边公差'
    );
  }

  function isVIS(record) {
    return record.checkCategory === 'VIS';
  }

  function isATT(record) {
    return record.checkCategory === 'ATT';
  }

  function isTEXT(record) {
    return record.checkCategory === 'TEXT';
  }

  const handleInput = (record) => {
    let isCustomTagAllowed = true;
    if (record.checkCategory === 'VIS') isCustomTagAllowed = false; // 根据具体条件动态设置
    if (!isCustomTagAllowed) {
      record[column.dataIndex] = []; // 清空用户的自定义输入
      console.warn('自定义标签不被允许！');
    }
  };

  const handleSelectChange = (selectedValue, record) => {
    console.log('Selected Value:', selectedValue);
    // 确保只允许一个标签
    let selectItem = '';
    if (Array.isArray(selectedValue) && selectedValue.length > 1) {
      selectItem = selectedValue[selectedValue.length - 1];
    }
    record.checkedQuest = selectItem;

    const selectedOption = options_checkitem.value.find(
      (option) => option.checkedQuest === selectItem,
    );
    if (
      (!selectedOption || selectedOption === '') &&
      record.checkCategory === 'VIS'
    ) {
      record.checkedQuest = '';
      message.error('特性类型VIS，不可自定义特性名称');
    }

    if (selectedOption) {
      // 更新字段，如果字段为 null，则赋值为空字符串
      record.checkRule = selectedOption.checkRule ?? '';
      record.limitType =
        ['单边上公差', '单边下公差', '双边公差'].includes(selectedOption.limitType)
          ? selectedOption.limitType
          : '';
      record.unitCode = selectedOption.unitCode ?? '';
    }
  };

  const handleSelectChangeUnit = (selectedValue, record) => {
    console.log('Selected Value:', selectedValue);
    // 确保只允许一个标签
    let selectItem = '';
    if (Array.isArray(selectedValue) && selectedValue.length > 1) {
      selectItem = selectedValue[selectedValue.length - 1];
    }
    record.unitCode = selectItem;

    const selectedOption = options_checkitem_unit.value.find(
      (option) => option.unitCode === selectItem,
    );
  };

  const loadPLMStandardOptions = async () => {
    try {
      const response = await getPLMStandard();
      console.log('response', response);
      // 获取数据
      const data = response.data;

      // 根据 process 的值筛选数据
      let filteredData;
      if (process === 'FPCA') {
        filteredData = data.filter((item) => item.type === 'SMT');
      } else if (process === 'FPC') {
        filteredData = data.filter((item) => item.type === 'FLEX');
      } else {
        // 如果 process 不匹配，可以返回全部数据，或者按其他条件筛选
        filteredData = data;
      }
      options_plm.value = filteredData;
      console.log('response', response);
    } catch (error) {
      console.error('保存失败', error);
      throw error;
    }
  };
  const loadCheckItemOptions = async () => {
    try {
      const response = await getCheckItem();
      // 获取数据
      const data = response.data;
      options_checkitem.value = data;
      options_checkitem_unit.value = data
        .filter((item, index, self) =>
          item.unitCode &&  // 确保 unitCode 不是空字符串或者 null
          index === self.findIndex((t) => t.unitCode === item.unitCode)
        );
      console.log('response', options_checkitem);
    } catch (error) {
      console.error('保存失败', error);
      throw error;
    }
  };
  defineExpose({ scrollToSelectedContent });

  // 初始化时获取数据
  onMounted(() => {
    total.value = props.reviewGroups.length;
    loadPLMStandardOptions();
    loadCheckItemOptions();
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
