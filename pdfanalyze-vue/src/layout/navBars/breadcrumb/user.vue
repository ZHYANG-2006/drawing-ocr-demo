<template>
  <div
    class="layout-navbars-breadcrumb-user pr15"
    :style="{ flex: layoutUserFlexNum }"
  >
    <a-dropdown @click.prevent>
      <div class="layout-navbars-breadcrumb-user-icon">
        <i class="iconfont icon-ziti" :title="$t('message.user.title0')"></i>
      </div>
      <template #overlay>
        <a-menu>
          <a-menu-item
            key="large"
            :disabled="state.disabledSize === 'large'"
            @click="onComponentSizeChange('large')"
          >
            {{ $t('message.user.dropdownLarge') }}
          </a-menu-item>
          <a-menu-item
            key="default"
            :disabled="state.disabledSize === 'default'"
            @click="onComponentSizeChange('default')"
          >
            {{ $t('message.user.dropdownDefault') }}
          </a-menu-item>
          <a-menu-item
            key="small"
            :disabled="state.disabledSize === 'small'"
            @click="onComponentSizeChange('small')"
          >
            {{ $t('message.user.dropdownSmall') }}
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
    <a-dropdown @click.prevent>
      <div class="layout-navbars-breadcrumb-user-icon">
        <i
          class="iconfont"
          :class="
            state.disabledI18n === 'en'
              ? 'icon-fuhao-yingwen'
              : 'icon-fuhao-zhongwen'
          "
          :title="$t('message.user.title1')"
        ></i>
      </div>
      <template #overlay>
        <a-menu>
          <a-menu-item
            key="zh-cn"
            :disabled="state.disabledI18n === 'zh-cn'"
            @click="onLanguageChange('zh-cn')"
          >
            简体中文
          </a-menu-item>
          <a-menu-item
            key="en"
            :disabled="state.disabledI18n === 'en'"
            @click="onLanguageChange('en')"
          >
            English
          </a-menu-item>
          <a-menu-item
            key="zh-tw"
            :disabled="state.disabledI18n === 'zh-tw'"
            @click="onLanguageChange('zh-tw')"
          >
            繁體中文
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
    <div class="layout-navbars-breadcrumb-user-icon" @click="onSearchClick">
      <a-tooltip :title="$t('message.user.title2')">
        <SearchOutlined />
      </a-tooltip>
    </div>
    <div
      class="layout-navbars-breadcrumb-user-icon"
      @click="onLayoutSetingClick"
    >
      <i class="icon-skin iconfont" :title="$t('message.user.title3')"></i>
    </div>
    <div class="layout-navbars-breadcrumb-user-icon">
      <a-popover
        placement="bottom"
        trigger="hover"
        :open="bellHovered"
        :overlay-style="{ width: '300px' }"
        @openChange="handleBellHoverChange"
      >
        <template #content>
          <UserNews />
        </template>
        <a-badge
          :count="messageCenter.unread"
          :hidden="messageCenter.unread === 0"
        >
          <a-tooltip :title="$t('message.user.title4')">
            <BellOutlined />
          </a-tooltip>
        </a-badge>
      </a-popover>
    </div>
    <div
      class="layout-navbars-breadcrumb-user-icon mr10"
      @click="onScreenfullClick"
    >
      <FullscreenOutlined />
    </div>
    <div>
      <span v-if="!isSocketOpen">
        <a-popconfirm
          title="$t('message.user.onlinePrompt')"
          :icon="InfoCircleFilled"
          :ok-text="$t('message.user.retry')"
          trigger="hover"
          @confirm="onlineConfirmEvent"
        >
          <template #title>
            <span>{{ $t('message.user.onlinePrompt') }}</span>
          </template>
          <template #trigger>
            <a-badge
              dot
              :class="{
                'online-status': isSocketOpen,
                'online-down': !isSocketOpen,
              }"
              class="item"
            >
              <img
                :src="userInfos.avatar || headerImage"
                class="layout-navbars-breadcrumb-user-link-photo mr5"
              />
            </a-badge>
          </template>
        </a-popconfirm>
      </span>
    </div>
    <a-dropdown @command="onHandleCommandClick">
      <span class="layout-navbars-breadcrumb-user-link">
        <span v-if="isSocketOpen">
          <a-badge
            dot
            class="item"
            :class="{
              'online-status': isSocketOpen,
              'online-down': !isSocketOpen,
            }"
          >
            <img
              :src="userInfos.avatar || headerImage"
              class="layout-navbars-breadcrumb-user-link-photo mr5"
            />
          </a-badge>
        </span>
        {{ userInfos.username === '' ? 'common' : userInfos.username }}
        <DownOutlined class="el-icon--right" />
      </span>
      <template #overlay>
        <a-menu>
          <a-menu-item key="/home" @click="onHandleCommandClick('/home')">
            {{ $t('message.user.dropdown1') }}
          </a-menu-item>
          <a-menu-item
            key="/personal"
            @click="onHandleCommandClick('/personal')"
          >
            {{ $t('message.user.dropdown2') }}
          </a-menu-item>
          <a-menu-item
            key="logOut"
            divider
            @click="onHandleCommandClick('logOut')"
          >
            {{ $t('message.user.dropdown5') }}
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>

    <Search ref="searchRef" />
  </div>
