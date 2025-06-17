<template>
  <div>
    <a-col
      :xs="6"
      :sm="4"
      :md="4"
      :lg="4"
      :xl="4"
      @click="$emit('click', iconName)"
    >
      <div
        class="icon-selector-warp-item"
        :class="{ 'icon-selector-active': prefix === iconName }"
      >
        <!-- 渲染图标 -->
        <component :is="iconComponent" />
      </div>
    </a-col>
  </div>
</template>

<script setup lang="ts">
  import { defineProps, defineEmits } from 'vue';

  const props = defineProps({
    iconName: String,
    iconComponent: Object,
    prefix: String,
  });

  const emit = defineEmits(['click']);
</script>
