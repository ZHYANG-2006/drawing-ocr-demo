<template>
  <div v-show="!isTagsViewCurrenFull" class="h100">
    <a-layout-sider
      class="layout-aside"
      :collapsed="themeConfig.isCollapse"
      :collapsed-width="64"
      :width="220"
      @breakpoint="onBreakpoint"
    >
      <Logo v-if="setShowLogo" />
      <div class="menu-container">
        <PerfectScrollbar
          ref="layoutAsideScrollbarRef"
          class="flex-auto"
          :options="{ suppressScrollX: true }"
          style="height: 100%"
          @mouseenter="onAsideEnterLeave(true)"
          @mouseleave="onAsideEnterLeave(false)"
        >
          <Vertical :menu-list="state.menuList" />
        </PerfectScrollbar>
      </div>
    </a-layout-sider>
  </div>
</template>

<script setup lang="ts" name="layoutAside">
  import {
    defineAsyncComponent,
    reactive,
    computed,
    watch,
    onBeforeMount,
    ref,
    onMounted,
  } from 'vue';
  import { storeToRefs } from 'pinia';
  import pinia from '/@/stores/index';
  import { useRoutesList } from '/@/stores/routesList';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
  import mittBus from '/@/utils/mitt';

  // 引入组件
  const Logo = defineAsyncComponent(() => import('/@/layout/logo/index.vue'));
  const Vertical = defineAsyncComponent(
    () => import('/@/layout/navMenu/vertical.vue'),
  );

  // 定义变量内容
  const layoutAsideScrollbarRef = ref();
  const stores = useRoutesList();
  const storesThemeConfig = useThemeConfig();
  const storesTagsViewRoutes = useTagsViewRoutes();
  const { routesList } = storeToRefs(stores);
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const { isTagsViewCurrenFull } = storeToRefs(storesTagsViewRoutes);
  const state = reactive<AsideState>({
    menuList: [],
    clientWidth: 0,
  });

  // 设置显示/隐藏 logo
  const setShowLogo = computed(() => {
    const { layout, isShowLogo } = themeConfig.value;
    return (
      (isShowLogo && layout === 'defaults') ||
      (isShowLogo && layout === 'columns')
    );
  });

  // 关闭移动端蒙版
  const closeLayoutAsideMobileMode = () => {
    const el = document.querySelector('.layout-aside-mobile-mode');
    el?.setAttribute('style', 'animation: error-img-two 0.3s');
    setTimeout(() => {
      el?.parentNode?.removeChild(el);
    }, 300);
    const clientWidth = document.body.clientWidth;
    if (clientWidth < 1000) themeConfig.value.isCollapse = false;
    document.body.setAttribute('class', '');
  };

  // 设置/过滤路由（非静态路由/是否显示在菜单中）
  const setFilterRoutes = () => {
    if (themeConfig.value.layout === 'columns') return false;
    state.menuList = filterRoutesFun(routesList.value);
  };

  // 路由过滤递归函数
  const filterRoutesFun = <T extends RouteItem>(arr: T[]): T[] => {
    return arr
      .filter((item: T) => !item.meta?.isHide)
      .map((item: T) => {
        item = Object.assign({}, item);
        if (item.children) item.children = filterRoutesFun(item.children);
        return item;
      });
  };

  // 设置菜单导航是否固定（移动端）
  const initMenuFixed = (clientWidth: number) => {
    state.clientWidth = clientWidth;
  };

  const onBreakpoint = (broken: boolean) => {
    themeConfig.value.isCollapse = broken;
  };

  // 鼠标移入、移出
  const onAsideEnterLeave = (bool: Boolean) => {
    const { layout } = themeConfig.value;
    if (layout !== 'columns') return false;
    if (!bool) mittBus.emit('restoreDefault');
    stores.setColumnsMenuHover(bool);
  };

  // 页面加载前
  onBeforeMount(() => {
    initMenuFixed(document.body.clientWidth);
    setFilterRoutes();
    mittBus.on('setSendColumnsChildren', (res: MittMenu) => {
      state.menuList = res.children;
    });
    mittBus.on('setSendClassicChildren', (res: MittMenu) => {
      const { layout, isClassicSplitMenu } = themeConfig.value;
      if (layout === 'classic' && isClassicSplitMenu) {
        state.menuList = res.children;
      }
    });
    mittBus.on('getBreadcrumbIndexSetFilterRoutes', () => {
      setFilterRoutes();
    });
    mittBus.on('layoutMobileResize', (res: LayoutMobileResize) => {
      initMenuFixed(res.clientWidth);
      closeLayoutAsideMobileMode();
    });
  });

  // 监听 themeConfig 配置文件的变化，更新菜单 scrollbar 的高度
  watch(themeConfig.value, (val) => {
    if (val.isShowLogoChange !== val.isShowLogo) {
      if (
        layoutAsideScrollbarRef.value &&
        layoutAsideScrollbarRef.value.$refs.ps
      )
        layoutAsideScrollbarRef.value.$refs.ps.update();
    }
  });

  // 监听 pinia 值的变化，动态赋值给菜单中
  watch(
    pinia.state,
    (val) => {
      const { layout, isClassicSplitMenu } = val.themeConfig.themeConfig;
      if (layout === 'classic' && isClassicSplitMenu) return false;
      setFilterRoutes();
    },
    {
      deep: true,
    },
  );

  onMounted(() => {
    console.log('themeConfig:', themeConfig.value.isCollapse);
  });
</script>
<style scoped>
  .layout-aside {
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%; /* 确保侧边栏高度占满父容器 */
    flex: 1;
  }

  .menu-container {
    position: relative;
    overflow: hidden;
    height: 100%;
    flex: 1;
  }

  .ps {
    max-height: 100%;
  }
</style>
