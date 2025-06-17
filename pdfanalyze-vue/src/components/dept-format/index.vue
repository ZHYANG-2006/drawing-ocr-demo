<template>
  <div>
    {{ data }}
  </div>
</template>

<script setup lang="ts">
  import { defineProps, ref, watch } from 'vue';
  import { useDeptInfoStore } from '/@/stores/modules/dept';

  const props = defineProps({
    modelValue: {
      type: [Number, String],
      default: undefined, // 提供默认值
    },
  });

  const data = ref('');

  watch(
    () => props.modelValue,
    async (newVal) => {
      if (newVal !== undefined && newVal !== null) {
        const numericVal =
          typeof newVal === 'string' ? parseInt(newVal) : newVal;
        if (!isNaN(numericVal)) {
          const deptInfoStore = useDeptInfoStore();
          const result = await deptInfoStore.getParentDeptById(numericVal);
          if (result?.nodes) {
            let name = '';
            result.nodes.forEach((item: any, index: number) => {
              name += index > 0 ? `/${item.name}` : item.name;
            });
            data.value = name;
          }
        }
      } else {
        data.value = ''; // 处理为空的情况
      }
    },
    { immediate: true },
  );
</script>
