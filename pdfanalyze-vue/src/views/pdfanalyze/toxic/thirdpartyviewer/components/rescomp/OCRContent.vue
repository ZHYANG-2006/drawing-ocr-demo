<template>
  <div ref="containerRef" class="ocr-content">
    <h2>OCR 识别结果</h2>
    <div
      v-for="section in ocrData"
      :id="`section-0`"
      :key="`section-0`"
      class="ocr-section"
    >
      <div
        v-for="element in section.content"
        :id="`content-${element.type}-${element.id}`"
        :key="`content-${element.type}-${element.id}`"
        :class="{ 'selected-frame': isSelectedContent(element) }"
        class="ocr-item"
        @click="handleContentClick(element)"
      >
        <component
          :is="getComponent(element.type)"
          :content="element"
          :selectedContent="props.selectedContent"
          :selected-cells="props.selectedCells"
          :is-selected="isSelectedContent(element)"
          @jump-to-page="handleJumpToPage"
          @update-selected="handleContentClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, defineProps, defineEmits, watch } from 'vue';
  import OCRParagraph from './OCRParagraph.vue';
  import OCRTable from './OCRTable.vue';
  import OCRImage from './OCRImage.vue';

  const props = defineProps({
    ocrData: Array,
    selectedContent: Object, // 用于接收外部传入的选中项
    selectedCells: Array,
  });
  const emit = defineEmits(['jump-to-page', 'update-selected-content']);

  function handleClick(section) {
    emit('jump-to-page', {
      page: section.page,
      polygon: section.polygon,
    });
  }

  const containerRef = ref(null); // 右侧容器引用

  function getComponent(type) {
    switch (type) {
      case 'Paragraph':
        return OCRParagraph;
      case 'Table':
        return OCRTable;
      case 'Image':
        return OCRImage;
      default:
        return null;
    }
  }

  function handleJumpToPage(data) {
    emit('jump-to-page', data);
  }

  function handleContentClick(content) {
    console.log('myucontent', props.selectedCells);
    emit('update-selected-content', content);
    handleJumpToPage({
      page: content.page,
      polygon: content.polygon,
    }); // 自动调用跳转
  }

  function isSelectedContent(content) {
    return props.selectedContent === content;
  }

  // 添加滚动到指定内容的方法
  function scrollToSelectedContent() {
    console.log('myselectedContent', props.selectedContent);
    if (props.selectedContent) {
      const element = document.getElementById(
        `content-${props.selectedContent.type}-${props.selectedContent.id}`,
      );
      if (element && containerRef.value) {

        // 获取容器的可视高度
        const containerHeight = containerRef.value.clientHeight;
        const containerScrollTop = containerRef.value.scrollTop;

        // 获取目标元素相对于视口的位置
        const rect = element.getBoundingClientRect();

        // 计算滚动位置，目标元素出现在中央
        // 获取目标元素相对于容器的位置，考虑容器的当前滚动位置
        const scrollTop = rect.top - containerHeight / 2 + rect.height / 2 + containerScrollTop;

        // 滚动至计算位置，平滑滚动
        containerRef.value.scrollTo({
          top: scrollTop,
          behavior: 'smooth',
        });
      }
    }
  }

  defineExpose({ scrollToSelectedContent });
</script>

<style scoped>
  .ocr-content {
    overflow-y: auto;
    height: 100%;
    padding: 0px;
  }
  .ocr-section {
    margin-bottom: 20px;
    padding: 10px;
    border-bottom: 1px solid #ddd;
  }
  .ocr-item {
    cursor: pointer;
    padding: 5px;
    border-radius: 5px;
  }
  .selected-frame {
    border: 2px solid blue; /* 高亮选中的表格框 */
  }
</style>
