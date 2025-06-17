<template>
  <div class="search-page" ref="wrapper">
    <!-- 搜索框 -->
    <div class="search-export-wrapper" style="display: flex; align-items: center; gap: 8px;">
      <input
        v-model="query"
        @input="onInput"
        class="search-box"
        placeholder="请输入搜索内容（使用空格分隔多关键词）..."
      />
      <button class="export-button" @click="exportResults">导出 Excel</button>
    </div>
    <!-- 表格显示区域 -->
    <div class="results-table-wrapper">
      <table class="results-table" v-if="results.length">
        <thead>
        <tr>
          <th style="width: 120px;">Items</th>
          <th>Upload Time</th>
          <th>DRAWING NUMBER</th>
          <th>REV</th>
          <th style="width: 230px;">TITLE</th>
          <th>Internal Code</th>
          <th>Project Description</th>
          <th>Flex Part Number</th>
          <th>Notes Number</th>
          <th style="width: 250px;">Description</th>
          <th style="width: 130px;">操作</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="item in results" :key="item.paragraph_id">
          <td>{{ item.paragraph_id }}</td>
<!--          <td>{{ item.drawing_number }}</td>-->
<!--          <td>{{ item.rev }}</td>-->
<!--          <td>{{ item.title }}</td>-->
<!--          <td>{{ item.num }}</td>-->
<!--          <td>{{ formatDate(item.create_datetime) }}</td>-->
          <!-- 高亮匹配部分 -->
          <td><div class="description-text" v-html="highlightText(formatDate(item.create_datetime), query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.drawing_number, query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.rev, query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.title, query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.internal_code, query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.project_description, query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.flex_part_number, query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.num, query)"></div></td>
          <td><div class="description-text" v-html="highlightText(item.text, query)"></div></td>
          <td>
              <span
                class="open-pdf"
                @click="handleStartReview(item.pdf_id)"
              >
                📄 打开 PDF
              </span>
