<template>
  <a-config-provider
    :locale="antLocale"
    :size="getGlobalComponentSize"
    :theme="{
      algorithm: theme.defaultAlgorithm,
    }"
  >
    <router-view v-show="themeConfig.lockScreenTime > 1" />
    <LockScreen v-if="themeConfig.isLockScreen" />
    <Setings v-show="themeConfig.lockScreenTime > 1" ref="setingsRef" />
    <CloseFull v-if="!themeConfig.isLockScreen" />
  </a-config-provider>
</template>
<script setup lang="ts" name="app">
  import {
    defineAsyncComponent,
    computed,
    ref,
    onBeforeMount,
    onMounted,
    onUnmounted,
    nextTick,
    watch,
    onBeforeUnmount,
  } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { useRoute } from 'vue-router';
  import { ConfigProvider, notification, theme } from 'ant-design-vue';
  import enUS from 'ant-design-vue/es/locale/en_US';
  import zhCN from 'ant-design-vue/es/locale/zh_CN';
  import zhTW from 'ant-design-vue/es/locale/zh_TW';
  import { storeToRefs } from 'pinia';
  import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import other from '/@/utils/other';
  import { Local, Session } from '/@/utils/storage';
  import mittBus from '/@/utils/mitt';
  import setIntroduction from '/@/utils/setIconfont';
  import websocket from '/@/utils/websocket';
  import { messageCenterStore } from '/@/stores/messageCenter';
  // 定义变量内容
  const { messages, locale } = useI18n(); // 使用 vue-i18n 语言
  const antLocale = computed(() => {
    switch (locale.value) {
      case 'en':
        return enUS;
      case 'zh-cn':
        return zhCN;
      case 'zh-tw':
        return zhTW;
      default:
        return zhCN;
    }
  });
  // 引入组件
  const LockScreen = defineAsyncComponent(
    () => import('/@/layout/lockScreen/index.vue'),
  );
  const Setings = defineAsyncComponent(
    () => import('/@/layout/navBars/breadcrumb/setings.vue'),
  );
  const CloseFull = defineAsyncComponent(
    () => import('/@/layout/navBars/breadcrumb/closeFull.vue'),
  );
  const Upgrade = defineAsyncComponent(
    () => import('/@/layout/upgrade/index.vue'),
  );
  const setingsRef = ref();
  const route = useRoute();
  const stores = useTagsViewRoutes();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);

  // 获取版本号
  const getVersion = computed(() => {
    let isVersion = false;
    if (route.path !== '/login') {
      if (
        // @ts-ignore
        (Local.get('version') && Local.get('version') !== __VERSION__) ||
        !Local.get('version')
      )
        isVersion = true;
    }
    return isVersion;
  });
  // 获取全局组件大小
  const getGlobalComponentSize = computed(() => {
    return other.globalComponentSize();
  });
  // 获取全局 i18n
  const getGlobalI18n = computed(() => {
    return messages.value[locale.value];
  });
  // 设置初始化，防止刷新时恢复默认
  onBeforeMount(() => {
    // 设置批量第三方 icon 图标
    setIntroduction.cssCdn();
    // 设置批量第三方 js
    setIntroduction.jsCdn();
  });
  // 页面加载时
  onMounted(() => {
    nextTick(() => {
      // 监听布局配'置弹窗点击打开
      mittBus.on('openSetingsDrawer', () => {
        setingsRef.value.openDrawer();
      });
      // 获取缓存中的布局配置
      if (Local.get('themeConfig')) {
        storesThemeConfig.setThemeConfig({
          themeConfig: Local.get('themeConfig'),
        });
        document.documentElement.style.cssText = Local.get('themeConfigStyle');
      }
      // 获取缓存中的全屏配置
      if (Session.get('isTagsViewCurrenFull')) {
        stores.setCurrenFullscreen(Session.get('isTagsViewCurrenFull'));
      }
    });
  });
  // 页面销毁时，关闭监听布局配置/i18n监听
  onUnmounted(() => {
    mittBus.off('openSetingsDrawer', () => {});
  });
  // 监听路由的变化，设置网站标题
  watch(
    () => route.path,
    () => {
      other.useTitle();
      other.useFavicon();
      if (!websocket.websocket) {
        //websockt 模块
        try {
          websocket.init(wsReceive);
        } catch (e) {
          console.log('websocket错误');
        }
      }
    },
    {
      deep: true,
    },
  );
  // websocket相关代码

  const wsReceive = (message: any) => {
    try {
      const data = JSON.parse(message.data);
      const { unread, contentType, content } = data;

      messageCenterStore().setUnread(unread);

      if (contentType === 'SYSTEM') {
        notification.success({
          message: '系统消息',
          description: content,
          placement: 'bottomRight',
          duration: 5, // 以秒为单位
        });
      }
    } catch (error) {
      console.error('解析消息时出错:', error);
    }
  };
  onBeforeUnmount(() => {
    // 关闭连接
    websocket.close();
  });
</script>
