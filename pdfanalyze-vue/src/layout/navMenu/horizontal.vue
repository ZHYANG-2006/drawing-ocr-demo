<template>
  <div class="ant-menu-horizontal-wrap">
    <a-scroll ref="elMenuHorizontalScrollRef" @wheel="onElMenuHorizontalScroll">
      <a-menu
        router
        :default-selected-keys="[state.defaultActive]"
        :mode="'horizontal'"
        :theme="'light'"
      >
        <template v-for="val in menuLists" :key="val.path">
          <a-sub-menu
            v-if="val.children && val.children.length > 0"
            :key="val.path"
          >
            <template #title>
              <SvgIcon :name="val.meta.icon" />
              <span>{{ $t(val.meta.title) }}</span>
            </template>
            <SubItem :chil="val.children" />
          </a-sub-menu>
          <a-menu-item :index="val.path">
            <template
              v-if="!val.meta.isLink || (val.meta.isLink && val.meta.isIframe)"
            >
              <SvgIcon :name="val.meta.icon" />
              {{ $t(val.meta.title) }}
            </template>
            <template v-else>
              <a class="w100" @click.prevent="onALinkClick(val)">
                <SvgIcon :name="val.meta.icon" />
                {{ $t(val.meta.title) }}
              </a>
            </template>
          </a-menu-item>
        </template>
      </a-menu>
    </a-scroll>
  </div>
</template>

<script setup lang="ts" name="navMenuHorizontal">
  import {
    defineAsyncComponent,
    reactive,
    computed,
    onMounted,
    nextTick,
    onBeforeMount,
    ref,
  } from 'vue';
  import { useRoute, onBeforeRouteUpdate, RouteRecordRaw } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useRoutesList } from '/@/stores/routesList';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import other from '/@/utils/other';
  import mittBus from '/@/utils/mitt';

  // 引入组件
  const SubItem = defineAsyncComponent(
    () => import('/@/layout/navMenu/subItem.vue'),
  );

  // 定义父组件传过来的值
  const props = defineProps({
    // 菜单列表
    menuList: {
      type: Array<RouteRecordRaw>,
      default: () => [],
    },
  });

  // 定义变量内容
  const elMenuHorizontalScrollRef = ref();
  const stores = useRoutesList();
  const storesThemeConfig = useThemeConfig();
  const { routesList } = storeToRefs(stores);
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const route = useRoute();
  const state = reactive({
    defaultActive: '' as string | undefined,
  });

  // 获取父级菜单数据
  const menuLists = computed(() => {
    return <RouteItems>props.menuList;
  });

  // 设置横向滚动条可以鼠标滚轮滚动
  const onElMenuHorizontalScroll = (e: WheelEventType) => {
    const eventDelta = e.wheelDelta || -e.deltaY * 40;
    elMenuHorizontalScrollRef.value.$refs.wrapRef.scrollLeft += eventDelta / 4;
  };

  // 初始化数据，页面刷新时，滚动条滚动到对应位置
  const initElMenuOffsetLeft = () => {
    nextTick(() => {
      const els = <HTMLElement>(
        document.querySelector(
          '.ant-menu.ant-menu-horizontal .ant-menu-item.ant-menu-item-selected',
        )
      );
      if (!els) return false;
      elMenuHorizontalScrollRef.value.$refs.wrapRef.scrollLeft = els.offsetLeft;
    });
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

  // 传送当前子级数据到菜单中
  const setSendClassicChildren = (path: string) => {
    const currentPathSplit = path.split('/');
    const currentData: MittMenu = { children: [] };
    filterRoutesFun(routesList.value).forEach((v, k) => {
      if (v.path === `/${currentPathSplit[1]}`) {
        v['k'] = k;
        currentData['item'] = { ...v };
        currentData['children'] = [{ ...v }];
        if (v.children) currentData['children'] = v.children;
      }
    });
    return currentData;
  };

  // 设置页面当前路由高亮
  const setCurrentRouterHighlight = (currentRoute: RouteToFrom) => {
    const { path, meta } = currentRoute;
    if (themeConfig.value.layout === 'classic') {
      state.defaultActive = `/${path?.split('/')[1]}`;
    } else {
      const pathSplit = meta?.isDynamic
        ? meta.isDynamicPath!.split('/')
        : path!.split('/');
      if (pathSplit.length >= 4 && meta?.isHide)
        state.defaultActive = pathSplit.splice(0, 3).join('/');
      else state.defaultActive = path;
    }
  };

  // 打开外部链接
  const onALinkClick = (val: RouteItem) => {
    other.handleOpenLink(val);
  };

  // 页面加载前
  onBeforeMount(() => {
    setCurrentRouterHighlight(route);
  });

  // 页面加载时
  onMounted(() => {
    initElMenuOffsetLeft();
  });

  // 路由更新时
  onBeforeRouteUpdate((to) => {
    setCurrentRouterHighlight(to);
    // 修复经典布局开启切割菜单时，点击tagsView后左侧导航菜单数据不变的问题
    const { layout, isClassicSplitMenu } = themeConfig.value;
    if (layout === 'classic' && isClassicSplitMenu) {
      mittBus.emit('setSendClassicChildren', setSendClassicChildren(to.path));
    }
  });
</script>

<style scoped lang="scss">
  .ant-menu-horizontal-wrap {
    flex: 1;
    overflow: hidden;
    margin-right: 30px;
    .ant-menu.ant-menu-horizontal {
      display: flex;
      height: 100%;
      width: 100%;
      box-sizing: border-box;
    }
  }
</style>
