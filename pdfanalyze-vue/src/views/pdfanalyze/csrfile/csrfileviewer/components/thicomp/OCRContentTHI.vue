<template>
  <div ref="containerRef" class="ocr-content">
    <h2>การแปลภาษาไทย</h2>
    <div
      v-for="section in ocrData"
      :id="`section-${section.type}-${section.id}`"
      :key="`section-${section.type}-${section.id}`"
      class="ocr-section"
    >
      <h3
        :id="`contentthi-${section.type}-${section.id}`"
        :key="`contentthi-${section.type}-${section.id}`"
        :class="{ 'selected-frame': isSelectedContent(section) }"
        @click="handleContentClick(section)"
      >
        {{
          section.has_strike_through || section.has_xbar
            ? section.true_thai_value
            : section.thai_value || ''
        }}
      </h3>
      <div
        v-for="content in section.contents[0]?.elements"
        :id="`contentthi-${section.type}-${content.id}`"
        :key="`contentthi-${section.type}-${content.id}`"
        :class="{ 'selected-frame': isSelectedContent(content) }"
        class="ocr-item"
        @click="handleContentClick(content)"
      >
        <component
          :is="getComponent(content.type)"
          :content="content"
          :is-selected="isSelectedContent(content)"
          @jump-to-page="handleJumpToPage"
          @update-selected="handleContentClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, defineProps, defineEmits } from 'vue';
  import OCRParagraph from './OCRParagraphTHI.vue';
  import OCRTable from './OCRTableTHI.vue';
  import OCRImage from './OCRImageTHI.vue';

  const props = defineProps({
    ocrData: Array,
    selectedContent: Object, // 用于接收外部传入的选中项
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
    emit('update-selected-content', content);
    handleJumpToPage({
      page: content.page,
      polygon: content.polygon,
      review_group_id: content.review_group_id,
    }); // 自动调用跳转
  }

  function isSelectedContent(content) {
    return props.selectedContent === content;
  }

  // 添加滚动到指定内容的方法
  function scrollToSelectedContent() {
    if (props.selectedContent) {
      const element = document.getElementById(
        `contentthi-${props.selectedContent.type}-${props.selectedContent.id}`,
      );

      if (element && containerRef.value) {

        // 获取容器的可视高度
        const containerHeight = containerRef.value.clientHeight;

        // 计算滚动位置，目标元素出现在中央
        const scrollTop =
          element.offsetTop - containerHeight / 2 + element.clientHeight / 2;
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
    font-family: 'Arial', 'Helvetica', 'sans-serif', 'Sarabun', 'Thai Sans';
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
