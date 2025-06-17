<template>
  <slot v-if="getUserAuthBtnList"></slot>
</template>

<script setup lang="ts" name="authAll">
  import { computed, PropType } from 'vue'; // 确保正确引入 PropType
  import { storeToRefs } from 'pinia';
  import { useUserInfo } from '/@/stores/userInfo';
  import { judementSameArr } from '/@/utils/arrayOperation';

  // 定义父组件传过来的值，并为其类型定义为 string[]
  const props = defineProps({
    value: {
      type: Array as PropType<string[]>, // 使用 PropType 来定义 props 的类型
      default: () => [],
    },
  });

  // 定义变量内容
  const stores = useUserInfo();
  const { userInfos } = storeToRefs(stores);

  // 获取 pinia 中的用户权限
  const getUserAuthBtnList = computed(() => {
    return judementSameArr(
      props.value,
      userInfos.value.authBtnList as string[],
    ); // 确保 authBtnList 是 string[]
  });
</script>
