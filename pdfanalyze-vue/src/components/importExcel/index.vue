<template>
  <div style="display: inline-block">
    <a-button type="primary" @click="handleImport">
      <slot>导入</slot>
    </a-button>
    <a-modal
      v-model="uploadShow"
      :title="props.upload.title"
      width="400px"
      @close="closeDialog"
    >
      <div v-if="loading" style="text-align: center">
        <a-spin />
      </div>
      <a-upload
        ref="uploadRef"
        :max-count="1"
        accept=".xlsx, .xls"
        :headers="props.upload.headers"
        :action="props.upload.url"
        :disabled="isUploading"
        :on-progress="handleFileUploadProgress"
        :on-success="handleFileSuccess"
        :auto-upload="false"
        list-type="picture-card"
      >
        <div>
          <PlusOutlined />
          <p>点击上传</p>
        </div>
      </a-upload>
      <div>
        <a-button
          type="default"
          style="font-size: 14px; margin-top: 20px"
          @click="importTemplate"
        >
          下载导入模板
        </a-button>
        <a-button
          type="default"
          style="font-size: 14px; margin-top: 20px"
          @click="updateTemplate"
        >
          批量更新模板
        </a-button>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <a-button type="primary" :disabled="loading" @click="submitFileForm">
            确 定
          </a-button>
          <a-button :disabled="loading" @click="uploadShow = false">
            取 消
          </a-button>
        </div>
      </template>
    </a-modal>
  </div>
</template>

<script lang="ts" setup name="importExcel">
  import { ref, inject } from 'vue';
  import { request, downloadFile } from '/@/utils/service';
  import { getBaseURL } from '/@/utils/baseUrl';
  import { Session } from '/@/utils/storage';
  import { Modal, message } from 'ant-design-vue';
  const refreshView = inject<() => void>('refreshView');

  const props = defineProps({
    upload: {
      type: Object,
      default() {
        return {
          open: true,
          title: '',
          isUploading: false,
          updateSupport: 0,
          headers: { Authorization: 'JWT ' + Session.get('token') },
          url: getBaseURL() + 'api/system/file/',
        };
      },
    },
    api: {
      type: String,
      default() {
        return undefined;
      },
    },
  });

  const loading = ref(false);
  const uploadRef = ref();
  const uploadShow = ref(false);
  const isUploading = ref(false);

  const handleImport = () => {
    uploadShow.value = true;
  };

  const importTemplate = () => {
    downloadFile({
      url: props.api + 'import_data/',
      params: {},
      method: 'get',
    });
  };

  const updateTemplate = () => {
    downloadFile({
      url: props.api + 'update_template/',
      params: {},
      method: 'get',
    });
  };

  const handleFileUploadProgress = () => {
    isUploading.value = true;
  };

  const handleFileSuccess = (response: any) => {
    isUploading.value = false;
    loading.value = true;
    uploadRef.value?.clearFiles();
    return request({
      url: props.api + 'import_data/',
      method: 'post',
      data: {
        url: response.url,
      },
    })
      .then(() => {
        loading.value = false;
        Modal.success({
          title: '导入完成',
          content: '导入成功',
          onOk: () => {
            if (refreshView) {
              refreshView();
            } else {
              // 处理 refreshView 为 undefined 的情况，比如抛出错误或显示消息
              console.warn('refreshView is undefined');
            }
          },
        });
      })
      .catch(() => {
        loading.value = false;
        message.error('导入失败');
      });
  };

  const submitFileForm = () => {
    uploadRef.value?.submit();
  };

  const closeDialog = () => {
    uploadShow.value = false;
  };
</script>

<style scoped></style>
