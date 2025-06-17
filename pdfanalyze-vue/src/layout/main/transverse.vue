<template>
  <a-layout class="layout-container flex-center layout-backtop">
    <LayoutHeader />
    <a-layout-content ref="layoutMainRef" class="layout-main">
      <LayoutMain />
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts" name="layoutTransverse">
  import { defineAsyncComponent, ref, watch, nextTick, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';

  // 引入组件
  const LayoutHeader = defineAsyncComponent(
    () => import('/@/layout/component/header.vue'),
  );
  const LayoutMain = defineAsyncComponent(
    () => import('/@/layout/component/main.vue'),
  );

  // 定义变量内容
  const layoutMainRef = ref();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const route = useRoute();

  // 更新子组件的滚动条
  const updateScrollbar = () => {
    if (layoutMainRef.value) {
      layoutMainRef.value.layoutMainScrollbarRef?.update();
    }
  };

  // 初始化滚动条高度
  const initScrollBarHeight = () => {
    nextTick(() => {
      setTimeout(() => {
        updateScrollbar();
        layoutMainRef.value!.layoutMainScrollbarRef.wrapRef.scrollTop = 0;
      }, 500);
    });
  };

  // 页面加载时
  onMounted(() => {
    initScrollBarHeight();
  });

  // 监听路由变化，切换界面时，滚动条置顶
  watch(
    () => route.path,
    () => {
      initScrollBarHeight();
    },
  );

  // 监听 themeConfig 的变化，更新菜单的高度
  watch(
    themeConfig,
    () => {
      updateScrollbar();
    },
    {
      deep: true,
    },
  );
</script>

<style scoped>
  .layout-container {
    /* 根据需要添加样式 */
  }

  .layout-main {
    /* 根据需要添加样式 */
  }

  .flex-center {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
  }
</style>
