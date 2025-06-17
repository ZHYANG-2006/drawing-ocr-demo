<template>
  <p @click="handleClick">
    {{
      content.has_strike_through || content.has_xbar
        ? content.true_ch_value
        : content.ch_value || ''
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
      review_group_id: props.content.review_group_id,
    });
  }
</script>

<style scoped>
  p {
    cursor: pointer;
    text-decoration: none;
    color: inherit;
  }
</style>
