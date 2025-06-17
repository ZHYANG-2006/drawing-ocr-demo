<template>
  <div class="user-info-head" @click="editCropper()">
    <a-avatar :size="100" :src="options.img" />
    <a-modal
      v-model="dialogVisible"
      :title="title"
      width="600px"
      @open="modalOpened"
      @close="closeDialog"
    >
      <a-row>
        <a-col class="flex justify-center">
          <vue-cropper
            v-if="visible"
            ref="cropper"
            :img="options.img"
            :info="true"
            :auto-crop="options.autoCrop"
            :auto-crop-width="options.autoCropWidth"
            :auto-crop-height="options.autoCropHeight"
            :fixed-box="options.fixedBox"
            :output-type="options.outputType"
            :center-box="true"
            class="cropper"
            @realTime="realTime"
          />
        </a-col>
      </a-row>
      <br />
      <a-row class="flex justify-center">
        <a-col :lg="2" :md="2">
          <a-upload
            custom-request="requestUpload"
            :show-upload-list="false"
            :before-upload="beforeUpload"
          >
            <a-button type="primary">
              选择
              <PlusOutlined />
            </a-button>
          </a-upload>
        </a-col>
        <a-col :lg="{ span: 1, offset: 2 }" :md="2">
          <a-button icon="RefreshLeftOutlined" @click="rotateLeft()" />
        </a-col>
        <a-col :lg="{ span: 1, offset: 2 }" :md="2">
          <a-button icon="RefreshRightOutlined" @click="rotateRight()" />
        </a-col>
        <a-col :lg="{ span: 2, offset: 2 }" :md="2">
          <a-button type="primary" @click="uploadImg">更新头像</a-button>
        </a-col>
      </a-row>
    </a-modal>
  </div>
</template>

<script setup>
  import { VueCropper } from 'vue-cropper';
  import { useUserInfo } from '/@/stores/userInfo';
  import {
    getCurrentInstance,
    nextTick,
    reactive,
    ref,
    computed,
    defineExpose,
  } from 'vue';
  import { base64ToFile } from '/@/utils/tools';
  const userStore = useUserInfo();
  const { proxy } = getCurrentInstance();

  const visible = ref(false);
  const title = ref('修改头像');
  const emit = defineEmits(['uploadImg']);
  const props = defineProps({
    modelValue: {
      type: Boolean,
      default: false,
      required: true,
    },
  });
  const dialogVisible = computed({
    get() {
      return props.modelValue;
    },
    set(newVal) {
      emit('update:modelValue', newVal);
    },
  });

  // 图片裁剪数据
  const options = reactive({
    img: userStore.userInfos.avatar, // 裁剪图片的地址
    fileName: '',
    autoCrop: true, // 是否默认生成截图框
    autoCropWidth: 200, // 默认生成截图框宽度
    autoCropHeight: 200, // 默认生成截图框高度
    fixedBox: true, // 固定截图框大小 不允许改变
    outputType: 'png', // 默认生成截图为PNG格式
  });

  /** 编辑头像 */
  function editCropper() {
    dialogVisible.value = true;
  }
  /** 打开弹出层结束时的回调 */
  function modalOpened() {
    nextTick(() => {
      visible.value = true;
    });
  }
  /** 覆盖默认上传行为 */
  function requestUpload() {}
  /** 向左旋转 */
  function rotateLeft() {
    proxy.$refs.cropper.rotateLeft();
  }
  /** 向右旋转 */
  function rotateRight() {
    proxy.$refs.cropper.rotateRight();
  }
  /** 图片缩放 */
  function changeScale(num) {
    num = num || 1;
    proxy.$refs.cropper.changeScale(num);
  }
  /** 上传预处理 */
  function beforeUpload(file) {
    if (file.type.indexOf('image/') == -1) {
      proxy.$message.error(
        '文件格式错误，请上传图片类型,如：JPG，PNG后缀的文件。',
      );
    } else {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        options.img = reader.result;
        options.fileName = file.name;
      };
    }
  }
  /** 上传图片 */
  function uploadImg() {
    // 获取截图的 base64 数据
    proxy.$refs.cropper.getCropData((data) => {
      const img = new Image();
      img.src = data;
      img.onload = async () => {
        const _data = compress(img);
        const imgFile = base64ToFile(_data, options.fileName);
        emit('uploadImg', imgFile);
      };
    });
  }
  // 压缩图片
  function compress(img) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const width = img.width;
    const height = img.height;
    canvas.width = width;
    canvas.height = height;
    // 铺底色
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, width, height);
    // 进行压缩
    const ndata = canvas.toDataURL('image/jpeg', 0.8);
    return ndata;
  }

  /** 关闭窗口 */
  function closeDialog() {
    options.visible = false;
    options.img = userStore.userInfos.avatar;
  }

  const updateAvatar = (img) => {
    options.img = img;
  };

  defineExpose({
    updateAvatar,
  });
</script>

<style lang="scss" scoped>
  .user-info-head {
    position: relative;
    display: inline-block;
    height: 120px;
  }

  .user-info-head:hover:after {
    content: '修改头像';
    position: absolute;
    text-align: center;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    color: #000000;
    font-size: 20px;
    font-style: normal;
    cursor: pointer;
    line-height: 110px;
  }
  .cropper {
    height: 400px;
    width: 400px;
  }
</style>