</template>

<script setup lang="ts" name="layoutBreadcrumbUser">
  import {
    defineAsyncComponent,
    ref,
    computed,
    reactive,
    onMounted,
    unref,
    watch,
  } from 'vue';
  import { useRouter } from 'vue-router';
  import { Modal, notification } from 'ant-design-vue';
  import screenfull from 'screenfull';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import { useUserInfo } from '/@/stores/userInfo';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import other from '/@/utils/other';
  import mittBus from '/@/utils/mitt';
  import { Session, Local } from '/@/utils/storage';
  import headerImage from '/@/assets/img/headerImage.png';
  import websocket from '/@/utils/websocket';
  // 引入组件
  const UserNews = defineAsyncComponent(
    () => import('/@/layout/navBars/breadcrumb/userNews.vue'),
  );
  const Search = defineAsyncComponent(
    () => import('/@/layout/navBars/breadcrumb/search.vue'),
  );

  // 定义变量内容
  const { locale, t } = useI18n();
  const router = useRouter();
  const stores = useUserInfo();
  const storesThemeConfig = useThemeConfig();
  const { userInfos } = storeToRefs(stores);
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const searchRef = ref();
  const state = reactive({
    isScreenfull: false,
    disabledI18n: 'zh-cn',
    disabledSize: 'large',
  });

  // 设置分割样式
  const layoutUserFlexNum = computed(() => {
    let num: string | number = '';
    const { layout, isClassicSplitMenu } = themeConfig.value;
    const layoutArr: string[] = ['defaults', 'columns'];
    if (
      layoutArr.includes(layout) ||
      (layout === 'classic' && !isClassicSplitMenu)
    )
      num = '1';
    else num = '';
    return num;
  });

  // 定义变量内容
  const { isSocketOpen } = storeToRefs(useUserInfo());

  // websocket状态
  const onlinePopoverRef = ref();
  const onlineConfirmEvent = () => {
    if (!isSocketOpen.value) {
      websocket.is_reonnect = true;
      websocket.reconnect_current = 1;
      websocket.reconnect();
    }
    // 手动隐藏弹出
    unref(onlinePopoverRef).popperRef?.delayHide?.();
  };
  // 全屏点击时
  const onScreenfullClick = () => {
    if (!screenfull.isEnabled) {
      notification.warning({
        message: '暂不支持全屏',
        description: '无法全屏的情况',
      });
      return false;
    }
    screenfull.toggle();
    screenfull.on('change', () => {
      if (screenfull.isFullscreen) state.isScreenfull = true;
      else state.isScreenfull = false;
    });
  };
  // 布局配置 icon 点击时
  const onLayoutSetingClick = () => {
    mittBus.emit('openSetingsDrawer');
  };
  // 下拉菜单点击时
  const onHandleCommandClick = (path: string) => {
    if (path === 'logOut') {
      Modal.confirm({
        title: t('message.user.logOutTitle'),
        content: t('message.user.logOutMessage'),
        okText: t('message.user.logOutConfirm'),
        cancelText: t('message.user.logOutCancel'),
        onOk: async () => {
          // 清除缓存/token等
          Session.clear();
          // 使用 reload 时，不需要调用 resetRoute() 重置路由
          window.location.reload();
        },
        onCancel() {
          // 取消操作可以不做任何事情
        },
      });
    } else {
      router.push(path);
    }
  };

  const bellHovered = ref<boolean>(false);
  const handleBellHoverChange = (visible: boolean) => {
    bellHovered.value = visible;
  };

  // 菜单搜索点击
  const onSearchClick = () => {
    searchRef.value.openSearch();
  };
  // 组件大小改变
  const onComponentSizeChange = (size: string) => {
    Local.remove('themeConfig');
    themeConfig.value.globalComponentSize = size;
    Local.set('themeConfig', themeConfig.value);
    initI18nOrSize('globalComponentSize', 'disabledSize');
    window.location.reload();
  };
  // 语言切换
  const onLanguageChange = (lang: string) => {
    Local.remove('themeConfig');
    themeConfig.value.globalI18n = lang;
    Local.set('themeConfig', themeConfig.value);
    locale.value = lang;
    other.useTitle();
    initI18nOrSize('globalI18n', 'disabledI18n');
  };
  // 初始化组件大小/i18n
  const initI18nOrSize = (value: string, attr: string) => {
    if (attr in state) {
      if (attr === 'isScreenfull')
        state['isScreenfull'] = Local.get('themeConfig')[value]; // 明确指定类型
      // 确保 attr 是 state 的键
      else if (attr === 'disabledI18n')
        state['disabledI18n'] = Local.get('themeConfig')[value];
      else state['disabledSize'] = Local.get('themeConfig')[value];
    }
  };
  // 页面加载时
  onMounted(() => {
    if (Local.get('themeConfig')) {
      initI18nOrSize('globalComponentSize', 'disabledSize');
      initI18nOrSize('globalI18n', 'disabledI18n');
    }
  });

  //消息中心的未读数量
  import { messageCenterStore } from '/@/stores/messageCenter';
  const messageCenter = messageCenterStore();
