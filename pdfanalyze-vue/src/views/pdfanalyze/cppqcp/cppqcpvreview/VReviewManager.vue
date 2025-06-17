<template>
  <div>
    <VRviewTable ref="vreviewTable" />
  </div>
</template>

<script setup>
  import { ref } from 'vue';
  import { message } from 'ant-design-vue';
  import VRviewTable from './components/VReviewfTable.vue';

  // 引用模态框组
  const vreviewTable = ref(null);
</script>
