<template>
  <div class="layout-navbars-breadcrumb-user-news">
    <div class="head-box">
      <div class="head-box-title">{{ $t('message.user.newTitle') }}</div>
      <!-- <div class="head-box-btn" v-if="state.newsList.length > 0" @click="onAllReadClick">{{ $t('message.user.newBtn') }}</div> -->
    </div>
    <div class="content-box">
      <template v-if="state.newsList.length > 0">
        <div v-for="(v, k) in state.newsList" :key="k" class="content-box-item">
          <div>{{ v.title }}</div>
          <div class="content-box-msg">
            <div v-html="v.content"></div>
          </div>
          <div class="content-box-time">{{ v.create_datetime }}</div>
        </div>
      </template>
      <a-empty v-else :description="$t('message.user.newDesc')" />
    </div>
    <div
      v-if="state.newsList.length > 0"
      class="foot-box"
      @click="onGoToGiteeClick"
    >
      {{ $t('message.user.newGo') }}
    </div>
  </div>
</template>

<script setup lang="ts" name="layoutBreadcrumbUserNews">
  import { reactive, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { request } from '/@/utils/service';

  // 定义变量内容
  const state = reactive({
    newsList: [] as any,
  });

  // 全部已读点击
  const onAllReadClick = () => {
    state.newsList = [];
  };

  // 前往通知中心点击
  const route = useRouter();
  const onGoToGiteeClick = () => {
    route.push('/messageCenter');
  };

  // 获取最新消息
  const getLastMsg = () => {
    request({
      url: '/api/system/message_center/get_newest_msg/',
      method: 'get',
      params: {},
    }).then((res: any) => {
      const { data } = res;
      state.newsList = [data];
    });
  };

  onMounted(() => {
    getLastMsg();
  });
</script>

<style scoped lang="scss">
  .layout-navbars-breadcrumb-user-news {
    .head-box {
      display: flex;
      border-bottom: 1px solid var(--ant-border-color-base);
      box-sizing: border-box;
      color: var(--ant-text-color);
      justify-content: space-between;
      height: 35px;
      align-items: center;
      .head-box-btn {
        color: var(--ant-primary-color);
        font-size: 13px;
        cursor: pointer;
        opacity: 0.8;
        &:hover {
          opacity: 1;
        }
      }
    }
    .content-box {
      font-size: 13px;
      .content-box-item {
        padding-top: 12px;
        &:last-of-type {
          padding-bottom: 12px;
        }
        .content-box-msg {
          color: var(--ant-text-color-secondary);
          margin-top: 5px;
          margin-bottom: 5px;
        }
        .content-box-time {
          color: var(--ant-text-color-secondary);
        }
      }
    }
    .foot-box {
      height: 35px;
      color: var(--ant-primary-color);
      font-size: 13px;
      cursor: pointer;
      opacity: 0.8;
      display: flex;
      align-items: center;
      justify-content: center;
      border-top: 1px solid var(--ant-border-color-base);
      &:hover {
        opacity: 1;
      }
    }
  }
</style>
