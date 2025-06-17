<template>
  <a-layout class="layout-container">
    <LayoutAside />
    <a-layout class="layout-container-view h100">
      <a-layout-content ref="layoutScrollbarRef" class="layout-backtop">
        <LayoutHeader />
        <LayoutMain ref="layoutMainRef" />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts" name="layoutDefaults">
  import { defineAsyncComponent, watch, onMounted, ref } from 'vue';
  import { useRoute } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import { NextLoading } from '/@/utils/loading';

  // 引入组件
  const LayoutAside = defineAsyncComponent(
    () => import('/@/layout/component/aside.vue'),
  );
  const LayoutHeader = defineAsyncComponent(
    () => import('/@/layout/component/header.vue'),
  );
  const LayoutMain = defineAsyncComponent(
    () => import('/@/layout/component/main.vue'),
  );

  // 定义变量内容
  const layoutScrollbarRef = ref();
  const layoutMainRef = ref();
  const route = useRoute();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);

  // 页面加载时
  onMounted(() => {
    NextLoading.done(600);
  });

  // 监听路由的变化，切换界面时，滚动条置顶
  watch(
    () => route.path,
    () => {
      layoutScrollbarRef.value.scrollTop = 0; // 确保滚动条置顶
    },
  );

  // 监听 themeConfig 配置文件的变化，更新菜单的高度
  watch(
    themeConfig,
    () => {
      // 更新菜单相关样式，如果有必要
    },
    {
      deep: true,
    },
  );
</script>
