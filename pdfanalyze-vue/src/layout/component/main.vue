<template>
  <PerfectScrollbar
    ref="scrollContainer"
    class="ps"
    :style="
      isFixedHeader
        ? { height: `calc(100% - ${setMainHeight})` }
        : { minHeight: `calc(100% - ${setMainHeight})` }
    "
    v-bind="$attrs"
  >
    <a-back-top :target="backTopTarget">
      <div class="ant-back-top-inner">UP</div>
    </a-back-top>
    <LayoutParentView />
    <LayoutFooter v-if="isFooter" />
  </PerfectScrollbar>
</template>

<script setup lang="ts" name="layoutMain">
  import { defineAsyncComponent, onMounted, computed, ref } from 'vue';
  import { useRoute } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import { NextLoading } from '/@/utils/loading';
  import { PerfectScrollbar } from 'vue3-perfect-scrollbar';
  import 'vue3-perfect-scrollbar/style.css';
  // 引入组件
  const LayoutParentView = defineAsyncComponent(
    () => import('/@/layout/routerView/parent.vue'),
  );
  const LayoutFooter = defineAsyncComponent(
    () => import('/@/layout/footer/index.vue'),
  );

  // 定义变量内容
  const layoutMainScrollbarRef = ref();
  const route = useRoute();
  const storesTagsViewRoutes = useTagsViewRoutes();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const { isTagsViewCurrenFull } = storeToRefs(storesTagsViewRoutes);

  // 设置 footer 显示/隐藏
  const isFooter = computed(() => {
    return themeConfig.value.isFooter && !route.meta.isIframe;
  });

  // 设置 header 固定
  const isFixedHeader = computed(() => {
    return themeConfig.value.isFixedHeader;
  });

  // 设置 Backtop 回到顶部
  const setBacktopClass = computed(() => {
    return themeConfig.value.isFixedHeader
      ? `.layout-backtop-header-fixed .ant-scrollbar__wrap`
      : `.layout-backtop .ant-scrollbar__wrap`;
  });

  // 设置主内容区的高度
  const setMainHeight = computed(() => {
    if (isTagsViewCurrenFull.value) return '0px';
    const { isTagsview, layout } = themeConfig.value;
    if (isTagsview && layout !== 'classic') return '85px';
    else return '51px';
  });

  // 定义 backTopTarget 函数
  const backTopTarget = (): HTMLElement | Window | Document => {
    return layoutMainScrollbarRef.value?.$el || document;
  };

  // 页面加载前
  onMounted(() => {
    NextLoading.done(600);
  });

  // 暴露变量
  defineExpose({
    layoutMainScrollbarRef,
  });
</script>
<style scoped>
  .ant-back-top-inner {
    height: 40px;
    width: 40px;
    line-height: 40px;
    border-radius: 4px;
    background-color: #1088e9;
    color: #fff;
    text-align: center;
    font-size: 20px;
  }
</style>
