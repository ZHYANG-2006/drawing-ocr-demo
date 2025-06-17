<template>
  <div class="upgrade-dialog">
    <a-modal
      :open="state.isUpgrade"
      width="300px"
      destroy-on-close
      closable="false"
      mask-closable="false"
      keyboard="false"
    >
      <div class="upgrade-title">
        <div class="upgrade-title-warp">
          <span class="upgrade-title-warp-txt">{{
            $t('message.upgrade.title')
          }}</span>
          <span class="upgrade-title-warp-version">v{{ state.version }}</span>
        </div>
      </div>
      <div class="upgrade-content">
        {{ getThemeConfig.globalTitle }} {{ $t('message.upgrade.msg') }}
        <div class="upgrade-content-desc mt5">
          {{ $t('message.upgrade.desc') }}
        </div>
      </div>
      <div class="upgrade-btn">
        <a-button round type="text" @click="onCancel">{{
          $t('message.upgrade.btnOne')
        }}</a-button>
        <a-button
          type="primary"
          round
          :loading="state.isLoading"
          @click="onUpgrade"
          >{{ state.btnTxt }}
        </a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts" name="layoutUpgrade">
  import { reactive, computed, onMounted } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import { Local, Session } from '/@/utils/storage';

  // 定义变量内容
  const { t } = useI18n();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const state = reactive({
    isUpgrade: false,
    // @ts-ignore
    version: __VERSION__,
    isLoading: false,
    btnTxt: '',
  });

  // 获取布局配置信息
  const getThemeConfig = computed(() => {
    return themeConfig.value;
  });
  // 残忍拒绝
  const onCancel = () => {
    state.isUpgrade = false;
    Session.set('isUpgrade', false);
  };
  // 马上更新
  const onUpgrade = () => {
    state.isLoading = true;
    state.btnTxt = t('message.upgrade.btnTwoLoading');
    setTimeout(() => {
      Local.clear();
      window.location.reload();
      Local.set('version', state.version);
      Session.set('isUpgrade', false);
    }, 2000);
  };
  // 延迟显示，防止刷新时界面显示太快
  const delayShow = () => {
    const isUpgrade =
      Session.get('isUpgrade') === false ? Session.get('isUpgrade') : true;
    if (isUpgrade) {
      setTimeout(() => {
        state.isUpgrade = true;
      }, 2000);
    }
  };
  // 页面加载时
  onMounted(() => {
    delayShow();
    setTimeout(() => {
      state.btnTxt = t('message.upgrade.btnTwo');
    }, 200);
  });
</script>

<style scoped lang="scss">
  .upgrade-dialog {
    :deep(.ant-modal) {
      .ant-modal-body {
        padding: 0 !important;
      }
      .ant-modal-header {
        display: none !important;
      }
      .upgrade-title {
        text-align: center;
        height: 130px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        &::after {
          content: '';
          position: absolute;
          background-color: var(--ant-primary-color-light-1);
          width: 130%;
          height: 130px;
          border-bottom-left-radius: 100%;
          border-bottom-right-radius: 100%;
        }
        .upgrade-title-warp {
          z-index: 1;
          position: relative;
          .upgrade-title-warp-txt {
            color: var(--ant-color-white);
            font-size: 22px;
            letter-spacing: 3px;
          }
          .upgrade-title-warp-version {
            color: var(--ant-color-white);
            background-color: var(--ant-primary-color-light-4);
            font-size: 12px;
            position: absolute;
            display: flex;
            top: -2px;
            right: -50px;
            padding: 2px 4px;
            border-radius: 2px;
          }
        }
      }
      .upgrade-content {
        padding: 20px;
        line-height: 22px;
        .upgrade-content-desc {
          color: var(--ant-info-light-5);
          font-size: 12px;
        }
      }
      .upgrade-btn {
        border-top: 1px solid var(--ant-border-color-lighter, #ebeef5);
        display: flex;
        justify-content: space-around;
        padding: 15px 20px;
        .ant-btn {
          width: 100%;
        }
      }
    }
  }
</style>
