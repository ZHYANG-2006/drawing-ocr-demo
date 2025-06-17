<template>
  <a-table
    :columns="columns"
    :data-source="data"
    :loading="loading"
    row-key="id"
    bordered
    size="small"
  >
    <!-- “执行时间”列的插槽 -->
    <template #cron_time="{ record }">
      {{ record.cron_hour }}:{{ record.cron_minute }}
    </template>

    <!-- “启用”列的插槽，直接把切换后的值作为 $event 传给方法 -->
    <template #enabled="{ record }">
      <a-switch
        :checked="record.enabled"
        @change="toggleConfig(record.id, $event)"
      />
    </template>

    <!-- “操作”列的插槽，@confirm 直接调用方法 -->
    <template #actions="{ record }">
      <a-button type="link" size="small" @click="edit(record)">
        编辑
      </a-button>
      <a-divider type="vertical" />
      <a-popconfirm
        title="确认删除？"
        @confirm="removeConfig(record.id)"
      >
        <a-button type="link" danger size="small">
          删除
        </a-button>
      </a-popconfirm>
    </template>
  </a-table>

  <a-pagination
    v-if="pagination.total > pagination.pageSize"
    style="margin-top:12px; text-align:right;"
    :total="pagination.total"
    :page-size="pagination.pageSize"
    :current="pagination.current"
    @change="onPageChange"
  />
</template>

<script setup>
  import { ref, reactive, onMounted, defineEmits, defineExpose } from 'vue'
  import {
    fetchMonitorConfigs,
    deleteMonitorConfig,
    updateMonitorConfig
  } from '/@/views/pdfanalyze/mco/api/mcomonitor/api.js'

  const emit = defineEmits(['edit', 'delete', 'toggle'])

  const loading = ref(false)
  const data    = ref([])
  const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

  const columns = [
    { title: '目录路径', dataIndex: 'directory_path', key: 'directory_path' },
    { title: '执行时间', dataIndex: 'cron_time', key: 'cron_time', slots: { customRender: 'cron_time' } },
    { title: '启用',     dataIndex: 'enabled',     key: 'enabled',     width: 100, slots: { customRender: 'enabled' } },
    { title: '上次运行', dataIndex: 'last_run',     key: 'last_run' },
    { title: '操作',     key: 'actions',           width: 160, slots: { customRender: 'actions' } },
  ]

  onMounted(() => fetchConfigs())

  async function fetchConfigs(page = 1) {
    loading.value = true
    pagination.current = page
    try {
      const resp = await fetchMonitorConfigs({ page, page_size: pagination.pageSize })
      data.value = resp.data.results.map(r => ({
        ...r,
        cron_time: `${r.cron_hour}:${r.cron_minute}`,
        last_run: r.last_run ? r.last_run.replace('T',' ') : '—'
      }))
      pagination.total = resp.data.count
    } finally {
      loading.value = false
    }
  }

  defineExpose({ fetchConfigs, removeConfig, toggleConfig })

  function edit(record) {
    emit('edit', record)
  }

  async function removeConfig(id) {
    await deleteMonitorConfig(id)
    await fetchConfigs(pagination.current)
    emit('delete', id)
  }

  async function toggleConfig(id, enabled) {
    await updateMonitorConfig(id, { enabled })
    emit('toggle', { id, enabled })
  }

  function onPageChange(page) {
    fetchConfigs(page)
  }
</script>
