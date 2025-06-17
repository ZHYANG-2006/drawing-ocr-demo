<template>
  <div class="login-container flex z-10">
    <div class="login-left">
      <div class="login-left-logo">
        <img :src="siteLogo" />
      </div>
      <img :src="loginBg" class="login-left-waves" />
    </div>
    <div class="login-right flex z-10">
      <div class="login-right-warp flex-margin">
        <div class="login-right-warp-main">
          <div class="login-right-warp-main-title">MFLEX 客户文件识别系统</div>
          <div class="login-right-warp-main-form">
            <div v-if="!state.isScan">
              <a-tabs v-model:activekey="state.tabsActiveName">
                <a-tab-pane key="account" :tab="$t('message.label.one1')">
                  <Account />
                </a-tab-pane>
                <!-- TODO 手机号码登录未接入，展示隐藏 -->
                <!-- <a-tab-pane :tab="$t('message.label.two2')" key="mobile">
									<Mobile />
								</a-tab-pane> -->
              </a-tabs>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="login-authorization z-10">
      <p>MFLEX AI-Analyze</p>
    </div>
  </div>
  <div v-if="siteBg">
    <img :src="siteBg" class="fixed inset-0 z-1 w-full h-full" />
  </div>
</template>

<script setup lang="ts" name="loginIndex">
  import { defineAsyncComponent, onMounted, reactive, computed } from 'vue';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import { NextLoading } from '/@/utils/loading';
  import logoMini from '/@/assets/mflexlogo.png';
  import loginMain from '/@/assets/login1.png';
  import loginBg from '/@/assets/login-bg.svg';
  import { SystemConfigStore } from '/@/stores/systemConfig';
  import { getBaseURL } from '/@/utils/baseUrl';
  import _ from 'lodash-es';

  // 引入组件
  const Account = defineAsyncComponent(
    () => import('/@/views/system/login/component/account.vue'),
  );

  // 定义变量内容
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const state = reactive({
    tabsActiveName: 'account',
    isScan: false,
  });

  // 获取布局配置信息
  const getThemeConfig = computed(() => {
    return themeConfig.value;
  });

  const systemConfigStore = SystemConfigStore();
  const { systemConfig } = storeToRefs(systemConfigStore);
  const getSystemConfig = computed(() => {
    return systemConfig.value;
  });

  const siteLogo = computed(() => {
    if (!_.isEmpty(getSystemConfig.value['login.site_logo'])) {
      return getSystemConfig.value['login.site_logo'];
    }
    return logoMini;
  });

  const siteBg = computed(() => {
    if (!_.isEmpty(getSystemConfig.value['login.login_background'])) {
      return getSystemConfig.value['login.login_background'];
    }
  });

  // 页面加载时
  onMounted(() => {
    NextLoading.done();
  });
</script>

<style scoped lang="scss">
  .login-container {
    display: flex;
    height: 100%;
    background: var(--ant-color-black);

    .login-left {
      flex: 1;
      position: relative;
      background-color: rgba(211, 239, 255, 1);
      margin-right: 100px;

      .login-left-logo {
        display: flex;
        align-items: center;
        position: absolute;
        top: 50px;
        left: 80px;
        z-index: 1;
        animation: logoAnimation 0.3s ease;

        img {
          width: 102px;
          height: 62px;
        }
      }

      .login-left-waves {
        position: absolute;
        top: 0;
        right: -100px;
      }
    }

    .login-right {
      width: 700px;

      .login-right-warp {
        border: 1px solid var(--ant-color-primary);
        border-radius: 3px;
        width: 500px;
        height: 500px;
        position: relative;
        overflow: hidden;
        background-color: var(--ant-color-white);

        .login-right-warp-main {
          display: flex;
          flex-direction: column;
          height: 100%;

          .login-right-warp-main-title {
            font-size: 27px;
            font-weight: 800;
            color: #081642;
            text-shadow: 3px 5px 10px rgba(0, 0, 0, 0.2);
            text-align: center;
            text-transform: uppercase;
            padding: 1em 0;
            letter-spacing: 3px;
            animation: logoAnimation 0.3s ease;
            animation-delay: 0.3s;
          }

          .login-right-warp-main-form {
            flex: 1;
            padding: 0 50px 50px;
          }
        }
      }
    }

    .login-authorization {
      position: fixed;
      bottom: 30px;
      left: 0;
      right: 0;
      text-align: center;

      p {
        font-size: 14px;
        color: rgba(0, 0, 0, 0.5);
      }
    }
  }
</style>
