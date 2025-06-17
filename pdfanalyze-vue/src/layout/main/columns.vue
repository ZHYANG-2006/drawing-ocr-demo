<template>
  <a-layout class="layout-container">
    <ColumnsAside />
    <a-layout class="layout-columns-warp layout-container-view h100">
      <LayoutAside />
      <a-layout-content ref="layoutScrollbarRef" class="layout-backtop">
        <LayoutHeader />
        <LayoutMain ref="layoutMainRef" />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts" name="layoutColumns">
  import { defineAsyncComponent, watch, onMounted, nextTick, ref } from 'vue';
  import { useRoute } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';

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
  const ColumnsAside = defineAsyncComponent(
    () => import('/@/layout/component/columnsAside.vue'),
  );

  // 定义变量内容
  const layoutScrollbarRef = ref();
  const layoutMainRef = ref();
  const route = useRoute();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);

  // 重置滚动条高度
  const updateScrollbar = () => {
    // 更新父级 scrollbar
    layoutScrollbarRef.value.scrollTop = 0; // Ant Design Vue 不提供专用的 scrollbar 更新方法
    layoutMainRef.value!.layoutMainScrollbarRef.scrollTop = 0; // 需要确保 layoutMainScrollbarRef 定义正确
  };

  // 页面加载时
  onMounted(() => {
    updateScrollbar();
  });

  // 监听路由的变化，切换界面时，滚动条置顶
  watch(
    () => route.path,
    () => {
      updateScrollbar();
    },
  );

  // 监听 themeConfig 配置文件的变化，更新菜单 el-scrollbar 的高度
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
