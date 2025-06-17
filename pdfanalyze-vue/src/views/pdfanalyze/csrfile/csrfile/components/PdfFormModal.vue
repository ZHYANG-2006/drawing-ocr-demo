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
          <!-- 制程 -->
          <a-col :span="12">
            <a-form-item label="制程" required>
              <a-select v-model:value="formData.process" placeholder="请选择">
                <a-select-option value="FPCA">FPCA</a-select-option>
                <a-select-option value="FPC">FPC</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <a-col :span="12">
            <a-form-item label="客户" required>
              <a-select v-model:value="formData.customer" placeholder="请选择">
                <a-select-option value="Jade">Jade</a-select-option>
                <a-select-option value="Others">Others</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item
              label="客户文件名称"
              :required=true
            >
              <a-input
                v-model:value="formData.customer_file_name"
                placeholder="请输入客户文件名称"
              />
            </a-form-item>
          </a-col>

          <a-col :span="12">
            <a-form-item
              label="客户文件编号"
              :required=true
            >
              <a-input
                v-model:value="formData.customer_file_code"
                placeholder="请输入客户文件编号"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item
              label="客户文件版本"
              :required=true
            >
              <a-input
                v-model:value="formData.customer_file_version"
                placeholder="请输入客户文件版本"
              />
            </a-form-item>
          </a-col>

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
  import { uploadPDF } from '/@/views/pdfanalyze/csrfile/api/csrfile/pdfFile.js';

  // 声明子组件支持的事件
  const emit = defineEmits(['ok', 'cancel', 'refresh']);

  // 定义响应式数据
  const visible = ref(false);
  const submitLoading = ref(false);
  const formData = reactive({
    process: 'FPCA',
    customer: 'Jade',
    customer_file_name: '',
    customer_file_code: '',
    customer_file_version: '',
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
    formData.process = 'FPCA';
    formData.customer = 'Jade';
    formData.customer_file_name = '';
    formData.customer_file_code = '';
    formData.customer_file_version = '';
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
    formDataToSend.append('process', formData.process);
    formDataToSend.append('customer', formData.customer);
    formDataToSend.append('customer_file_name', formData.customer_file_name);
    formDataToSend.append('customer_file_code', formData.customer_file_code);
    formDataToSend.append('customer_file_version', formData.customer_file_version);
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
