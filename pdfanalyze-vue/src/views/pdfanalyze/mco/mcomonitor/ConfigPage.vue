<template>
  <div class="config-page">
    <a-page-header title="目录扫描任务配置" />
    <div class="toolbar">
      <a-button type="primary" @click="onAdd">
        新增扫描任务
      </a-button>
    </div>

    <ConfigTable
      ref="tableRef"
      @edit="onEdit"
      @delete="onDelete"
      @toggle="onToggle"
    />

    <ConfigFormModal
      ref="modalRef"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { message } from 'ant-design-vue'
  import ConfigTable from './components/ConfigTable.vue'
  import ConfigFormModal from './components/ConfigFormModal.vue'

  const tableRef = ref(null)
  const modalRef = ref(null)

  // 点击“新增”
  function onAdd() {
    modalRef.value.open()   // 打开弹窗，无初始数据
  }

  // 点击“编辑”时，table 通过 event 携带整个 record
  function onEdit(record) {
    modalRef.value.open(record)
  }

  // 删除回调
  async function onDelete(id) {
    try {
      await tableRef.value.removeConfig(id)
      message.success('删除成功')
    } catch {
      message.error('删除失败')
    }
  }

  // 切换启用/禁用
  async function onToggle({ id, enabled }) {
    try {
      await tableRef.value.toggleConfig(id, enabled)
      message.success('更新成功')
    } catch {
      message.error('更新失败')
    }
  }

  // 弹窗保存成功后，刷新 table
  function onSaved() {
    tableRef.value.fetchConfigs()
    message.success('保存成功')
  }
</script>

<style scoped>
  .config-page { padding: 24px; background: #fff; border-radius: 6px; }
  .toolbar { margin-bottom: 16px; }
</style>
