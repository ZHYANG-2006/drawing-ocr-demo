<template>
  <div ref="pdfContainer" class="pdf-viewer" @mousedown="startDragging">
    <canvas ref="pdfCanvas" class="pdf-canvas"></canvas>
    <canvas ref="overlayCanvas" class="overlay-canvas"></canvas>
  </div>
  <div class="controls fixed-controls">
    <button :disabled="scale <= minScale" @click="zoomOut">缩小</button>
    <button @click="zoomIn">放大</button>
    <button :disabled="currentPage <= 1" @click="prevPage">上一页</button>
    <span>第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
    <button :disabled="currentPage >= totalPages" @click="nextPage">
      下一页
    </button>
    <input
      v-model.number="jumpPage"
      type="number"
      min="1"
      :max="totalPages"
      placeholder="页码"
    />
    <button @click="goToPage">跳转</button>
  </div>
</template>

<script setup>
  import { ref, onMounted, onUnmounted, watch } from 'vue';
  import * as pdfjsLib from 'pdfjs-dist';

  // 设置 PDF.js Worker 路径
  pdfjsLib.GlobalWorkerOptions.workerSrc = './pdf.worker.min.mjs';

  const props = defineProps({
    file: {
      type: [String, Object], // 接受字符串路径或文件对象
      required: true,
    },
    jumpData: Object, // 用于接收跳转信息
    findMatchingContent: Function, // 接收来自 App.vue 的查找函数
  });

  const pdfContainer = ref(null);
  const pdfCanvas = ref(null);
  const overlayCanvas = ref(null);
  let pdfDoc = null; // 非响应式变量
  const currentPage = ref(1);
  const totalPages = ref(0);
  const scale = ref(1.5); // 默认缩放比例
  const minScale = 0.5; // 最小缩放比例
  const maxScale = 3; // 最大缩放比例
  const jumpPage = ref(''); // 跳转页面输入框的值

  // 拖动状态
  const isDragging = ref(false);
  const dragStart = ref({ x: 0, y: 0 });
  const scrollStart = ref({ x: 0, y: 0 });

  const emit = defineEmits(['jump-to-content', 'jump-to-page']);

  function handlePdfClick(event) {
    const rect = pdfCanvas.value.getBoundingClientRect();
    const x = (event.clientX - rect.left) / scale.value;
    const y = (event.clientY - rect.top) / scale.value;
    const page = currentPage.value;
    console.log(`clicked point: (${x}, ${y})`);

    // 使用坐标查找匹配的 OCR 内容
    const matchingContent = props.findMatchingContent(currentPage.value, {
      x,
      y,
    });
    if (matchingContent) {
      emit('jump-to-content', matchingContent);
      emit('jump-to-page', {
        page: matchingContent.page,
        polygon: matchingContent.polygon,
      });
    }
  }

  const startDragging = (event) => {
    isDragging.value = true;
    dragStart.value = { x: event.clientX, y: event.clientY };
    scrollStart.value = {
      x: pdfContainer.value.scrollLeft,
      y: pdfContainer.value.scrollTop,
    };

    // 添加鼠标移动和松开事件
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', stopDragging);
  };

  const stopDragging = () => {
    isDragging.value = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', stopDragging);
  };

  const handleMouseMove = (event) => {
    if (!isDragging.value) return;

    const deltaX = event.clientX - dragStart.value.x;
    const deltaY = event.clientY - dragStart.value.y;

    // 更新 pdfContainer 的滚动位置
    pdfContainer.value.scrollLeft = scrollStart.value.x - deltaX;
    pdfContainer.value.scrollTop = scrollStart.value.y - deltaY;
  };
  let renderTask = null;
  // 渲染指定页码的内容
  const renderPage = async (pageNum, polygon = null) => {
    try {
      if (!pdfDoc) return;

      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale: scale.value });
      const canvas = pdfCanvas.value;
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      const context = canvas.getContext('2d');

      // 取消上一个渲染任务，如果还在进行
      if (renderTask) {
        renderTask.cancel();
      }

      // 开始新的渲染任务
      renderTask = page.render({ canvasContext: context, viewport });
      await renderTask.promise; // 等待渲染完成
      renderTask = null;

      // 设置 overlayCanvas 尺寸
      overlayCanvas.value.width = viewport.width;
      overlayCanvas.value.height = viewport.height;
      overlayCanvas.value.style.position = 'absolute';
      overlayCanvas.value.style.zIndex = '10'; // 提升 z-index 确保在 PDF 之上
      overlayCanvas.value.style.border = '1px solid green'; // 添加边框来检查是否覆盖正确
      polygon = validatePolygonData(polygon);
      // 如果有 polygon 信息，绘制标记并滚动到指定位置
      if (polygon) {
        drawPolygon(polygon, viewport);
        scrollToPolygon(polygon, viewport);
      } else {
        clearOverlay(); // 清除先前的标记
      }
    } catch (error) {
      // 检查是否是 RenderingCancelledException 异常
      if (error.name === 'RenderingCancelledException') {
        // 忽略该异常并继续新渲染任务
        console.log(`Rendering cancelled: ${error.message}`);
      } else {
        // 处理其他渲染错误
        console.error('Error rendering page:', error);
      }
    }
  };

  function validatePolygonData(polygon) {
    // 将平铺数组转换为二维数组
    if (polygon && Array.isArray(polygon) && typeof polygon[0] === 'number') {
      if (polygon.length === 4) {
        // 提取四个数值并创建一个矩形
        const [x1, y1, x2, y2] = polygon;
        const groupedPolygon = [
          [x1, y1], // 左上角
          [x2, y1], // 右上角
          [x2, y2], // 右下角
          [x1, y2], // 左下角
        ];
        return groupedPolygon;
      } else {
        // 原先逻辑: 将数组以 2 为单位分组
        const groupedPolygon = [];
        for (let i = 0; i < polygon.length; i += 2) {
          groupedPolygon.push([polygon[i], polygon[i + 1]]);
        }
        return groupedPolygon;
      }
    }
    return polygon;
  }

  function applyTransform(x, y, transform) {
    const [a, b, c, d, e, f] = transform;
    const det = a * d - b * c;
    if (det === 0) return { x: NaN, y: NaN }; // 无法求逆矩阵

    // 计算逆矩阵
    const a_inv = d / det;
    const b_inv = -b / det;
    const c_inv = -c / det;
    const d_inv = a / det;
    const e_inv = (c * f - d * e) / det;
    const f_inv = (b * e - a * f) / det;

    // 应用逆矩阵
    return {
      x: a_inv * x + c_inv * y + e_inv,
      y: b_inv * x + d_inv * y + f_inv,
    };
  }

  // 在 overlayCanvas 上绘制多边形标记
  function drawPolygon(polygon, viewport) {
    const ctx = overlayCanvas.value.getContext('2d');
    ctx.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height);

    ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
    ctx.beginPath();

    const [scaleX, , , scaleY, offsetX, offsetY] = viewport.transform;

    polygon.forEach(([xRaw, yRaw], index) => {
      // 应用缩放和偏移，将 Y 轴翻转基于 Canvas 高度
      const x = xRaw * scaleX + offsetX;
      const y = -viewport.height + (yRaw * Math.abs(scaleY) + offsetY);

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.closePath();
    ctx.fill();
  }

  function scrollToPolygon(polygon, viewport) {
    const [scaleX, , , scaleY, offsetX, offsetY] = viewport.transform;

    // 使用 polygon 的第一个点进行定位
    const [xRaw, yRaw] = polygon[0];

    // 转换点的位置和方向
    const scrollX =
      xRaw * scaleX + offsetX - pdfContainer.value.clientWidth / 2;
    const scrollY =
      -viewport.height +
      (yRaw * Math.abs(scaleY) + offsetY) -
      pdfContainer.value.clientHeight / 2; // 上下翻转的 y

    pdfContainer.value.scrollTo(scrollX, scrollY);
  }

  // 清除 overlayCanvas 上的标记
  function clearOverlay() {
    const ctx = overlayCanvas.value.getContext('2d');
    ctx.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height);
  }

  // 页面跳转方法
  const goToPage = () => {
    if (jumpPage.value > 0 && jumpPage.value <= totalPages.value) {
      currentPage.value = jumpPage.value;
      renderPage(currentPage.value);
    } else {
      alert(`请输入 1 到 ${totalPages.value} 之间的页码`);
    }
  };

  // 放大页面
  const zoomIn = () => {
    if (scale.value < maxScale) {
      scale.value += 0.5;
      renderPage(currentPage.value);
    }
  };

  // 缩小页面
  const zoomOut = () => {
    if (scale.value > minScale) {
      scale.value -= 0.5;
      renderPage(currentPage.value);
    }
  };

  // 下一页
  const nextPage = () => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++;
      renderPage(currentPage.value);
    }
  };

  // 上一页
  const prevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--;
      renderPage(currentPage.value);
    }
  };

  // 初始化 PDF 文档
  onMounted(async () => {
    const pdfFile = props.file;
    // 添加到 DocumentViewer.vue
    if (pdfCanvas.value) {
      pdfCanvas.value.addEventListener('click', handlePdfClick);
    }
    try {
      const pdfData = await pdfFile.arrayBuffer();
      pdfDoc = await pdfjsLib.getDocument({ data: pdfData }).promise;
      totalPages.value = pdfDoc.numPages;
      renderPage(currentPage.value);
    } catch (error) {
      console.error('Error loading PDF:', error);
    }
  });

  onUnmounted(() => {
    if (pdfCanvas.value) {
      pdfCanvas.value.removeEventListener('click', handlePdfClick);
    }
  });

  // 监听 jumpData 改变并重新渲染页面和标记
  watch(
    () => props.jumpData,
    (newData) => {
      if (newData) {
        currentPage.value = newData.page;
        renderPage(newData.page, newData.polygon);
      }
    },
  );
</script>

<style scoped>
  .pdf-viewer {
    position: relative;
    width: 100%;
    height: calc(100% - 60px);
    overflow: auto;
    cursor: grab;
  }

  .pdf-viewer:active {
    cursor: grabbing;
  }

  .pdf-canvas,
  .overlay-canvas {
    position: absolute;
    top: 0;
    left: 0;
  }

  .overlay-canvas {
    pointer-events: none;
    z-index: 10;
  }

  .controls {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 10px;
  }

  .fixed-controls {
    position: relative;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #f8f9fa;
    padding: 10px;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.2);
    height: 50px;
    justify-content: center;
    align-items: center;
    z-index: 9;
  }

  button,
  input[type='number'] {
    margin: 0 5px;
  }

  input[type='number'] {
    width: 60px;
    padding: 5px;
    text-align: center;
  }

  button {
    margin: 0 5px;
  }
</style>
