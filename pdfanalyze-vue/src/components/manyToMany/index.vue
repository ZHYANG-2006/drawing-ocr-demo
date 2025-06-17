<template>
  <a-tag
    v-for="(item, index) in data"
    :key="index"
    class="many-to-many-tag"
    :color="randomType"
    >{{ item }}
  </a-tag>
</template>

<script lang="ts" setup>
  import { watch, ref } from 'vue';

  const props = defineProps({
    modelValue: Array,
    bindValue: Array,
    displayLabel: {
      type: String,
      default: '',
    },
  });

  // template上使用data
  const data = ref<string[] | null>(null);
  watch(
    () => props.bindValue, // 监听bindValue的变化，
    (value) => {
      const { displayLabel } = props;
      const result = value
        ? value.map((item: any) => {
            return item[displayLabel];
          })
        : null;
      data.value = result;
    },
    { immediate: true }, // 立即触发一次，给data赋值初始值
  );

  const tagType = ['green', 'blue', 'orange', 'red'];
  const randomType = (): string => {
    return tagType[Math.floor(Math.random() * tagType.length)];
  };
</script>

<style scoped>
  .many-to-many-tag {
    margin-right: 5px;
  }
  .many-to-many-tag:last-child {
    margin-right: 0;
  }
</style>
