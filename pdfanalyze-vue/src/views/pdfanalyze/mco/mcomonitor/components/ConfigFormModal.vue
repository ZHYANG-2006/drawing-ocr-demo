<template>
  <a-modal
    v-model:visible="visible"
    title="扫描任务配置"
    @ok="onOk"
    @cancel="visible = false"
  >
    <a-form
      :model="form"
      :rules="rules"
      ref="formRef"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 16 }"
    >
      <!-- 普通字段 -->
      <a-form-item
        label="目录路径"
        name="directory_path"
        :rules="rules.directory_path"
      >
        <a-input
          v-model="form.directory_path"
          placeholder="\\\\server\\\\share 或 /mnt/pdfs"
        />
      </a-form-item>

      <!-- 组合字段：执行时间 -->
      <a-form-item
        label="执行时间"
        style="margin-bottom: 0"
      >
        <a-space>
          <!-- 小时 -->
          <a-form-item
            name="cron_hour"
            :rules="rules.cron_hour"
            :no-style="true"
          >
            <a-input-number
              v-model="form.cron_hour"
              :min="0"
              :max="23"
            /> 时
          </a-form-item>

          <!-- 分钟 -->
          <a-form-item
            name="cron_minute"
            :rules="rules.cron_minute"
            :no-style="true"
          >
            <a-input-number
              v-model="form.cron_minute"
              :min="0"
              :max="59"
            /> 分
          </a-form-item>
        </a-space>
      </a-form-item>

      <!-- 启用 开关 -->
      <a-form-item
        label="启用"
        name="enabled"
      >
        <a-switch
          v-model:checked="form.enabled"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
  import { ref, reactive } from 'vue'
  import { createMonitorConfig, updateMonitorConfig } from '/@/views/pdfanalyze/mco/api/mcomonitor/api.js'

  // 声明 emitted 事件
  const emit = defineEmits(['saved'])

  const visible = ref(false)
  const formRef = ref(null)
  const isEdit = ref(false)

  const form = reactive({
    id: null,
    directory_path: '',
    cron_hour: 2,
    cron_minute: 0,
    enabled: false,
  })

  const rules = {
    directory_path: [{ required: true, message: '请输入目录路径' }],
    cron_hour:       [{ required: true, message: '请输入小时(0-23)' }],
    cron_minute:     [{ required: true, message: '请输入分钟(0-59)' }],
  }

  // 外部调用打开弹窗
  function open(record = null) {
    if (record) {
      Object.assign(form, record)
      isEdit.value = true
    } else {
      form.id = null
      form.directory_path = ''
      form.cron_hour = 2
      form.cron_minute = 0
      form.enabled = false
      isEdit.value = false
    }
    visible.value = true
  }
  defineExpose({ open })

  // 确认按钮
  async function onOk() {
    await formRef.value.validate()
    if (isEdit.value) {
      await updateMonitorConfig(form.id, form)
    } else {
      await createMonitorConfig(form)
    }
    visible.value = false
    // 通知父组件刷新
    emit('saved')
  }
</script>
