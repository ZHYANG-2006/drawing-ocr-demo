<template>
  <div>
    <a-modal
      ref="pdfFormModal"
      :title="'上传 PDF 文件'"
      :open="visible"
      :confirm-loading="submitLoading"
      @cancel="close"
      @ok="confirm"
    >
      <a-form :model="formData" layout="vertical">
        <a-row :gutter="16">
          <!-- 上传 PDF -->
          <a-col :span="12">
            <a-form-item label="上传 PDF" required>
              <a-upload
                :before-upload="handleBeforeUpload"
                :file-list="formData.fileList"
                accept=".pdf"
                list-type="text"
                :maxCount="1"
              >
                <a-button icon="upload">点击上传</a-button>
              </a-upload>
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
  import { ref, reactive, watch } from 'vue';
  import { message } from 'ant-design-vue';
  import { uploadPDF } from '/@/views/pdfanalyze/stack/api/stackfile/pdfFile.js';

  // 声明子组件支持的事件
  const emit = defineEmits(['ok', 'cancel', 'refresh']);

  // 定义响应式数据
  const visible = ref(false);
  const submitLoading = ref(false);
  const formData = reactive({
    fileList: [], // 上传的文件列表
  });

  // 处理上传文件
  const handleBeforeUpload = (file) => {
    if (file.type !== 'application/pdf') {
      message.error('仅支持上传 PDF 文件');
      return false;
    }
    formData.fileList = [file];
    return false; // 阻止默认上传行为
  };

  const resetFormData = () => {
    formData.fileList = [];
  };

  // 打开模态框
  const openModal = () => {
    resetFormData();
    visible.value = true;
  };

  // 确认提交
  const confirm = async () => {
    if (!formData.fileList.length) {
      message.error('请上传 PDF 文件');
      return;
    }
    // 创建 FormData 对象
    const formDataToSend = new FormData();
    formDataToSend.append('file', formData.fileList[0]);

    submitLoading.value = true;

    try {
      const response = await uploadPDF(formDataToSend);
      if (response.code === 2000) {
        message.success('上传成功');
        close();
      } else {
        message.error(response.msg);
      }
    } catch (error) {
    } finally {
      submitLoading.value = false;
    }
  };

  // 关闭模态框
  const close = () => {
    visible.value = false;
    emit('refresh'); // 通知父组件刷新表格
  };

  // 暴露给父组件的方法
  defineExpose({
    openModal,
  });
</script>
