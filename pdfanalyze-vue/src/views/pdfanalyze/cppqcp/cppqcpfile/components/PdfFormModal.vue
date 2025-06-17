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

          <!-- 文件类型 -->
          <a-col :span="12">
            <a-form-item label="文件类型" required>
              <a-select v-model:value="formData.file_type" placeholder="请选择">
                <a-select-option value="QCP">QCP</a-select-option>
                <a-select-option value="CPP">CPP</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <!-- 客户 -->
          <a-col :span="12">
            <a-form-item label="客户" required>
              <a-select v-model:value="formData.customer" placeholder="请选择">
                <a-select-option value="Jade">Jade</a-select-option>
                <a-select-option value="Others">Others</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <!-- 是否通用 -->
          <a-col :span="12">
            <a-form-item label="是否通用" required>
              <a-select
                v-model:value="formData.is_universal"
                placeholder="请选择"
              >
                <a-select-option value="Y">Y</a-select-option>
                <a-select-option value="N">N</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <!-- 料号 -->
          <a-col :span="12">
            <a-form-item
              label="料号"
              :required="formData.is_universal === 'N'"
              :validate-status="materialNoStatus"
              :help="materialNoMessage"
            >
              <a-input
                v-model:value="formData.material_number"
                placeholder="请输入5位数字料号"
                @blur="validateMaterialNo"
              />
            </a-form-item>
          </a-col>

          <!-- LOB -->
          <a-col :span="12">
            <a-form-item label="LOB" required>
              <a-select
                v-model:value="formData.lob"
                mode="multiple"
                placeholder="请选择"
              >
                <a-select-option value="Phone">Phone</a-select-option>
                <a-select-option value="Watch">Watch</a-select-option>
                <a-select-option value="MAC">MAC</a-select-option>
                <a-select-option value="Pad">Pad</a-select-option>
                <a-select-option value="ACC">ACC</a-select-option>
                <a-select-option value="Car">Car</a-select-option>
                <a-select-option value="Other">Other</a-select-option>
                <a-select-option value="ALL">ALL</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <!-- PFMEA类别 -->
          <a-col :span="12">
            <a-form-item label="PFMEA类别" required>
              <a-select
                v-model:value="formData.pfmea_type"
                :disabled="formData.customer === 'Jade'"
                placeholder="请选择"
              >
                <a-select-option value="FMEA4">FMEA4</a-select-option>
                <a-select-option value="FMEA5">FMEA5</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <!-- SITE -->
          <a-col :span="12">
            <a-form-item label="SITE" required>
              <a-select v-model:value="formData.branch" placeholder="请选择">
                <a-select-option value="SZ">苏州SZ</a-select-option>
                <a-select-option value="YC">盐城YC</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

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
          <a-col :span="12">
            <a-form-item
              label="TYPE"
            >
              <a-input
                v-model:value="formData.type"
                placeholder="请输入type"
              />
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
  import { uploadPDF } from '/@/views/pdfanalyze/cppqcp/api/cppqcpfile/pdfFile.js';

  // 声明子组件支持的事件
  const emit = defineEmits(['ok', 'cancel', 'refresh']);

  // 定义响应式数据
  const visible = ref(false);
  const submitLoading = ref(false);
  const formData = reactive({
    process: 'FPCA',
    file_type: null,
    customer: 'Jade',
    is_universal: 'N',
    material_number: '',
    lob: [],
    pfmea_type: '',
    branch: '',
    fileList: [], // 上传的文件列表
    type: '',
  });

  // 监听客户动态调整 PFMEA 类别
  watch(
    () => formData.customer,
    (newVal) => {
      if (newVal === 'Jade') {
        formData.pfmea_type = 'FMEA4';
      } else {
        formData.pfmea_type = '';
      }
    },
    { immediate: true },
  );

  // 校验料号
  const materialNoStatus = ref('');
  const materialNoMessage = ref('');
  const validateMaterialNo = () => {
    if (formData.is_universal === 'N') {
      // 非通用：料号必须输入且为5位数字
      if (!/^\d{5}$/.test(formData.material_number)) {
        materialNoStatus.value = 'error';
        materialNoMessage.value = '料号必须是5位数字';
        return;
      }
    } else if (formData.is_universal === 'Y') {
      // 通用：料号可以为空，但输入时必须为5位数字
      if (
        formData.material_number &&
        !/^\d{5}$/.test(formData.material_number)
      ) {
        materialNoStatus.value = 'error';
        materialNoMessage.value = '料号必须是5位数字';
        return;
      }
    }
    // 校验通过
    materialNoStatus.value = '';
    materialNoMessage.value = '';
  };

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
    formData.file_type = null;
    formData.customer = 'Jade';
    formData.is_universal = 'N';
    formData.material_number = '';
    formData.lob = [];
    formData.type = '';
    formData.pfmea_type = 'FMEA4';
    formData.branch = '';
    formData.fileList = [];
  };

  // 打开模态框
  const openModal = () => {
    resetFormData();
    visible.value = true;
  };

  // 确认提交
  const confirm = async () => {
    validateMaterialNo();
    if (materialNoStatus.value === 'error') {
      return;
    }
    if (!formData.fileList.length) {
      message.error('请上传 PDF 文件');
      return;
    }
    // 创建 FormData 对象
    const formDataToSend = new FormData();
    formDataToSend.append('process', formData.process);
    formDataToSend.append('file_type', formData.file_type);
    formDataToSend.append('customer', formData.customer);
    formDataToSend.append('is_universal', formData.is_universal);
    formDataToSend.append('material_number', formData.material_number || '');
    formDataToSend.append('lob', formData.lob.join(','));
    formDataToSend.append('pfmea_type', formData.pfmea_type || '');
    formDataToSend.append('branch', formData.branch || '');
    formDataToSend.append('type', formData.type);
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
