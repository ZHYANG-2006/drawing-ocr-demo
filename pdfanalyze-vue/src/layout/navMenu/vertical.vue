<template>
  <a-menu
    mode="inline"
    :default-selected-keys="[state.defaultActive]"
    theme="dark"
    :collapsed="state.isCollapse"
    :open-keys="state.openKeys"
    :items="items"
    @click="handleMenuClick"
    @openChange="handleOpenChange"
  />
</template>

<script setup lang="ts">
  import {
    ref,
    defineAsyncComponent,
    reactive,
    computed,
    onMounted,
    watch,
    getCurrentInstance,
    h,
  } from 'vue';
  import type { VNode } from 'vue';
  import {
    useRoute,
    useRouter,
    onBeforeRouteUpdate,
    RouteLocationNormalizedGeneric,
  } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import other from '/@/utils/other';
  import { JSX } from 'vue/jsx-runtime';
  import { useI18n } from 'vue-i18n';

  interface MenuItem {
    key: string;
    label: string | { label: string; path: string; onClick: () => void };
    icon?: VNode | (() => VNode) | undefined;
    children?: MenuItem[];
    onClick?: () => void; // 添加 onClick 事件处理函数
  }
  // 定义父组件传递的属性
  const props = defineProps({
    menuList: {
      type: Array,
      default: () => [],
    },
  });

  // 定义状态和引用
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const route = useRoute();
  const router = useRouter();
  const items = ref<MenuItem[]>([]);
  const state = reactive({
    defaultActive: route.meta.isDynamic ? route.meta.isDynamicPath : route.path,
    isCollapse: themeConfig.value.isCollapse,
    openKeys: [], // 存储展开的菜单项
  });

  // 定义菜单转换函数
  const { appContext } = getCurrentInstance()!;
  const Icons = appContext.config.globalProperties.$icons;
  const { t } = useI18n();
  function transformMenuData(data: any[]): MenuItem[] {
    return data.map((item) => {
      const IconComponent = Icons[item.meta?.icon || item.icon];
      const menuItem: MenuItem = {
        key: item.path,
        label: t(item.meta?.title) || item.title,
        icon: IconComponent ? h(IconComponent) : undefined,
      };

      // 如果没有子菜单项，才设置 onClick
      if (!item.children || item.children.length === 0) {
        console.log('path', item);
        menuItem.onClick =
          item.meta?.isLink && !item.meta?.isIframe
            ? () => onALinkClick(item)
            : () => router.push(item.path);
      }

      // 递归处理子菜单
      if (item.children && item.children.length > 0) {
        menuItem.children = transformMenuData(item.children);
      }

      return menuItem;
    });
  }

  const handleMenuClick = (info: any) => {
    const keyStr = info.key.toString();
    const menuItem = items.value.find((item) => item.key === keyStr);

    // 仅当 menuItem 存在且不含子项时触发 onClick
    if (menuItem && menuItem.onClick && !menuItem.children) {
      menuItem.onClick();
    }
  };

  // 动态计算菜单项
  const menuLists = computed(() => {
    return props.menuList;
  });

  // 获取主题配置
  const getThemeConfig = computed(() => themeConfig.value);

  // 动态控制菜单项展开与收起
  const handleOpenChange = (keys: never[]) => {
    state.openKeys = keys;
  };

  // 父菜单高亮
  const setParentHighlight = (currentRoute: RouteLocationNormalizedGeneric) => {
    const { path, meta } = currentRoute;
    const pathSplit = meta?.isDynamic
      ? meta.isDynamicPath!.split('/')
      : path!.split('/');
    return pathSplit.length >= 4 && meta?.isHide
      ? pathSplit.splice(0, 3).join('/')
      : path;
  };

  // 外部链接点击事件
  const onALinkClick = (val: RouteItem<any>) => {
    other.handleOpenLink(val);
  };

  // 页面加载时设置默认选中和展开项
  onMounted(() => {
    items.value = transformMenuData(props.menuList);
    console.log('items');
    console.log(items.value);
    state.defaultActive = setParentHighlight(route);
    if (state.isCollapse) state.openKeys = [];
  });

  // 路由更新时重新设置菜单项
  onBeforeRouteUpdate((to) => {
    state.defaultActive = setParentHighlight(to);
    if (document.body.clientWidth < 1000) themeConfig.value.isCollapse = false;
  });

  // 动态监听菜单的展开和收起状态
  watch(
    () => themeConfig.value,
    (newThemeConfig) => {
      state.isCollapse = newThemeConfig.isCollapse;
      if (state.isCollapse) state.openKeys = [];
    },
    { immediate: true, deep: true },
  );
</script>

<style scoped>
  /* 自定义样式可以根据 Ant Design Vue 提供的样式类进行调整 */
</style>
