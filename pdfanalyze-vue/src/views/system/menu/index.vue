<template>
  <div>
    <a-row class="menu-a-row">
      <a-col :span="6">
        <div class="menu-box menu-left-box">
          <MenuTreeCom
            ref="menuTreeRef"
            :tree-data="menuTreeData"
            @treeClick="handleTreeClick"
            @updateMenu="handleUpdateMenu"
            @deleteMenu="handleDeleteMenu"
          />
        </div>
      </a-col>

      <a-col :span="18">
        <a-tabs default-active-key="1" type="card">
          <a-tab-pane key="1" tab="按钮权限配置">
            <div style="height: 80vh">
              <MenuButtonCom ref="menuButtonRef" />
            </div>
          </a-tab-pane>
          <a-tab-pane key="2" tab="列权限配置">
            <div style="height: 80vh">
              <MenuFieldCom ref="menuFieldRef" />
            </div>
          </a-tab-pane>
        </a-tabs>
      </a-col>
    </a-row>

    <a-drawer
      v-model:open="drawerVisible"
      title="菜单配置"
      placement="right"
      width="500px"
      :closable="false"
      @close="() => handleDrawerClose()"
    >
      <MenuFormCom
        v-if="drawerVisible"
        :init-form-data="drawerFormData"
        :cache-data="menuTreeCacheData"
        :tree-data="menuTreeData"
        @drawerClose="handleDrawerClose"
      />
    </a-drawer>
  </div>
</template>
<script lang="ts" setup name="menuPages">
  import { ref, onMounted } from 'vue';
  import XEUtils from 'xe-utils';
  import { Modal } from 'ant-design-vue';
  import MenuTreeCom from './components/MenuTreeCom/index.vue';
  import MenuButtonCom from './components/MenuButtonCom/index.vue';
  import MenuFormCom from './components/MenuFormCom/index.vue';
  import MenuFieldCom from './components/MenuFieldCom/index.vue';
  import { GetList, DelObj } from './api';
  import { successNotification } from '/@/utils/message';
  import { APIResponseData, MenuTreeItemType } from './types';
  import type {
    DataNode,
    DirectoryTreeProps,
    EventDataNode,
  } from 'ant-design-vue/lib/tree';

  const menuTreeData = ref([]);
  const menuTreeCacheData = ref<MenuTreeItemType[]>([]);
  const drawerVisible = ref(false);
  const drawerFormData = ref<Partial<MenuTreeItemType>>({});
  const menuTreeRef = ref<InstanceType<typeof MenuTreeCom> | null>(null);
  const menuButtonRef = ref<InstanceType<typeof MenuButtonCom> | null>(null);
  const menuFieldRef = ref<InstanceType<typeof MenuFieldCom> | null>(null);
  const getData = () => {
    GetList({}).then((ret: APIResponseData) => {
      const responseData = ret.data;
      const result = XEUtils.toArrayTree(responseData, {
        parentKey: 'parent',
        children: 'children',
        strict: true,
      });
      menuTreeData.value = result;
    });
  };

  /**
   * 菜单的点击事件
   */
  const handleTreeClick = (record: DataNode) => {
    console.log(record);
    menuButtonRef.value?.handleRefreshTable(record);
    menuFieldRef.value?.handleRefreshTable(record);
  };

  /**
   * 菜单的 新增 or 编辑 事件
   */
  const handleUpdateMenu = (type: string, record?: DataNode) => {
    if (type === 'update' && record) {
      console.log('currentNode', record.parent);
      const parentData = record.parent;
      menuTreeCacheData.value = [parentData];
      drawerFormData.value = record;
      console.log('drawerFormData', drawerFormData.value);
    }
    drawerVisible.value = true;
  };
  const handleDrawerClose = (type?: string) => {
    if (type === 'submit') {
      getData();
    }
    drawerVisible.value = false;
    drawerFormData.value = {};
  };

  /**
   * 部门的删除事件
   */
  const handleDeleteMenu = (id: string, callback: Function) => {
    Modal.confirm({
      title: '温馨提示',
      content: '您确认删除该菜单项吗?',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        const res: APIResponseData = await DelObj(id);
        callback();
        if (res?.code === 2000) {
          successNotification(res.msg as string);
          getData();
        }
      },
    });
  };

  onMounted(() => {
    getData();
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
