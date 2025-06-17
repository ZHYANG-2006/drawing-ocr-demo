<template>
  <a-tag :color="randomType">{{ data }}</a-tag>
</template>

<script lang="ts" setup>
  import { watch, ref } from 'vue';

  // 正确声明 props 的类型
  const props = defineProps({
    modelValue: {
      type: [String, Object],
      default: null,
    },
    displayLabel: {
      type: String,
      default: '',
    },
  });

  // 使用 data 来显示 modelValue 的值
  const data = ref<string | null>(null);

  // 监听 modelValue 的变化
  watch(
    () => props.modelValue,
    (value) => {
      if (typeof value === 'string') {
        data.value = value;
      } else if (typeof value === 'object' && value !== null) {
        const { displayLabel } = props;
        data.value = value[displayLabel] || null;
      } else {
        data.value = null;
      }
    },
    { immediate: true }, // 初始化时立即触发
  );

  // 定义随机的标签颜色
  const tagType = ['success', 'info', 'warning', 'danger'];
  const randomType = (): string => {
    return tagType[Math.floor(Math.random() * tagType.length)];
  };
</script>
