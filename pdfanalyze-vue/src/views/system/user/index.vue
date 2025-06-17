<template>
  <div>
    <a-row class="menu-a-row">
      <a-col :span="6">
        <div class="menu-box menu-left-box">
          <DeptTreeCom
            ref="deptTreeRef"
            :tree-data="deptTreeData"
            @treeClick="handleTreeClick"
          />
        </div>
      </a-col>
      <a-col :span="18">
        <div style="height: 80vh">
          <UserCom ref="userRef" />
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { message } from 'ant-design-vue';
  import { createCrudOptions } from './crud';
  import * as api from './api';
  import { GetDept } from './api';
  import UserCom from '/@/views/system/user/components/UserCom/index.vue';
  import DeptTreeCom from '/@/views/system/user/components/DeptTreeCom/index.vue';
  import { APIResponseData } from '/@/views/system/menu/types';
  import XEUtils from 'xe-utils';
  import type { DataNode } from 'ant-design-vue/lib/tree';

  const deptTreeData = ref([]);
  const userRef = ref<InstanceType<typeof UserCom> | null>(null);
  const getData = () => {
    GetDept({}).then((ret: APIResponseData) => {
      const responseData = ret.data;
      console.log('responseData', responseData);
      const result = XEUtils.toArrayTree(responseData, {
        parentKey: 'parent',
        children: 'children',
        strict: true,
      });
      // 创建一个 Map，以 ID 作为键，完整节点作为值
      const idMap = new Map<number, any>();
      responseData.forEach((node: any) => {
        idMap.set(node.id, node);
      });

      // 递归处理树形结构，将 parent 替换为对象
      const convertParentToObj = (node: any) => {
        if (node.parent !== null) {
          node.parent = idMap.get(node.parent) || null; // 将 parent ID 替换为对象
        }
        if (node.children) {
          node.children.forEach(convertParentToObj); // 递归处理子节点
        }
      };

      result.forEach(convertParentToObj);

      console.log('result with parent as object', result);
      deptTreeData.value = result;
    });
  };

  // 表单状态和数据源
  const crud = createCrudOptions();

  const handleTreeClick = (record: DataNode) => {
    console.log(record);
    userRef.value?.handleRefreshTable(record);
  };

  // 获取数据
  const fetchData = async () => {
    const res = await crud.fetchData();
    console.log('deptres', res);
  };

  // 获取部门和角色数据
  const loadOptions = async () => {
    crud.getRoleOptions(1);
  };

  onMounted(() => {
    getData();
    loadOptions();
    fetchData();
  });
</script>

<style lang="scss" scoped>
  .menu-a-row {
    height: 100%;
    overflow: hidden;

    .a-col {
      height: 100%;
      padding: 10px 0;
      box-sizing: border-box;
    }
  }

  .menu-box {
    height: 100%;
    padding: 10px;
    background-color: #fff;
    box-sizing: border-box;
  }

  .menu-left-box {
    position: relative;
    border-radius: 0 8px 8px 0;
    margin-right: 10px;
  }

  .menu-right-box {
    border-radius: 8px 0 0 8px;
  }
</style>
