<template>
  <div class="app-container">
    <!-- 面板切换 -->
    <div class="tabs-row">
      <div class="tabs-panel fixed-controls">
        <button
          v-for="panel in panels"
          :key="panel.name"
          :class="{
            active:
              visiblePanels.includes(panel.name) && lockedPanel !== panel.name,
            locked:
              lockedPanel === panel.name && visiblePanels.includes(panel.name),
          }"
          @mousedown="startLongPress(panel.name)"
          @mouseup="cancelLongPress(panel.name)"
        >
          {{ panel.label }}
        </button>
      </div>
    </div>
    <div class="content-row">
      <!-- 内容区域 -->
      <div
        class="content-container"
        :class="{ haslocked: lockedPanel !== null }"
      >
        <div
          v-for="panel in visiblePanels"
          :key="panel"
          :class="{
            panel: panel !== 'review' || lockedPanel === panel,
            panellocked: lockedPanel === panel,
            panelrst: panel === 'review' && lockedPanel !== panel,
          }"
        >
          <!-- PDF 面板 -->
          <div v-if="panel === 'pdf'" class="panel-content">
            <DocumentViewer
              v-if="pdfFile"
              :file="pdfFile"
              :jumpData="jumpData"
              :findMatchingContent="findMatchingContent"
              @jump-to-content="handleJumpToContent"
              @jump-to-page="handleJumpToPage"
            />
          </div>

          <!-- OCR 结果面板 -->
          <div v-else-if="panel === 'ocr'" class="panel-content">
            <OCRContent
              v-if="ocrData.length > 0"
              ref="ocrContentRef"
              :ocrData="ocrData"
              :selectedContent="selectedContent"
              :selectedCells="selectedCells"
              @jump-to-page="handleJumpToPage"
              @update-selected-content="updateSelectedContent"
            />
          </div>

          <!-- 其他面板 -->
          <div v-else-if="panel === 'translation'" class="panel-content">
            <OCRContentCH
              v-if="ocrData.length > 0"
              ref="ocrContentCHRef"
              :ocrData="ocrData"
              :selectedCells="selectedCells"
              :selectedContent="selectedContent"
              @jump-to-page="handleJumpToPage"
              @update-selected-content="updateSelectedContent"
            />
          </div>
          <div v-else-if="panel === 'review'" class="panel-content">
            <ReviewTable
              ref="reviewRef"
              :review-groups="reviewGroups"
              @select-cells="updateSelectedContents"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
  import { nextTick, onMounted, ref } from 'vue';
  import DocumentViewer from './components/DocumentViewer.vue';
  import OCRContent from './components/rescomp/OCRContent.vue';
  import OCRContentCH from './components/chcomp/OCRContentCH.vue';
  import ReviewTable from './components/reviewcomp/ReviewResultTable.vue';
  import { useRoute } from 'vue-router';
  import { useFileStore } from '/@/views/pdfanalyze/mco/stores/fileStore.js';
  import pdfPath from '/@/assets/sample2.pdf';
  import jsonData from '/@/assets/sample2.json';
  import {
    getJson,
    getPDF,
  } from '/@/views/pdfanalyze/mco/api/mcofile/pdfFile.js';

  const pdfFile = ref(null); // 存储上传的 PDF 文件路径
  const ocrData = ref([]); // 用于存储加载的 JSON 数据
  const reviewGroups = ref([]); // 用于存储加载的 JSON 数据
  const pageIndex = ref({}); // 页码索引
  const jumpData = ref(null);
  const selectedContent = ref(null);
  const selectedCells = ref([]);
  const ocrContentRef = ref(null);
  const ocrContentCHRef = ref(null);
  const reviewRef = ref(null);
  let uniqueId = 0; // 自增 id 初始化
  const route = useRoute();
  const fileStore = useFileStore();
  const reviewId = fileStore.fileId;

  // 定义所有 Panel 的信息
  const panels = [
    { name: 'pdf', label: 'PDF' },
    { name: 'ocr', label: 'OCR 结果' },
  ];

  const loadData = async () => {
    try {
      console.log('reviewid', reviewId);
      if (!reviewId) throw new Error('缺少文件 ID 参数');
      const response = await getPDF(reviewId);
      pdfFile.value = response.data;
      console.log('pdfresponse', response);
      console.log('*****');
      const responsejs = await getJson(reviewId);
      console.log('#####');
      ocrData.value = responsejs.data.pages;
      addUniqueIdToData(responsejs.data.pages);
      pageIndex.value = buildPageIndex(responsejs.data.pages);
    } catch (error) {
      console.error('加载数据失败:', error);
    }
  };
  // 默认显示的 Panel，至少显示两个
  const visiblePanels = ref(['pdf', 'ocr']);

  // 当前锁定的面板
  const lockedPanel = ref(null);
  const lockedButton = ref(null);

  // 切换 Panel 显示/隐藏逻辑
  function togglePanel(panelName) {
    const index = visiblePanels.value.indexOf(panelName);
    if (index > -1 && visiblePanels.value.length > 2) {
      // 如果已经显示并且剩余 Panel 多于两个，则移除
      visiblePanels.value.splice(index, 1);
      if (lockedPanel.value === panelName) {
        lockedPanel.value = null;
      }
    } else if (index === -1) {
      // 如果未显示且总面板数小于5，则添加该面板
      if (visiblePanels.value.length < 5) {
        visiblePanels.value.push(panelName);
      }
    }
  }
  let clickStartTime = 0; // 记录点击开始的时间
  // 长按事件处理
  let longPressTimer = null;
  function startLongPress(panelName) {
    // 记录点击开始的时间
    clickStartTime = Date.now();
    // 在按钮按下时开始计时
    longPressTimer = setTimeout(() => {
      if (lockedPanel.value === panelName) {
        lockedPanel.value = null;
      } else {
        const index = visiblePanels.value.indexOf(panelName);
        if (index === -1) {
          visiblePanels.value.push(panelName);
        }
        lockedPanel.value = panelName;
      }
    }, 1000); // 设置为1秒钟长按
  }

  function cancelLongPress(panelName) {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
    }
    // 判断点击时间差，如果不超过 1 秒则执行 togglePanel
    const clickDuration = Date.now() - clickStartTime;
    if (clickDuration < 1000) {
      togglePanel(panelName); // 点击时长不超过 1 秒，执行切换面板
    }
    // 如果长按被取消，清除定时器
    clearTimeout(longPressTimer);
  }

  function addUniqueIdToData(data) {
    data.forEach((element) => {
      element.id = uniqueId++; // 为每个 content 分配一个唯一的 id
      if (element.type === 'Table') {
        element.value.forEach((cell) => {
          cell.id = uniqueId++;
        });
      }
    });
  }

  function handleFileUpload(type, event) {
    const file = event.target.files[0];
    if (!file) return;

    if (type === 'pdf') {
      pdfFile.value = URL.createObjectURL(file);
    } else if (type === 'json') {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const data = JSON.parse(e.target.result);
          ocrData.value = data;
          addUniqueIdToData(data);
          pageIndex.value = buildPageIndex(data);
        } catch (error) {
          console.error('Error parsing JSON file:', error);
        }
      };
      reader.readAsText(file);
    }
  }

  function buildPageIndex(data) {
    const index = {};
    data.forEach((section) => {
      const pagesection = section.page;
      if (!index[pagesection]) index[pagesection] = [];
      index[pagesection].push(section);
      section.contents[0]?.elements.forEach((item) => {
        const page = item.page;
        if (!index[page]) index[page] = [];
        index[page].push(item);
      });
    });
    return index;
  }

  function handleJumpToPage(data) {
    jumpData.value = data;
    console.log('contentqw1', data);
    nextTick(() => {
      const ocrindex = visiblePanels.value.indexOf('ocr');
      const translationindex = visiblePanels.value.indexOf('translation');
      const reviewindex = visiblePanels.value.indexOf('review');
      if (
        ocrindex > -1 &&
        ocrContentRef.value &&
        ocrContentRef.value[0].scrollToSelectedContent
      ) {
        ocrContentRef.value[0].scrollToSelectedContent();
      }
      if (
        translationindex > -1 &&
        ocrContentCHRef.value &&
        ocrContentCHRef.value[0].scrollToSelectedContent
      ) {
        ocrContentCHRef.value[0].scrollToSelectedContent();
      }
      if (
        reviewindex > -1 &&
        reviewRef.value &&
        reviewRef.value[0].scrollToSelectedContent
      ) {
        reviewRef.value[0].scrollToSelectedContent(data);
      }
    });
  }
  function handleJumpToContent(content) {
    console.log('contentqw2', content);
    selectedContent.value = content;
    const ocrindex = visiblePanels.value.indexOf('ocr');
    const translationindex = visiblePanels.value.indexOf('translation');
    const reviewindex = visiblePanels.value.indexOf('review');
    if (
      ocrindex > -1 &&
      ocrContentRef.value &&
      ocrContentRef.value[0].scrollToSelectedContent
    ) {
      ocrContentRef.value[0].scrollToSelectedContent();
    }
    if (
      translationindex > -1 &&
      ocrContentCHRef.value &&
      ocrContentCHRef.value[0].scrollToSelectedContent
    ) {
      ocrContentCHRef.value[0].scrollToSelectedContent();
    }
    if (
      reviewindex > -1 &&
      reviewRef.value &&
      reviewRef.value[0].scrollToSelectedContent
    ) {
      reviewRef.value[0].scrollToSelectedContent();
    }
  }

  function findMatchingContent(page, clickPoint) {
    const contents = pageIndex.value[page];
    console.log('content', contents);
    if (!contents) return null;
    return contents.find((content) =>
      isPointInPolygon(clickPoint, content.polygon),
    );
  }

  function isPointInPolygon(point, polygon) {
    if (!polygon) { return false; }
    polygon = validatePolygonData(polygon);
    const { x, y } = point;
    let isInside = false;

    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i][0],
        yi = polygon[i][1];
      const xj = polygon[j][0],
        yj = polygon[j][1];
      const intersect =
        yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
      if (intersect) isInside = !isInside;
    }
    return isInside;
  }

  function validatePolygonData(polygon) {
    if (polygon && Array.isArray(polygon) && typeof polygon[0] === 'number') {
      if (polygon.length === 4) {
        const [x1, y1, x2, y2] = polygon;
        return [
          [x1, y1],
          [x2, y1],
          [x2, y2],
          [x1, y2],
        ];
      } else {
        const groupedPolygon = [];
        for (let i = 0; i < polygon.length; i += 2) {
          groupedPolygon.push([polygon[i], polygon[i + 1]]);
        }
        return groupedPolygon;
      }
    }
    return polygon;
  }

  function updateSelectedContent(content) {
    console.log('lm here', content);
    selectedContent.value = content;
    selectedCells.value = [];
  }

  function updateSelectedContents(record) {
    if (record.element_type === 'cell') {
      selectedCells.value = [...record.element_ids];
      selectedContent.value = null;

    } else {
      const fitboy = findMatchingObject(ocrData, record);
      if (fitboy) {
        updateSelectedContent(fitboy);
        handleJumpToContent(fitboy);
      }
      handleJumpToPage({
        page: fitboy.page,
        polygon: fitboy.polygon,
      });
    }
    console.log('record.element_ids', selectedCells.value);
  }

  onMounted(() => {
    loadData();
  });

  function findMatchingObject(json, record, maxDepth = 100) {
    let result = null;
    const visited = new WeakSet();

    function recursiveSearch(node, depth = 0) {
      if (depth > maxDepth) {
        console.warn('Exceeded max recursion depth');
        return; // 超过最大深度时停止递归
      }

      if (typeof node === 'object' && node !== null) {
        if (visited.has(node)) {
          return; // 如果已经访问过该节点，直接返回
        }

        visited.add(node);

        if (Array.isArray(node)) {
          for (const item of node) {
            if (
              item.id === record.element_ids[0] &&
              (record.element_type.toLowerCase() === 'page' ||
                item.type.toLowerCase() === record.element_type.toLowerCase())
            ) {
              result = item;
              return;
            }
            recursiveSearch(item, depth + 1); // 继续遍历，增加深度
          }
        } else {
          if (
            node.id === record.element_ids[0] &&
            node.type.toLowerCase() === record.element_type.toLowerCase()
          ) {
            result = node;
            return;
          }
          for (const key in node) {
            if (node.hasOwnProperty(key)) {
              recursiveSearch(node[key], depth + 1);
            }
          }
        }
      }
    }

    recursiveSearch(json);
    return result;
  }
