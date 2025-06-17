<template>
  <template v-for="val in chils" :key="val.path">
    <a-sub-menu
      v-if="val.children && val.children.length > 0"
      :key="`sub-${val.path}`"
    >
      <template #title>
        <SvgIcon :name="String(val.meta?.icon || 'default-icon')" />
        <span>{{ $t(String(val.meta?.title || 'default-title')) }}</span>
      </template>
      <nav-menu-sub-item :chil="val.children" />
    </a-sub-menu>
    <a-menu-item v-else :key="`item-${val.path}`">
      <template
        v-if="
          val.meta &&
          (!val.meta.isLink || (val.meta.isLink && val.meta.isIframe))
        "
      >
        <SvgIcon :name="String(val.meta?.icon || 'default-icon')" />
        <span>{{ $t(String(val.meta?.title || 'default-title')) }}</span>
      </template>
      <template v-else>
        <a class="w100" @click.prevent="onALinkClick(val)">
          <SvgIcon :name="String(val.meta?.icon || 'default-icon')" />
          {{ $t(String(val.meta?.title || 'default-title')) }}
        </a>
      </template>
    </a-menu-item>
  </template>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import { RouteRecordRaw } from 'vue-router';
  import other from '/@/utils/other';

  // 定义父组件传过来的值
  const props = defineProps({
    chil: {
      type: Array as () => RouteRecordRaw[],
      default: () => [],
    },
  });

  // 获取父级菜单数据
  const chils = computed(() => {
    return props.chil || [];
  });

  // 打开外部链接
  const onALinkClick = (val: RouteRecordRaw) => {
    // 假设 val.meta.isLink 为外部链接的地址
    const link = val.meta?.isLink;

    if (typeof link === 'string') {
      // 判断是否是绝对链接，直接打开
      if (link.startsWith('http') || link.startsWith('https')) {
        window.open(link, '_blank');
      } else {
        // 否则，假设是相对链接，跳转到该路径
        window.location.href = link;
      }
    }
  };
</script>
