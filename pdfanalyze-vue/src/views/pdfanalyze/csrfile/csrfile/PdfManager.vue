<template>
  <div>
    <a-button style="margin: 10px" type="primary" @click="showModal">
      上传 PDF
    </a-button>
    <PdfTable ref="pdfTable" :loading="loading" @update:loading="loading = $event" />
    <PdfFormModal ref="pdfFormModal" @refresh="refreshTable" />
  </div>
</template>

<script setup>
  import { ref } from 'vue';
  import { message } from 'ant-design-vue';
  import PdfFormModal from './components/PdfFormModal.vue';
  import PdfTable from './components/PdfTable.vue';
  // import { BtnPermissionStore } from '/@/plugin/permission/store.permission.js'; // 根据实际路径调整

  // 引用模态框组件
  const pdfFormModal = ref(null);
  const pdfTable = ref(null);
  const loading = ref(false);  // 添加 loading 状态

  // 打开子组件的模态框
  const showModal = () => {
    pdfFormModal.value.openModal();
  };

  // 刷新表格数据
  const refreshTable = async () => {
    try {
      pdfTable.value.fetchPdfFiles({});
    } catch (error) {
      console.error('表格刷新失败', error);
    } finally {
      loading.value = false;
    }
  };

  // 处理子组件的 ok 事件
  const handleOk = () => {
    message.success('操作完成，刷新数据');
    // 刷新表格数据逻辑
  };
</script>
