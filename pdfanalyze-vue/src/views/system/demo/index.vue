<template>
  <a-page>
    <a-card>
      <template #header>
        <div
          v-show="isEcharts"
          id="myEcharts"
          v-resize-ob="handleResize"
          :style="{ width: '100%', height: '300px' }"
        ></div>
      </template>
      <a-table :data-source="data" :columns="columns" />
    </a-card>
  </a-page>
</template>

<script lang="ts" setup name="loginLog">
  import { ref, onMounted } from 'vue';
  import * as echarts from 'echarts';

  const isEcharts = ref(true);
  const data = ref([]); // 表格数据
  const columns = ref([
    // 表格列定义
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '创建者',
      dataIndex: 'creator_name',
      key: 'creator_name',
    },
    {
      title: '创建时间',
      dataIndex: 'create_datetime',
      key: 'create_datetime',
    },
  ]);

  function initChart() {
    const chart = echarts.init(
      document.getElementById('myEcharts'),
      'purple-passion',
    );
    chart.setOption({
      title: {
        text: '2021年各月份销售量（单位：件）',
        left: 'center',
      },
      xAxis: {
        type: 'category',
        data: [
          '一月',
          '二月',
          '三月',
          '四月',
          '五月',
          '六月',
          '七月',
          '八月',
          '九月',
          '十月',
          '十一月',
          '十二月',
        ],
      },
      tooltip: {
        trigger: 'axis',
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          data: [606, 542, 985, 687, 501, 787, 339, 706, 383, 684, 669, 737],
          type: 'line',
          smooth: true,
          itemStyle: {
            normal: {
              label: {
                show: true,
                position: 'top',
                formatter: '{c}',
              },
            },
          },
        },
      ],
    });
    window.onresize = function () {
      chart.resize();
    };
  }

  // 页面打开后获取列表数据
  onMounted(() => {
    // 请求 API 加载数据
    fetchData();
    initChart();
  });

  function handleResize(size: any) {
    console.log(size);
  }

  async function fetchData() {
    // 示例 API 请求
    const response = await fetch('your-api-url');
    const result = await response.json();
    data.value = result; // 设置表格数据
  }
</script>
