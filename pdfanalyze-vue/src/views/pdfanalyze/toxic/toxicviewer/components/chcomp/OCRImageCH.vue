<template>
  <img
    :src="'data:image/jpg;base64,' + content.image_base64"
    alt="Recognized Image"
    @click="handleClick"
  />
</template>

<script setup>
  import { defineProps, defineEmits } from 'vue';

  const props = defineProps({
    content: Object,
  });

  const emit = defineEmits();

  function handleClick() {
    console.log('1');
    console.log(props.content.page);
    console.log(props.content.polygon);
    emit('jump-to-page', {
      page: props.content.page,
      polygon: props.content.polygon,
      review_group_id: props.content.review_group_id,
    });
  }
</script>

<style scoped>
  img {
    cursor: pointer;
    max-width: 100%;
    height: auto;
  }
</style>
