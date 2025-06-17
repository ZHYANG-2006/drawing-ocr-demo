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
        :style="leftOffsetStyles(lockedPanel)"
      >
        <div
          v-for="panel in visiblePanels"
          :key="panel"
          :class="{
            panel: panel !== 'review' || lockedPanel === panel,
            panellocked: lockedPanel === panel,
            panelrst: panel === 'review' && lockedPanel !== panel,
          }"
          :style="panelStyles(panel)"
        >
          <!-- 拖拽句柄（右侧） -->
          <div v-if="lockedPanel === panel" class="resizer resizer-right" @mousedown="(event) => initResize('width', event)"></div>
          <!-- 拖拽句柄（下方） -->
          <div v-if="lockedPanel === panel" class="resizer resizer-bottom" @mousedown="(event) => initResize('height', event)"></div>
          <!-- PDF 面板 -->
          <div v-if="panel === 'pdf'" class="panel-content">
            <DocumentViewer
              v-if="pdfFile"
              :file="pdfFile"
              :jumpData="jumpData"
              :jumpDatas="jumpDatas"
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
          <div v-else-if="panel === 'translationTHI'" class="panel-content">
            <OCRContentTHI
              v-if="ocrData.length > 0"
              ref="ocrContentTHIRef"
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
  import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
  import DocumentViewer from './components/DocumentViewer.vue';
  import OCRContent from './components/rescomp/OCRContent.vue';
  import OCRContentCH from './components/chcomp/OCRContentCH.vue';
  import OCRContentTHI from './components/thicomp/OCRContentTHI.vue';
  import ReviewTable from './components/reviewcomp/ReviewResultTable.vue';
  import { useRoute } from 'vue-router';
  import { useFileStore } from '/@/views/pdfanalyze/cppqcp/stores/fileStore.js';
  import {
    getJson,
    getPDF,
  } from '/@/views/pdfanalyze/cppqcp/api/viewer/viewer.js';

  const pdfFile = ref(null); // 存储上传的 PDF 文件路径
  const ocrData = ref([]); // 用于存储加载的 JSON 数据
  const reviewGroups = ref([]); // 用于存储加载的 JSON 数据
  const pageIndex = ref({}); // 页码索引
  const jumpData = ref(null);
  const jumpDatas = ref([]);
  const selectedContent = ref(null);
  const selectedCells = ref([]);
  const ocrContentRef = ref(null);
  const ocrContentCHRef = ref(null);
  const ocrContentTHIRef = ref(null);
  const reviewRef = ref(null);
  let uniqueId = 0; // 自增 id 初始化
  const route = useRoute();
  const fileStore = useFileStore();
  const reviewId = fileStore.fileId;

  // 定义所有 Panel 的信息
  const panels = [
    { name: 'review', label: 'review' },
    { name: 'ocr', label: 'OCR 结果' },
    { name: 'translation', label: 'OCR 翻译' },
    { name: 'translationTHI', label: 'การแปลภาษาไทย' },
    { name: 'pdf', label: 'PDF' },
  ];

  // 锁定面板的宽度和高度（像素）
  const lockedPanelWidth = ref(40); // 初始宽度为30vw
  const lockedPanelHeight = ref(80); // 初始高度为50vh

  const loadData = async () => {
    try {
      console.log('reviewid', reviewId);
      if (!reviewId) throw new Error('缺少文件 ID 参数');
      const response = await getPDF(reviewId);
      pdfFile.value = response.data;
      console.log('pdfresponse', response);
      const responsejs = await getJson(reviewId);
      ocrData.value = responsejs.data.sections;
      addUniqueIdToData(responsejs.data.sections);
      pageIndex.value = buildPageIndex(responsejs.data.sections);
      reviewGroups.value = responsejs.data.review_groups;
      console.log('reviewGroups111111111111', reviewGroups.value);
    } catch (error) {
      console.error('加载数据失败:', error);
    }
  };

  // 默认显示的 Panel，至少显示两个
  const visiblePanels = ref(['review', 'ocr', 'pdf']);

  // 当前锁定的面板
  const lockedPanel = ref('review');
  const lockedButton = ref('review');

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
    data.forEach((section) => {
      section.contents.forEach((content) => {
        content.index = uniqueId++; // 为每个 content 分配一个唯一的 id
      });
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
      const translationTHIindex = visiblePanels.value.indexOf('translationTHI');
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
        translationTHIindex > -1 &&
        ocrContentTHIRef.value &&
        ocrContentTHIRef.value[0].scrollToSelectedContent
      ) {
        ocrContentTHIRef.value[0].scrollToSelectedContent();
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
    const translationTHIindex = visiblePanels.value.indexOf('translationTHI');
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
      translationindex > -1 &&
      ocrContentTHIRef.value &&
      ocrContentTHIRef.value[0].scrollToSelectedContent
    ) {
      ocrContentTHIRef.value[0].scrollToSelectedContent();
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
    if (!contents) return null;
    return contents.find((content) =>
      isPointInPolygon(clickPoint, content.polygon),
    );
  }

  function isPointInPolygon(point, polygon) {
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
    const savedWidth = localStorage.getItem('lockedPanelWidth');
    const savedHeight = localStorage.getItem('lockedPanelHeight');
    if (savedWidth) {
      lockedPanelWidth.value = parseFloat(savedWidth);
    }
    if (savedHeight) {
      lockedPanelHeight.value = parseFloat(savedHeight);
    }

    // 初始化 CSS 变量
    document.documentElement.style.setProperty('--locked-panel-width', `${lockedPanelWidth.value}px`);
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
              (record.element_type.toLowerCase() === 'section' ||
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

  // 监听 lockedPanelWidth 的变化，将其应用到主内容区域的左边距
  watch(lockedPanelWidth, (newWidth) => {
    document.documentElement.style.setProperty('--locked-panel-width', `${newWidth}px`);
  });

  // 拖拽相关变量
  const isResizingWidth = ref(false);
  const isResizingHeight = ref(false);
  const startX = ref(0);
  const startY = ref(0);
  const startWidth = ref(lockedPanelWidth.value);
  const startHeight = ref(lockedPanelHeight.value);

  // 拖拽开始
  function initResize(type) {
    console.log('initResize called with type:', type);
    event.preventDefault();
    if (type === 'width') {
      console.log('Resizing width started');
      isResizingWidth.value = true;
      startX.value = event.clientX;
      startWidth.value = lockedPanelWidth.value;
    } else if (type === 'height') {
      console.log('Resizing height started');
      isResizingHeight.value = true;
      startY.value = event.clientY;
      startHeight.value = lockedPanelHeight.value;
    }

    // 添加全局事件监听器
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', stopResize);
  }
  const minWidthVw = 40; // 最小宽度为20vw
  const maxWidthVw = 90; // 最大宽度为50vw
  const minHeightVh = 80; // 最小高度为20vh
  const maxHeightVh = 90; // 最大高度为80vh
  // 函数：将像素值转换为 `vw`
  const pxToVw = (px) => (px / window.innerWidth) * 100;

  // 函数：将像素值转换为 `vh`
  const pxToVh = (px) => (px / window.innerHeight) * 100;
  // 拖拽过程中
  function onMouseMove(event) {
    console.log(
      'onMouseMove called with isResizingWidth:',
      isResizingWidth.value,
      'isResizingHeight:',
      isResizingHeight.value
    );

    if (isResizingWidth.value) {
      const dx = event.clientX - startX.value;
      const deltaVw = pxToVw(dx);
      let newWidth = startWidth.value + deltaVw;

      // 应用最小和最大宽度限制
      if (newWidth < minWidthVw) newWidth = minWidthVw;
      if (newWidth > maxWidthVw) newWidth = maxWidthVw;

      lockedPanelWidth.value = newWidth;
      console.log(`Resizing Width: ${newWidth}vw`);
    }

    if (isResizingHeight.value) {
      const dy = event.clientY - startY.value;
      const deltaVh = pxToVh(dy);
      let newHeight = startHeight.value + deltaVh;

      // 应用最小和最大高度限制
      if (newHeight < minHeightVh) newHeight = minHeightVh;
      if (newHeight > maxHeightVh) newHeight = maxHeightVh;

      lockedPanelHeight.value = newHeight;
      console.log(`Resizing Height: ${newHeight}vh`);
    }
  }

  // 拖拽结束
  function stopResize() {
    if (isResizingWidth.value || isResizingHeight.value) {
      isResizingWidth.value = false;
      isResizingHeight.value = false;

      // 移除全局事件监听器
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', stopResize);
    }
  }

  const panelStyles = (panel) => {
    return lockedPanel.value === panel
      ? {
        width: `${lockedPanelWidth.value}vw`,
        height: `${lockedPanelHeight.value}vh`,
      }
      : {};
  };

  const leftOffsetStyles = (panel) => {
    return panel !== null
      ? {
        paddingLeft: `${lockedPanelWidth.value}vw`,
      }
      : {paddingLeft: `10px`};
  };

  // 清理事件监听器
  onBeforeUnmount(() => {
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', stopResize);
  });
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
    position: absolute;
    top: 50px; /* 高度与 tabs-row 一致 */
    left: 0;
    background-color: #fff;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    overflow: hidden;
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

  .resizer {
    position: absolute;
    background-color: rgba(0, 0, 0, 0.1); /* 临时可见的背景颜色 */
    z-index: 10;
  }

  .resizer-right {
    top: 0;
    right: 0;
    width: 15px;
    height: 100%;
    cursor: ew-resize;
    z-index: 1001;
  }

  .resizer-right:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }

  .resizer-bottom {
    bottom: 0;
    left: 0;
    width: 100%;
    height: 15px;
    cursor: ns-resize;
    z-index: 1001;
  }

  .resizer-bottom:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }
</style>
