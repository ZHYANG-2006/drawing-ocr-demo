<template>
  <p @click="handleClick" class="text-content">
    {{
      content.value || ''
    }}
  </p>
</template>

<script setup>
  import { defineProps, defineEmits } from 'vue';

  const props = defineProps({
    content: Object,
  });

  const emit = defineEmits();

  function handleClick() {
    emit('jump-to-page', {
      page: props.content.page,
      polygon: props.content.polygon,
    });
  }
</script>

<style scoped>
  p {
    cursor: pointer;
    text-decoration: none;
    color: inherit;
  }

  .text-content {
    white-space: pre-line; /* 解析 \n 为换行 */
  }
</style>
