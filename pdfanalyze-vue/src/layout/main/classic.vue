<template>
  <a-layout class="layout-container flex-center">
    <LayoutHeader />
    <a-layout class="layout-main-height-50">
      <LayoutAside />
      <div class="flex-center layout-backtop">
        <LayoutTagsView v-if="isTagsview" />
        <LayoutMain ref="layoutMainRef" />
      </div>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts" name="layoutClassic">
  import {
    defineAsyncComponent,
    computed,
    ref,
    watch,
    nextTick,
    onMounted,
  } from 'vue';
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
  const LayoutTagsView = defineAsyncComponent(
    () => import('/@/layout/navBars/tagsView/tagsView.vue'),
  );

  // 定义变量内容
  const layoutMainRef = ref();
  const route = useRoute();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);

  // 判断是否显示 tagsview
  const isTagsview = computed(() => {
    return themeConfig.value.isTagsview;
  });

  // 重置滚动条高度，更新子级 scrollbar
  const updateScrollbar = () => {
    layoutMainRef.value?.layoutMainScrollbarRef.update();
  };

  // 重置滚动条高度，由于组件是异步引入的
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

  // 监听路由的变化，切换界面时，滚动条置顶
  watch(
    () => route.path,
    () => {
      initScrollBarHeight();
    },
  );

  // 监听 themeConfig 配置文件的变化，更新菜单 scrollbar 的高度
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
    /* 根据您的设计需求进行样式调整 */
  }
  .layout-main-height-50 {
    /* 根据您的设计需求进行样式调整 */
  }
</style>
