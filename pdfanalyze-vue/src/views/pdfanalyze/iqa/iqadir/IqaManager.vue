<template>
  <div>
    <a-button style="margin: 10px" type="primary" @click="showModal">
      上传 PDF
    </a-button>
    <IqaTable ref="iqaTable" />
    <IqaFormModal ref="iqaFormModal" @refresh="refreshTable" />
  </div>
</template>

<script setup>
  import { ref } from 'vue';
  import { message } from 'ant-design-vue';
  import IqaFormModal from './components/IqaFormModal.vue';
  import IqaTable from './components/IqaTable.vue';
  // import { BtnPermissionStore } from '/@/plugin/permission/store.permission.js'; // 根据实际路径调整

  // 引用模态框组件
  const iqaFormModal = ref(null);
  const iqaTable = ref(null);

  // 打开子组件的模态框
  const showModal = () => {
    iqaFormModal.value.openModal();
  };

  // 刷新表格数据
  const refreshTable = async () => {
    try {
      iqaTable.value.fetchIqaDirs({});
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
