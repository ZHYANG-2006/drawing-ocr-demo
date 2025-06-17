<template>
  <div class="icon-selector-warp-row">
    <PerfectScrollbar ref="selectorScrollbarRef">
      <!-- 使用 a-row 和 a-col 控制每行图标数量 -->
      <a-row v-if="list.length > 0" :gutter="[10, 10]">
        <a-col
          v-for="(iconName, index) in list"
          :key="index"
          :span="4"
          @click="onColClick(iconName as string)"
        >
          <div
            class="icon-selector-warp-item"
            :class="{ 'icon-selector-active': prefix === iconName }"
          >
            <!-- 渲染图标 -->
            <component :is="getIconComponent(iconName as string)" />
          </div>
        </a-col>
      </a-row>
      <!-- 空状态 -->
      <a-empty v-else :image-size="100" :description="empty" />
    </PerfectScrollbar>
  </div>
</template>

<script setup lang="ts" name="iconSelectorList">
  import { getCurrentInstance } from 'vue';

  // 定义父组件传入的属性
  const props = defineProps({
    list: { type: Array, default: () => [] },
    empty: { type: String, default: '无相关图标' },
    prefix: { type: String, default: '' },
  });

  // 获取全局 Icons
  const { appContext } = getCurrentInstance()!;
  const Icons = appContext.config.globalProperties.$icons;

  // 获取图标组件
  const getIconComponent = (iconName: string) => {
    return Icons[iconName] || null;
  };

  // 定义子组件向父组件传递事件
  const emit = defineEmits(['get-icon']);
  // 点击图标时触发事件
  const onColClick = (iconName: string) => {
    console.log('$$$');
    emit('get-icon', iconName);
  };
</script>

<style scoped lang="scss">
  .icon-selector-warp-row {
    height: 230px;
    overflow: auto;
  }

  .icon-selector-warp-item {
    display: flex;
    justify-content: center;
    align-items: center;
    border: 1px solid var(--ant-border-color);
    border-radius: 5px;
    margin-bottom: 10px;
    height: 40px;
    cursor: pointer;
    i {
      font-size: 20px;
      color: var(--ant-text-color-regular);
    }
    &:hover {
      background-color: var(--ant-color-primary-light-9);
      border-color: var(--ant-color-primary-light-5);
      i {
        color: var(--ant-color-primary);
      }
    }
  }

  .icon-selector-active {
    background-color: var(--ant-color-primary-light-9);
    border-color: var(--ant-color-primary-light-5);
    i {
      color: var(--ant-color-primary);
    }
  }
</style>
