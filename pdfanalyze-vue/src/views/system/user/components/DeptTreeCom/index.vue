<template>
  <div>
    <a-input v-model:value="filterVal" placeholder="请输入部门名称">
      <template #prefix>
        <SearchOutlined />
      </template>
    </a-input>
    <div class="menu-tree-com">
      <div class="mtc-head">
        <MenuOutlined style="padding: 10px" />
        部门列表
        <a-tooltip placement="right" title="1.部门信息;">
          <QuestionCircleOutlined style="padding: 10px" />
        </a-tooltip>
      </div>

      <a-tree
        ref="treeRef"
        :tree-data="treeData"
        :fieldNames="defaultTreeProps"
        :load-data="onLoadData"
        :filter-tree-node="filterNode"
        lazy
        show-line
        @select="handleNodeClick"
      >
        <template #title="{ name, icon }">
          <component :is="icon" style="margin-right: 8px" />
          <span>{{ name }}</span>
        </template>
      </a-tree>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, toRaw, watch, onMounted } from 'vue';
  import {
    SearchOutlined,
    MenuOutlined,
    QuestionCircleOutlined,
    PlusOutlined,
    EditOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined,
    DeleteOutlined,
  } from '@ant-design/icons-vue';
  import { lazyLoadDept } from '../../api';
  import type {
    DataNode,
    DirectoryTreeProps,
    EventDataNode,
  } from 'ant-design-vue/lib/tree';
  import { TreeDataItem } from 'ant-design-vue/es/tree/Tree';

  interface IProps {
    treeData: DataNode[];
  }

  const sortDisable = ref(false);

  const defaultTreeProps: any = {
    title: 'name',
    key: 'id',
    isLeaf: (data: any) => !data.hasChild,
  };

  const treeRef = ref();

  const props = withDefaults(defineProps<IProps>(), {
    treeData: () => [],
  });

  // 使用 ref 包装 props.treeData 使其响应式
  const treeData = ref<TreeDataItem[]>(props.treeData);

  watch(
    () => props.treeData, // 监听 props.treeData
    (newValue) => {
      treeData.value = newValue; // 更新响应式 treeData 的值
    },
  );

  const emit = defineEmits(['treeClick']);

  const filterVal = ref('');
  const treeSelectMenu = ref<Partial<DataNode>>({});
  const treeSelectNode = ref<DataNode | null>(null);
  const expandedKeys = ref<string[]>([]);

  watch(filterVal, (val) => {
    treeRef.value?.filterTreeNode(val);
  });

  /**
   * 树的搜索事件
   */
  const filterNode = (treeNode: EventDataNode) => {
    if (!filterVal.value) return true;
    return treeNode.title.toString().indexOf(filterVal.value) !== -1;
  };

  const addExpandedKey = (key: string) => {
    if (!expandedKeys.value.includes(key)) {
      expandedKeys.value.push(key);
    }
  };

  const updateTreeData = (
    list: DataNode[],
    key: string,
    children: any[],
    parentId: number,
    parent: EventDataNode,
  ) => {
    list.forEach((node) => {
      if (node.id === parentId) {
        node.children = children.map((child) => ({
          ...child,
          parent: parent, // 将每个子节点的 parent 字段设置为传递进来的 parent
          isLeaf: !child.hasChild,
        }));
      } else if (node.children) {
        updateTreeData(node.children, key, children, parentId, parent); // 递归查找父节点
      }
    });
  };

  const onLoadData = (treeNode: any) => {
    return new Promise((resolve: (value?: unknown) => void) => {
      if (treeNode.children) {
        // 如果已经加载了子节点，直接 resolve
        resolve();
        return;
      }
      // 调用后端接口获取子节点数据
      lazyLoadDept({ parent: treeNode.key }).then((res: { data: any[] }) => {
        // 假设 res.data 返回的是子节点数组
        treeNode.children = res.data.map((child: any) => ({
          id: child.id,
          name: child.name,
          hasChild: child.hasChild,
          isLeaf: !child.hasChild,
          icon: child.icon || 'SettingOutlined', // 默认图标或指定图标
        }));
        updateTreeData(
          treeData.value,
          treeNode.key as string,
          res.data,
          treeNode.key,
          treeNode,
        );
        treeData.value = [...treeData.value]; // 触发响应式更新
        resolve();
      });
    });
  };

  /**
   * 树的点击事件
   */
  const handleNodeClick = (keys: any, event: any) => {
    treeSelectMenu.value = event.node.dataRef;
    treeSelectNode.value = event.node.dataRef;
    console.log('treeselectMenu', treeSelectMenu.value);
    emit('treeClick', treeSelectMenu.value);
  };

  defineExpose({
    treeRef,
  });
</script>

<style lang="scss" scoped>
  .dept-tree-com {
    .mtc-head {
      display: flex;
      align-items: center;
      color: #606266;
      font-weight: 600;
      .mtc-head-icon {
        margin-right: 8px;
        position: relative;
        top: -1px;
      }

      .mtc-tooltip {
        margin-left: 5px;
        position: relative;
        top: -1px;
      }
    }
    .mtc-tags {
      height: 40px;
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 0 20px;
      display: flex;
      align-items: center;
      justify-content: space-around;
      box-sizing: border-box;

      .mtc-tags-icon {
        cursor: pointer;
        color: var(--ant-color-primary);
      }
    }
  }
</style>

<style lang="scss">
  .dept-tree-com {
    height: calc(100% - 60px);
    padding: 20px;
    box-sizing: border-box;
    overflow-y: auto;

    .ant-tree-treenode {
      height: 32px !important;
    }

    .ant-tree .anticon-file svg {
      display: none !important;
      height: 0;
      width: 0;
    }
  }
</style>
