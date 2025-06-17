<template>
  <div>
    <a-modal
      ref="iqaFormModal"
      :title="'上传 PDF 文件'"
      :open="visible"
      :confirm-loading="submitLoading"
      @cancel="close"
      @ok="confirm"
    >
      <a-form :model="formData" layout="vertical">
        <a-row>
          <!-- 上传 PDF -->
          <a-col :span="24">
            <a-form-item label="上传 PDF" required>
              <a-upload
                directory
                :before-upload="handleBeforeUpload"
                :file-list="formData.fileList"
                :show-upload-list="false"
                list-type="text"
              >
                <a-button icon="upload">点击上传目录</a-button>
              </a-upload>
              <div v-if="formData.fileList.length > 0">
                已选文件数：{{ formData.fileList.length }}
              </div>
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
  import { uploadIQA } from '/@/views/pdfanalyze/iqa/api/iqadir/iqaDir.js';

  // 声明子组件支持的事件
  const emit = defineEmits(['ok', 'cancel', 'refresh']);

  // 定义响应式数据
  const visible = ref(false);
  const submitLoading = ref(false);
  const formData = reactive({
    file_path: '',
    folder_name: '',
    fileList: [], // 上传的文件列表
  });

  // 处理上传文件
  const handleBeforeUpload = (file, fileList) => {
    // 输出该文件在所选文件夹中的相对路径
    console.log('webkitRelativePath:', file.webkitRelativePath);

    // 如果只需要获取最上层文件夹名字
    if (file.webkitRelativePath) {
      const topFolderName = file.webkitRelativePath.split('/')[0];
      formData.folder_name = topFolderName;

      // 你可以把这个名称存到组件的 data 或 Vuex 中，或者附加到 file 对象
      // file.folderName = topFolderName;
    }
    if (file.type !== 'application/pdf') {
      message.error('仅支持上传 PDF 文件');
      return false;
    }
    formData.fileList = fileList;
    return false; // 阻止默认上传行为
  };

  const resetFormData = () => {
    formData.folder_name = '';
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
    formDataToSend.append('file_path', formData.file_path);
    formDataToSend.append('folder_name', formData.folder_name);
    formData.fileList.forEach((item) => {
      if (item) {
        formDataToSend.append('file', item);
      }
    });

    submitLoading.value = true;

    try {
      const response = await uploadIQA(formDataToSend);
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
