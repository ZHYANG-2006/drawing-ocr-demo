<template>
  <div class="layout-search-dialog">
    <a-modal
      v-model:open="state.isShowSearch"
      :closable="false"
      :footer="null"
      destroy-on-close
    >
      <a-auto-complete
        ref="layoutMenuAutocompleteRef"
        v-model:value="state.menuQuery"
        :options="suggestions"
        placeholder="搜索菜单"
        style="width: 100%"
        :filter-option="false"
      >
        <template #option="option">
          <div>
            <SvgIcon :name="option.meta.icon" class="mr5" />
            {{ $t(option.meta.title) }}
          </div>
        </template>
      </a-auto-complete>
    </a-modal>
  </div>
</template>

<script setup lang="ts" name="layoutBreadcrumbSearch">
  import { reactive, ref, nextTick } from 'vue';
  import { useRouter } from 'vue-router';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';

  interface Suggestion {
    value: string;
    label: string;
    meta: {
      // define additional meta properties if needed
    };
  }

  interface RouteMeta {
    title: string; // Name used in the menu bar, tags view bar, and menu search (localized)
    isLink?: string; // URL if it's an external link, should be non-empty if used
    isHide?: boolean; // Whether to hide this route
    isKeepAlive?: boolean; // Whether to cache the component state
    isAffix?: boolean; // Whether to pin to the tags view bar
    isIframe?: boolean; // Whether it is an iframe, requires isIframe true and isLink non-empty
    roles?: string[]; // Permissions identifier for the route, e.g., ['admin', 'common']
    icon?: string; // Icon for the menu and tags view, prefixed accordingly (e.g., 'iconfont xxx', 'fa xxx')
  }

  interface RouteItem {
    path?: string;
    meta: RouteMeta;
  }
  // 定义变量内容
  const storesTagsViewRoutes = useTagsViewRoutes();
  const { tagsViewRoutes } = storeToRefs(storesTagsViewRoutes);
  const layoutMenuAutocompleteRef = ref();
  const { t } = useI18n();
  const router = useRouter();
  const state = reactive<SearchState>({
    isShowSearch: false,
    menuQuery: '',
    tagsViewList: [],
  });

  const suggestions = ref<Suggestion[]>([]);

  // 搜索弹窗打开
  const openSearch = () => {
    state.menuQuery = '';
    state.isShowSearch = true;
    initTageView();
    nextTick(() => {
      setTimeout(() => {
        layoutMenuAutocompleteRef.value.focus();
      });
    });
  };

  // 搜索弹窗关闭
  const closeSearch = () => {
    state.isShowSearch = false;
  };

  // 菜单搜索数据过滤
  const menuSearch = (queryString: string) => {
    if (queryString) {
      suggestions.value = state.tagsViewList
        .filter(createFilter(queryString))
        .map((item) => ({
          value: item.path,
          label: item.meta.title,
          meta: item.meta,
        }));
    } else {
      suggestions.value = [];
    }
  };

  // 菜单搜索过滤
  const createFilter = (queryString: string) => {
    return (restaurant: RouteItem) => {
      // Ensure both path and meta.title are defined before including them in the filter
      const queryLower = queryString.toLowerCase();
      return (
        (restaurant.path?.toLowerCase().includes(queryLower) ?? false) ||
        (restaurant.meta?.title?.toLowerCase().includes(queryLower) ?? false) ||
        t(restaurant.meta?.title ?? '')
          .toLowerCase()
          .includes(queryLower)
      );
    };
  };

  // 初始化菜单数据
  const initTageView = () => {
    if (state.tagsViewList.length > 0) return;
    tagsViewRoutes.value.forEach((v: RouteItem) => {
      if (!v.meta?.isHide) state.tagsViewList.push({ ...v });
    });
  };

  // 当前菜单选中时
  const onHandleSelect = (value: string | number | any) => {
    const item = state.tagsViewList.find((route) => route.path === value);
    if (!item) return;

    const { path, redirect, meta } = item;
    if (meta?.isLink && !meta?.isIframe) window.open(meta?.isLink);
    else if (redirect) router.push(redirect);
    else router.push(path);
    closeSearch();
  };

  // 暴露变量
  defineExpose({
    openSearch,
  });
</script>

<style scoped lang="scss">
  .layout-search-dialog {
    position: relative;
    :deep(.ant-modal) {
      .ant-modal-content {
        .ant-modal-header,
        .ant-modal-body {
          display: none;
        }
        .ant-modal-footer {
          position: absolute;
          left: 50%;
          transform: translateX(-50%);
          top: -53vh;
        }
      }
      :deep(.ant-select) {
        width: 560px;
        position: absolute;
        top: 150px;
        left: 50%;
        transform: translateX(-50%);
      }
    }
  }
</style>
