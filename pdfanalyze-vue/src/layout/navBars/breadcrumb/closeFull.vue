<template>
  <div v-if="isTagsViewCurrenFull" class="layout-navbars-close-full">
    <div class="layout-navbars-close-full-icon">
      <CloseCircleOutlined
        type="close-circle"
        :title="$t('message.tagsView.closeFullscreen')"
        class="icon-style"
        @click="onCloseFullscreen"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { storeToRefs } from 'pinia';
  import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';

  // 使用 Pinia store
  const stores = useTagsViewRoutes();
  const { isTagsViewCurrenFull } = storeToRefs(stores);

  // 关闭全屏的函数
  const onCloseFullscreen = () => {
    stores.setCurrenFullscreen(false);
  };
</script>

<style scoped lang="scss">
  .layout-navbars-close-full {
    position: fixed;
    z-index: 9999999999;
    right: -20px;
    top: -20px;
    .layout-navbars-close-full-icon {
      width: 60px;
      height: 60px;
      border-radius: 100%;
      cursor: pointer;
      background: rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      .icon-style {
        font-size: 40px;
        color: #333333;
        transition:
          transform 0.3s ease,
          color 0.3s ease; /* 增加transform过渡效果 */
      }
    }
    &:hover {
      .icon-style {
        transform: scale(1.2); /* 缩放到1.2倍 */
        color: var(--ant-primary-color);
      }
    }
  }
</style>