<!--            &nbsp;|&nbsp;-->
<!--            <span-->
<!--              class="download-pdf"-->
<!--              @click="downloadPdf(item.pdf_id)"-->
<!--            >-->
<!--                ⬇ 下载 PDF-->
<!--              </span>-->
          </td>
        </tr>
        </tbody>
      </table>
      <!-- 无结果时的提示 -->
      <div v-else class="no-results">暂无搜索结果</div>
    </div>

    <!-- 加载中提示 -->
    <div v-if="loading" class="loading">加载中...</div>

    <!-- 分页操作栏 -->
    <div class="pagination-bar" v-if="totalPages > 1 && !loading">
      <button
        class="pagination-button"
        :disabled="page === 1"
        @click="prevPage"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ page }} 页 / 共 {{ totalPages }} 页
      </span>
      <button
        class="pagination-button"
        :disabled="page === totalPages"
        @click="nextPage"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
  import { ref, watch, onMounted } from "vue";
  import { useRouter } from "vue-router";
  import { message } from "ant-design-vue";
  import dayjs from 'dayjs';
  import debounce from 'lodash/debounce'
  import * as XLSX from "xlsx";

  // 你的后端请求方法
  import { getPara, downloadPDF, getFilterPara } from "/@/views/pdfanalyze/mco/api/mcosearch/paraSearcher.js";

  // 你的存储
  import { useFileStore } from "/@/views/pdfanalyze/mco/stores/fileStore.js";

  const fileStore = useFileStore();
  const router = useRouter();

  // 搜索相关
  const query = ref("");
  const results = ref([]);
  const loading = ref(false);

  // 分页相关
  const page = ref(1);
  const pageSize = 10;
  const totalPages = ref(1);

  function formatDate(datetimeStr) {
    // 传入字符串或日期对象都可以
    // dayjs会自动识别并解析
    return dayjs(datetimeStr).format('YYYY-MM-DD HH:mm:ss');
  }
  /**
   * 获取数据
   */
  async function fetchResults() {
    if (loading.value) return;
    loading.value = true;

    try {
      // 注意：需要你的后端 getPara 能支持传入 page 和 pageSize 参数
      // 如果后端不支持，请根据实际场景修改
      const response = await getPara(query.value, page.value, pageSize);
      // 设置列表与总页数
      results.value = response.data.results || [];
      totalPages.value = response.data.total_results
        ? Math.ceil(response.data.total_results / pageSize)
        : 1;
    } catch (err) {
      console.error("搜索接口出错：", err);
      message.error("搜索出错，请检查控制台日志");
    } finally {
      loading.value = false;
    }
  }

  async function exportResults() {
    try {
      // 用 getFilterPara 拉取所有数据（不分页）
      const resp = await getFilterPara(query.value);
      const data = resp.data.results || [];

      // 把 JSON 数组转成工作表
      const ws = XLSX.utils.json_to_sheet(data.map(item => ({
        Items: item.paragraph_id,
        "Upload Time": item.create_datetime,
        "DRAWING NUMBER": item.drawing_number,
        REV: item.rev,
        TITLE: item.title,
        "Internal Code": item.internal_code,
        "Project Description": item.project_description,
        "Flex Part Number": item.flex_part_number,
        "Notes Number": item.num,
        Description: item.text
      })));
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Results");

      // 生成二进制并触发下载
      const wbout = XLSX.write(wb, { bookType: "xlsx", type: "array" });
      const blob = new Blob([wbout], { type: "application/octet-stream" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "search_results.xlsx";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

    } catch (err) {
      console.error(err);
      message.error("导出失败，请检查控制台日志");
    }
  }

  const debouncedFetch = debounce(() => {
    page.value = 1
    fetchResults()
  }, 500)  // 500ms 没再输入才触发

  /**
   * 搜索框输入时回调
   * 重置页码为 1，并重新拉取数据
   */
  function onInput() {
    debouncedFetch();
  }

  const wrapper = ref(null)

  function scrollContainerToTop() {
    if (wrapper.value) {
      wrapper.value.scrollTop = 0  // 立即生效，忽略 CSS scroll‐behavior
    }
  }

  function prevPage() {
    if (page.value > 1) {
      page.value--
      nextTick(scrollContainerToTop)
    }
  }
  function nextPage() {
    if (page.value < totalPages.value) {
      page.value++
      nextTick(scrollContainerToTop)
    }
  }

  /**
   * 监听 page 变化，根据最新页面重新获取数据
   */
  watch(page, () => {
    fetchResults();
  });

  /**
   * 高亮关键词
   */
  function highlightText(text, queryStr) {
    if (!text) return "";

    // 如果 text 不是字符串，就转成字符串
    if (typeof text !== "string") {
      text = String(text);
    }

    if (!queryStr) return text;
    const terms = queryStr.trim().split(/\s+/).filter(Boolean);
    if (terms.length === 0) return text;
    const regex = new RegExp(`(${terms.join("|")})`, "gi");
    return text.replace(regex, '<mark>$1</mark>');
  }

  /**
   * 下载 PDF
   */
  async function downloadPdf(pdfId) {
    try {
      const resp = await downloadPDF(pdfId);
      const blob = await resp.data;

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `document_${pdfId}.pdf`; // 可根据后端的 filename 或自己定义
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("下载PDF出错：", error);
      message.error("下载PDF出错，请检查控制台日志");
    }
  }

  /**
   * 打开 PDF
   */
  function handleStartReview(id) {
    fileStore.setFileId(id);
    router.push({
      name: "mcoviewer", // 路由名称，与你的路由配置匹配
    });
  }

  /**
   * 组件初始化时，默认执行一次搜索
   * 如果不想默认加载，可以去掉
   */
  onMounted(() => {
    fetchResults();
  });
</script>

<style scoped>
  .search-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 90%;
    margin: 0 auto;
    padding: 1rem;
    font-family: "Arial", sans-serif;
  }

  .search-box {
    width: 100%;
    padding: 0.8rem 1rem;
    font-size: 1rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    outline: none;
    transition: border 0.3s;
  }

  .search-box:focus {
    border-color: #3498db;
    box-shadow: 0 0 8px rgba(52, 152, 219, 0.5);
  }

  /* 表格样式 */
  .results-table-wrapper {
    margin-top: 1rem;
    overflow-x: auto; /* 防止列太多时撑破布局，可根据需要保留或删除 */
  }

  .results-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    background-color: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .results-table thead {
    background-color: #f7f7f8;
  }

  .results-table th,
  .results-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #eaeaea;
  }

  /* 匹配不到时的提示 */
  .no-results {
    padding: 1rem;
    text-align: center;
    font-size: 1rem;
    color: #888;
  }

  mark {
    background: rgba(255, 223, 0, 0.5);
    padding: 2px 4px;
    border-radius: 3px;
    transition: background 0.3s;
  }

  /* 加载中样式 */
  .loading {
    text-align: center;
    padding: 1rem;
    font-size: 1.2rem;
    color: #555;
  }

  /* 操作区域 */
  .open-pdf,
  .download-pdf {
    cursor: pointer;
    color: #007bff;
    text-decoration: underline;
    font-weight: normal;
  }
  .open-pdf:hover,
  .download-pdf:hover {
    color: #0056b3;
  }

  /* 分页栏 */
  .pagination-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 1rem;
  }

  .pagination-button {
    background: #3498db;
    border: none;
    color: #fff;
    font-size: 0.9rem;
    padding: 0.6rem 1rem;
    margin: 0 0.5rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s, transform 0.2s;
  }

  .pagination-button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .pagination-button:hover:not(:disabled) {
    background: #2878b7;
    transform: translateY(-1px);
  }

  .page-info {
    font-size: 0.9rem;
    margin: 0 0.5rem;
    color: #444;
  }

  .description-text {
    /* 设置一个固定高度。此处以 100px 为例，可按需调整 */
    max-height: 100px;
    /* 超出部分产生滚动条 */
    overflow-y: auto;
    /* 如果想让文本在单元格内换行，可以加上 */
    white-space: pre-wrap;
  }
  .search-export-wrapper {
    margin-bottom: 1rem;
  }
  .export-button {
    padding: 0.6rem 1rem;
    background: #28a745;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  .export-button:hover {
    background: #218838;
  }
</style>