</script>

<style scoped>
  .app-container {
    display: flex;
    flex-direction: column;
    height: 80vh; /* 或根据需要调整 */
    box-sizing: border-box; /* 确保内边距计算在内 */
    padding: 10px;
  }

  .upload-panel {
    padding: 10px;
    background-color: #f5f5f5;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .tabs-panel {
    display: flex;
    align-items: center; /* 垂直居中内容 */
    gap: 10px; /* 按钮之间的间距 */
    height: 50px; /* 固定高度 */
    flex-shrink: 0; /* 防止其缩小 */
    border-bottom: 1px solid #ddd; /* 可选：分隔线 */
  }

  .tabs-panel button {
    padding: 5px 10px;
    cursor: pointer;
    border: none;
    background-color: #f0f0f0;
    border-radius: 5px;
  }

  .tabs-panel button.active {
    background-color: #007bff;
    color: white;
  }

  .content-container {
    display: flex;
    flex: 1; /* 自动占据剩余空间 */
    gap: 10px; /* 子元素之间的间距 */
    overflow-y: hidden; /* 防止子面板超出容器 */
    overflow-x: scroll;
  }

  .tabs-row {
    display: flex;
    flex-shrink: 0; /* 防止被挤压 */
    height: 50px; /* 固定高度 */
    border-bottom: 1px solid #ddd; /* 可选：分隔线 */
    background-color: #f8f8f8; /* 可选：背景色 */
    align-items: center; /* 垂直居中内容 */
    padding: 0 10px; /* 增加左右内边距 */
    box-sizing: border-box; /* 包含内边距 */
  }

  .content-row {
    display: flex;
    flex: 1; /* 占据剩余空间 */
    overflow: hidden; /* 防止溢出 */
  }

  .panel {
    flex: 1; /* 每个面板均分容器空间 */
    display: flex;
    overflow: auto; /* 防止内容溢出 */
    border: 1px solid #ddd; /* 可选：添加边框以便调试布局 */
    padding: 10px; /* 可选：内边距 */
    min-width: 40vw;
  }

  .panelrst {
    min-width: 60vw;
    overflow: auto; /* 防止内容溢出 */
  }

  .panel-review {
    min-width: 80vw;
  }

  .panel-content {
    flex: 1;
  }

  .fixed-controls {
    position: relative;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #f8f9fa;
    padding: 10px;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.2);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
  }

  .panellocked {
    height: 70vh;
    position: absolute;
    left: 0;
    width: 40vw; /* 你可以根据需要调整宽度 */
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.3);
    background-color: #fff;
    z-index: 10;
  }

  .haslocked {
    padding-left: 40vw;
  }

  button.locked {
    background-color: #f1c40f; /* 给锁定按钮一个视觉反馈 */
  }

  button.active {
    background-color: #3498db;
  }
</style>