</script>

<style scoped lang="scss">
  .layout-navbars-breadcrumb-user {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    &-link {
      height: 100%;
      display: flex;
      align-items: center;
      white-space: nowrap;
      &-photo {
        width: 25px;
        height: 25px;
        border-radius: 100%;
      }
    }
    &-icon {
      padding: 0 10px;
      cursor: pointer;
      color: var(--next-bg-topBarColor);
      height: 50px;
      line-height: 50px;
      display: flex;
      align-items: center;
      &:hover {
        background: var(--next-color-user-hover);
        i {
          display: inline-block;
          animation: logoAnimation 0.3s ease-in-out;
        }
        .ant-badge {
          display: inline-block;
          animation: logoAnimation 0.3s ease-in-out;
        }
        .anticon {
          display: inline-block;
          animation: logoAnimation 0.3s ease-in-out;
        }
      }
    }
    :deep(.ant-dropdown) {
      color: var(--next-bg-topBarColor);
    }
    :deep(.ant-badge) {
      height: 40px;
      line-height: 40px;
      display: flex;
      align-items: center;
    }
    :deep(.ant-badge__content.is-fixed) {
      top: 12px;
    }
    .anticon {
      display: inline-block;
      animation: iconAnimation 0.3s ease-in-out;
    }
    .online-status {
      cursor: pointer;
      :deep(.ant-badge__content.is-fixed) {
        top: 30px;
        font-size: 14px;
        left: 5px;
        height: 12px;
        width: 12px;
        padding: 0;
        background-color: #18bc9c;
      }
    }
    .online-down {
      cursor: pointer;
      :deep(.ant-badge__content.is-fixed) {
        top: 30px;
        font-size: 14px;
        left: 5px;
        height: 12px;
        width: 12px;
        padding: 0;
        background-color: #979b9c;
      }
    }
  }
</style>
