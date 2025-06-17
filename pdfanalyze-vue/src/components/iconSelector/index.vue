<template>
  <div class="icon-selector">
    <a-popover
      v-model:open="state.popoverOpen"
      placement="bottom"
      :width="state.fontIconWidth"
      popper-class="icon-selector-popper"
      trigger="click"
    >
      <a-input
        ref="inputWidthRef"
        v-model:value="state.fontIconSearch"
        :placeholder="state.fontIconPlaceholder"
        clearable
        :disabled="disabled"
        :size="size"
        @clear="onClearFontIcon"
        @focus="onIconFocus"
        @blur="onIconBlur"
      >
        <!-- 使用 component 动态渲染图标 -->
        <template #prefix>
          <!-- 动态显示选中的 Ant Design 图标 -->
          <component :is="state.fontIconPrefix || prepend" class="font14" />
          <a-divider type="vertical" style="border-color: #000; opacity: 0.4" />
        </template>
      </a-input>

      <template #content>
        <div class="icon-selector-warp">
          <div class="icon-selector-warp-title">{{ title }}</div>
          <IconList
            :list="fontIconSheetsFilterList"
            :empty="emptyDescription"
            :prefix="state.fontIconPrefix"
            @get-icon="onColClick"
          />
        </div>
      </template>
    </a-popover>
  </div>
</template>

<script setup lang="ts" name="iconSelector">
  import {
    ref,
    reactive,
    nextTick,
    computed,
    onMounted,
    watch,
    PropType,
    defineAsyncComponent,
    getCurrentInstance,
    inject,
  } from 'vue';

  import icons from '/@/components/iconSelector/icons.json';
  import type { MenuFormDataType } from '/@/types/types';

  // 定义父组件传过来的值
  const props = defineProps({
    prepend: {
      type: String,
      default: () => 'CloseCircleOutlined', // 默认图标
    },
    placeholder: {
      type: String,
      default: () => '请输入内容搜索图标或者选择图标',
    },
    size: {
      type: String as PropType<'small' | 'middle' | 'large'>,
      default: 'middle',
    },
    title: {
      type: String,
      default: () => '请选择图标',
    },
    disabled: {
      type: Boolean,
      default: () => false,
    },
    clearable: {
      type: Boolean,
      default: () => true,
    },
    emptyDescription: {
      type: String,
      default: () => '无相关图标',
    },
    modelValue: {
      type: String,
      default: '',
    },
  });

  const emit = defineEmits(['update:modelValue', 'get', 'clear']);

  const IconList = defineAsyncComponent(
    () => import('/@/components/iconSelector/list.vue'),
  );

  const menuFormData = inject('menuFormData') as MenuFormDataType;

  const inputWidthRef = ref();

  const state = reactive({
    fontIconPrefix: '',
    fontIconWidth: 0,
    fontIconSearch: '',
    fontIconPlaceholder: '',
    fontIconList: icons,
    popoverOpen: false,
  });

  // 图标搜索及展示逻辑
  const fontIconSheetsFilterList = computed(() => {
    if (!state.fontIconSearch) return state.fontIconList;
    const search = state.fontIconSearch.trim().toLowerCase();
    return state.fontIconList.filter((item: string) =>
      item.toLowerCase().includes(search),
    );
  });

  // 图标点击逻辑
  const onColClick = (v: string) => {
    state.fontIconPlaceholder = v;
    state.fontIconPrefix = v;
    console.log('###');
    console.log('v');
    console.log(v);
    emit('get', menuFormData.icon);
    emit('update:modelValue', menuFormData.icon);
    state.popoverOpen = false;
    inputWidthRef.value.focus();
  };

  // 清除图标逻辑
  const onClearFontIcon = () => {
    state.fontIconPrefix = '';
    emit('clear', state.fontIconPrefix);
    emit('update:modelValue', state.fontIconPrefix);
  };

  // 处理输入框聚焦时的逻辑
  const onIconFocus = () => {
    if (!props.modelValue) return false;
    state.fontIconSearch = '';
    state.fontIconPlaceholder = props.modelValue;
  };
  // 处理输入框失去焦点时的逻辑
  const onIconBlur = () => {
    const icon = state.fontIconList.filter(
      (icon: string) => icon === state.fontIconSearch,
    );
    if (icon.length <= 0) state.fontIconSearch = '';
  };

  // 获取 input 宽度
  const getInputWidth = () => {
    nextTick(() => {
      state.fontIconWidth = inputWidthRef.value.offsetWidth;
    });
  };

  // 监听页面宽度改变
  const initResize = () => {
    window.addEventListener('resize', () => {
      getInputWidth();
    });
  };
  // 页面加载时
  onMounted(() => {
    initResize();
    getInputWidth();
    console.log('modelvalue');
    console.log(props);
    console.log('menuData', { menuFormData });
    state.fontIconPrefix = menuFormData.icon || '';
    state.fontIconPlaceholder = menuFormData.icon || '';
    console.log('IconSelector modelValue updated:', state.fontIconPrefix);
  });
  // 监听 modelValue 变化
  /*
  watch(
    () => props.modelValue,
    (newValue) => {
      state.fontIconPrefix = newValue || '';
      console.log('IconSelector modelValue updated:', newValue);
    },
    { immediate: true },
  );
  */
</script>

<style scoped lang="scss">
  .icon-selector-warp {
    height: 250px;
    width: 230px;
  }
  .icon-selector-warp-title {
    font-weight: bold;
    margin-bottom: 10px;
  }
  .icon-selector-popper {
    max-height: 400px;
    overflow-y: auto;
  }
</style>
