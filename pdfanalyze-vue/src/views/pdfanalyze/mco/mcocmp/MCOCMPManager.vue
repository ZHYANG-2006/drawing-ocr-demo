<template>
  <div class="compare-page scrollable-container">
    <h1 class="page-title">PDF 文档对比</h1>
    <!-- 表单输入区域 -->
    <div class="compare-form">
      <div class="form-row">
        <label>旧版 Drawing Number:</label>
        <input v-model="oldDrawing" placeholder="旧文件编号" />
      </div>
      <div class="form-row">
        <label>旧版 Rev:</label>
        <input v-model="oldRev" placeholder="旧文件版本" />
      </div>
      <div class="form-row">
        <label>新版 Drawing Number:</label>
        <input v-model="newDrawing" placeholder="新文件编号" />
      </div>
      <div class="form-row">
        <label>新版 Rev:</label>
        <input v-model="newRev" placeholder="新文件版本" />
      </div>
      <button class="compare-btn" @click="submitCompare" :disabled="loading">
        <span v-if="loading" class="loading-spinner"></span>
        {{ loading ? '比对中...' : '提交比对' }}
      </button>
    </div>
    <!-- 状态提示 -->
    <div class="status-section" v-if="taskId">
      <p>当前状态: {{ parseStateMessage }}</p>
    </div>
    <!-- 加载/错误提示 -->
    <transition name="fade">
      <div v-if="errorMsg" class="error-box">{{ errorMsg }}</div>
    </transition>

    <!-- 结果展示 -->
    <transition name="fade">
      <div v-if="resultData" class="result-area">
        <div class="diff-summary">
          <span>🔧 修改：{{ modCount }}</span>
          <span>➕ 新增：{{ insertCount }}</span>
          <span>➖ 删除：{{ deleteCount }}</span>
        </div>
        <h2 class="section-title">对比结果</h2>
        <!-- 新增：旧版/新版全文对比区域 -->
        <div class="compare-section full-text-compare">
          <!-- 左侧：旧版全文 -->
          <div class="full-text-column">
            <div class="full-text-title">旧版全文</div>
            <div class="full-text-content" v-html="resultData.article.old_article"></div>
          </div>
          <!-- 右侧：新版全文 -->
          <div class="full-text-column">
            <div class="full-text-title">新版全文</div>
            <div class="full-text-content" v-html="resultData.article.new_article"></div>
          </div>
        </div>
        <!-- sdiff：匹配到但存在修改的段落列表 -->
        <div
          v-for="(item, sIndex) in resultData.sdiff"
          :key="'sdiff-'+sIndex"
          class="sdiff-card"
        >
          <div class="sdiff-header">
            <h3 class="sdiff-title">修改段落 #{{ sIndex + 1 }}</h3>
          </div>
          <div class="sdiff-body">
            <div class="compare-section">
              <!-- 左侧：旧段落 -->
              <div class="old-part">
                <p class="para-title">旧文本:</p>
                <p class="para-content">
                  <!-- 使用 v-html 来渲染高亮过的文本 -->
                  <span v-html="highlightDiff(item.old_para_value, item.diff, 'old')"></span>
                </p>
                <img
                  class="para-img"
                  :src="item.old_para_pic"
                  alt="Old Paragraph"
                />
              </div>
              <!-- 右侧：新段落 -->
              <div class="new-part">
                <p class="para-title">新文本:</p>
                <p class="para-content">
                  <span v-html="highlightDiff(item.new_para_value, item.diff, 'new')"></span>
                </p>
                <img
                  class="para-img"
                  :src="item.new_para_pic"
                  alt="New Paragraph"
                />
              </div>
            </div>
            <div class="diff-analyze" v-if="item.analyze">
              <p class="analysis-title">差异分析:</p>
              <p class="analysis-content">{{ item.analyze }}</p>
            </div>
          </div>
        </div>

        <!-- ldiff：新增或删除的段落 -->
        <div
          v-for="(item, lIndex) in resultData.ldiff"
          :key="'ldiff-'+lIndex"
          class="ldiff-card"
        >
          <div class="ldiff-header">
            <h3 class="ldiff-title">
              段落变化 #{{ lIndex + 1 }}
            </h3>
          </div>
          <div class="ldiff-body">
            <p v-if="item.type === 'inserted'" class="ldiff-label inserted">
              【新增】该段落仅出现在新版本:
            </p>
            <p v-else-if="item.type === 'deleted'" class="ldiff-label deleted">
              【删除】该段落在旧版本存在，新版本已无:
            </p>
            <div class="ldiff-content">
              <p class="ldiff-text">{{ item.para_value }}</p>
              <img
                class="ldiff-img"
                :src="item.para_pic"
                alt="Paragraph Image"
              />
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
  import { ref, onUnmounted, onMounted, computed, watch } from 'vue'
  import axios from 'axios'
  import { getDiff, getResult } from "/@/views/pdfanalyze/mco/api/mcocmp/pdfCmper.js";
  /**
   * 响应式状态
   */
  const oldDrawing = ref('')
  const oldRev = ref('')
  const newDrawing = ref('')
  const newRev = ref('')

  const loading = ref(false)
  const taskId = ref(null)
  const errorMsg = ref('')
  // 保存对比任务ID
  const compareId = ref(null)
  // 最终展示的对比结果数据（sdiff/ldiff）
  const resultData = ref(null)

  // 用来显示状态提示
  const parseStateMessage = ref('')

  // 最终对比结果
  const compareResult = ref(null)

  // 轮询定时器
  let pollingTimer = null

  const modCount = computed(() => resultData.value?.sdiff?.length || 0)
  const insertCount = computed(() => resultData.value?.ldiff?.filter(item => item.type === 'inserted').length || 0)
  const deleteCount = computed(() =>
    resultData.value?.ldiff?.filter(item => item.type === 'deleted').length || 0
  )

  const STORAGE_KEY = 'pdfCompareResult'
  const DN_OLD_KEY = 'dnOldKey'
  const DEV_OLD_KEY ='devOldKey'
  const DN_NEW_KEY = 'dnNewKey'
  const DEV_NEW_KEY ='devNewKey'

  onMounted(() => {
    const cache = sessionStorage.getItem(STORAGE_KEY)
    if (cache) {
      try { resultData.value = JSON.parse(cache) } catch {}
    }
    const dn_old = sessionStorage.getItem(DN_OLD_KEY)
    if (dn_old) {
      try { oldDrawing.value = dn_old } catch {}
    }
    const dev_old = sessionStorage.getItem(DEV_OLD_KEY)
    if (dev_old) {
      try { oldRev.value = dev_old } catch {}
    }
    const dn_new = sessionStorage.getItem(DN_NEW_KEY)
    if (dn_new) {
      try { newDrawing.value = dn_new } catch {}
    }
    const dev_new = sessionStorage.getItem(DEV_NEW_KEY)
    if (dn_old) {
      try { newRev.value = dev_new } catch {}
    }
  })

  // 拿到新数据时写缓存
  watch(resultData, (val) => {
    if (val) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(val))
      sessionStorage.setItem(DN_OLD_KEY, oldDrawing.value)
      sessionStorage.setItem(DEV_OLD_KEY, oldRev.value)
      sessionStorage.setItem(DN_NEW_KEY, newDrawing.value)
      sessionStorage.setItem(DEV_NEW_KEY, newRev.value)
    }
  }, { deep: true })

  /**
   * 提交对比请求
   * 1. 向后端 /api/compare/ 发送旧/新文件参数
   * 2. 若返回 compare_id 和 pending 状态，则开始轮询
   * 3. 若直接返回对比结果，则可直接展示
   */
  const submitCompare = async () => {
    try {
      loading.value = true
      errorMsg.value = ''
      resultData.value = null
      compareId.value = null
      parseStateMessage.value = ''
      // 构造请求体
      const payload = {
        old_drawing: oldDrawing.value,
        old_rev: oldRev.value,
        new_drawing: newDrawing.value,
        new_rev: newRev.value
      }
      // 发起 POST 请求
      const resp = await getDiff(payload)
      console.log('resp!!', resp.data.task_id)
      // 可能后端返回:
      // 1. { compare_id: 42, status: 'pending' } (异步模式)
      // 2. 直接 sdiff, ldiff 结构 (同步模式)
      if (resp.data.task_id) {
        compareId.value = resp.data.task_id
        if (resp.data.status === 'pending') {
          taskId.value = resp.data.task_id
          parseStateMessage.value = '对比中...'  // 初始提示
          // 后端异步任务尚未完成 -> 进入轮询
          pollResult()
        } else if (resp.data.status === 'completed') {
          console.log('completed')
          // 如果后端已直接完成(极少见)，那么把结果取出来
          resultData.value = resp.data.result
        }
      } else {
        // 说明后端直接返回对比结果 JSON (同步处理)
        resultData.value = resp.data
      }
    } catch (err) {
      errorMsg.value = '提交对比请求失败: ' + err
    } finally {
      loading.value = false
    }
  }

  /**
   * 轮询获取对比结果
   * 每隔3秒请求一次 /api/compare/<compareId>/ 查询状态
   */
  const pollResult = () => {
    if (pollingTimer) {
      clearInterval(pollingTimer)
    }
    pollingTimer = setInterval(async () => {
      try {
        const resp = await getResult(compareId.value)
        // 约定后端返回 { status: 'pending'/'completed'/'failed', result_data: {...} }
        if (resp.data.data.status === 'pending') {
          // 继续等待
          console.log('对比任务进行中...')
        } else if (resp.data.data.status === 'completed') {
          // 拿到最终结果 sdiff/ldiff
          resultData.value = resp.data.data.result.result
          console.log('resultData', resultData.value)
          clearInterval(pollingTimer)
          pollingTimer = null
          taskId.value = null
        } else if (resp.data.data.status === 'failed') {
          errorMsg.value = '对比任务失败'
          clearInterval(pollingTimer)
          pollingTimer = null
        }
      } catch (err) {
        console.error('轮询失败:', err)
      }
    }, 3000)
  }

  /**
   * 页面卸载时清除定时器
   */
  onUnmounted(() => {
    if (pollingTimer) {
      clearInterval(pollingTimer)
    }
  })

  const WHITE = '[\\s\\u00A0]';

  function escapeReg(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  // 把一个片段拆成词，再用 \s* 拼回去 → 任意空白都能穿过去
  function looseify(str) {
    return str.trim()
      .split(/\s+/)
      .map(escapeReg)
      .join(`${WHITE}*`);   // ↖? 用扩展空白
  }

  function buildWindowRegex(l, c, r) {
    const left  = l ? `${looseify(l)}${WHITE}*` : '';
    const right = r ? `${WHITE}*${looseify(r)}` : '';
    return new RegExp(`${left}(${looseify(c)})${right}`, 'gsi');
  }

  const highlightDiff = (text, diffs, mode) => {
    if (!diffs || diffs.length === 0) return text
    let html = text

    for (const d of diffs) {
      if (mode === 'old' && ['delete', 'replace'].includes(d.type) && d.old_text.trim()) {
        const reg = buildWindowRegex(d.old_left, d.old_text, d.old_right)
        html = html.replace(reg, (_match, p1) =>
          _match.replace(
            p1,
            `<span class="${d.type === 'delete' ? 'diff-delete' : 'diff-replace-old'}">${p1}</span>`
          )
        )
      }

      if (mode === 'new' && ['insert', 'replace'].includes(d.type) && d.new_text.trim()) {
        const reg = buildWindowRegex(d.new_left, d.new_text, d.new_right)
        html = html.replace(reg, (_match, p1) =>
          _match.replace(
            p1,
            `<span class="${d.type === 'insert' ? 'diff-insert' : 'diff-replace-new'}">${p1}</span>`
          )
        )
      }
    }
    return html
  }
</script>

<style scoped>
  /* 背景与整体布局 */
  .compare-page {
    margin: 0 auto;
    max-width: 95vw;
    padding: 2rem;
    background: linear-gradient(160deg, #f3f9fe 0%, #fdfdfd 100%);
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    font-family: "Helvetica Neue", "Open Sans", sans-serif;
    color: #333;
  }

  .compare-section.full-text-compare {
    display: flex;
    align-items: flex-start; /* 左右栏目顶部对齐 */
    gap: 20px; /* 栏目间间距，与整体风格一致 */

    .full-text-column {
      flex: 1; /* 双栏等宽 */
      display: flex;
      flex-direction: column; /* 确保标题和内容垂直排列 */
    }

    .full-text-title {
      font-weight: bold;
      margin-bottom: 8px; /* 标题与内容之间留白 */
      /* 可根据现有 compare-section 标题样式进行调整 (如字体大小、颜色等) */
    }

    .full-text-content {
      /* 内容区域样式，尽量与现有 compare-section 风格一致 */
      background-color: #f7f7f7;
      border: 1px solid #e0e0e0;
      padding: 15px;
      border-radius: 4px;
      color: #333;
      word-break: break-all; /* 防止超长单词破坏布局，必要时自动换行 */
      /* 如内容较长，可限制高度并开启滚动，以保持页面整洁 */
      max-height: 500px;
      overflow-y: auto;
      white-space: pre-line;
    }
  }

  /* 标题 */
  .page-title {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    text-align: center;
    color: #3c3c3c;
    font-weight: 600;
  }

  /* 表单区域 */
  .compare-form {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1rem;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1.5rem;
  }

  .form-row {
    display: flex;
    align-items: center;
  }

  .form-row label {
    width: auto;
    font-weight: 500;
    margin-right: 8px;
    color: #555;
  }

  .form-row input {
    width: 180px;
    padding: 6px 10px;
    font-size: 0.95rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    outline: none;
    transition: border 0.2s;
  }

  .form-row input:focus {
    border-color: #8ec1fd;
  }

  .compare-btn {
    padding: 0.6rem 1.2rem;
    background: #007fff;
    color: #fff;
    border: none;
    border-radius: 20px;
    font-size: 1rem;
    cursor: pointer;
    margin-left: auto;
    transition: background 0.25s;
    display: flex;
    align-items: center;
  }

  .compare-btn:hover {
    background: #006ae1;
  }

  .compare-btn:disabled {
    background: #c2d3f3;
    cursor: not-allowed;
  }

  .loading-spinner {
    border: 3px solid #fff;
    border-top: 3px solid #007fff;
    border-radius: 50%;
    width: 15px;
    height: 15px;
    margin-right: 8px;
    animation: spin 0.8s linear infinite;
  }

  /* 加载动画 */
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* 错误提示 */
  .error-box {
    background: #ffefef;
    color: #e00;
    padding: 0.8rem 1rem;
    border: 1px solid #f7d2d2;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  /* 在这里设置最大高度 + 滚动条 */
  .scrollable-container {
    max-height: 100vh;
    overflow: auto;
    padding-right: 0.5rem; /* 留一点空白，好看些 */
  }

  /* 结果区 */
  .result-area {
    margin-top: 20px;
    padding-top: 10px;
  }

  /* 卡片标题 */
  .section-title {
    font-size: 1.4rem;
    margin-bottom: 1rem;
    font-weight: 600;
    color: #444;
    border-bottom: 2px solid #ddd;
    padding-bottom: 0.3rem;
  }

  /* sdiff 卡片 */
  .sdiff-card {
    background: #ffffffee;
    border: 1px solid #eee;
    border-radius: 8px;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    overflow: hidden;
  }

  .sdiff-header {
    background: #f7faff;
    border-bottom: 1px solid #eee;
    padding: 0.5rem 1rem;
  }

  .sdiff-title {
    font-size: 1.1rem;
    margin: 0;
    font-weight: 600;
    color: #007fff;
  }

  .sdiff-body {
    padding: 1rem;
  }

  /* ldiff 卡片 */
  .ldiff-card {
    background: #fff;
    border: 1px solid #eee;
    border-radius: 8px;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    overflow: hidden;
  }

  .ldiff-header {
    background: #f7faff;
    border-bottom: 1px solid #eee;
    padding: 0.5rem 1rem;
  }

  .ldiff-title {
    font-size: 1.1rem;
    margin: 0;
    font-weight: 600;
    color: #ee679f;
  }

  /* sdiff / ldiff 具体布局 */
  .compare-section {
    display: flex;
    gap: 20px;
    margin: 10px 0;
  }

  .old-part, .new-part {
    width: 50%;
    background: #fafafa;
    border: 1px solid #eee;
    border-radius: 4px;
    padding: 0.7rem;
    position: relative;
  }

  .para-title {
    font-weight: 500;
    margin-bottom: 4px;
    color: #555;
  }

  .para-content {
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 0.5rem;
    min-height: 1.5em;
  }

  .para-content > span{
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 0.5rem;
    min-height: 1.5em;
    white-space: pre-line;
  }

  .para-img,
  .ldiff-img {
    /* 不再设置 width, max-width, height 等，这样就保留图片本身的分辨率 */
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-top: 0.4rem;
  }

  /* 差异说明 */
  .diff-analyze {
    margin-top: 1rem;
    padding: 0.7rem;
    border-left: 3px solid #8ec1fd;
    background: #fefefe;
    white-space: pre-line;
  }

  .analysis-title {
    font-size: 0.95rem;
    font-weight: 500;
    margin-bottom: 0.3rem;
    color: #007fff;
  }

  .analysis-content {
    margin: 0;
    font-size: 0.9rem;
    color: #333;
    white-space: pre-line;
  }

  /* ldiff */
  .ldiff-body {
    padding: 1rem;
  }

  .ldiff-label {
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
  }

  .ldiff-label.inserted {
    color: #28a745;
    font-weight: bold;
  }

  .ldiff-label.deleted {
    color: #e83e8c;
    font-weight: bold;
  }

  .ldiff-text {
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
    white-space: pre-line;
  }
  /* 动画过渡 */
  .fade-enter-active, .fade-leave-active {
    transition: all 0.4s ease;
  }
  .fade-enter-from, .fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
  }

  .diff-summary {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.95rem;
    color: #555;
  }
  .diff-summary span {
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    background: #f0f0f0;
  }

  /* diff 高亮 */
  :deep(.diff-insert) {
    background-color: #d4fcdc; /* 淡绿 */
    padding: 2px 3px;
    border-radius: 2px;
  }
  :deep(.diff-delete) {
    background-color: #ffe6e6; /* 淡粉 */
    text-decoration: line-through;
    padding: 2px 3px;
    border-radius: 2px;
  }
  :deep(.diff-replace-old) {
    background-color: #fae3b4; /* 淡黄 */
    text-decoration: line-through;
    padding: 2px 3px;
    border-radius: 2px;
  }
  :deep(.diff-replace-new) {
    background-color: #fae3b4; /* 淡黄 */
    font-weight: bold;
    padding: 2px 3px;
    border-radius: 2px;
  }
</style>