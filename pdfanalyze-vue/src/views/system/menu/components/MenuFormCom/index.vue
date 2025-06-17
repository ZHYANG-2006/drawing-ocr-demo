<template>
  <div class="menu-form-com">
    <div class="menu-form-alert">
      1.红色星号表示必填;<br />
      2.添加菜单，如果是目录，组件地址为空即可;<br />
      3.添加根节点菜单，父级菜单为空即可;
    </div>
    <a-form
      ref="formRef"
      :rules="rules"
      :model="menuFormData"
      :label-col="{ span: 8 }"
      :wrapper-col="{ span: 16 }"
    >
      <a-form-item label="菜单名称" name="name">
        <a-input
          v-model:value="menuFormData.name"
          placeholder="请输入菜单名称"
        />
      </a-form-item>

      <a-form-item label="父级菜单" name="parent">
        <a-tree-select
          v-model:value="menuFormData.parent"
          :replace-fields="defaultTreeProps"
          tree-data-simple-mode
          :tree-data="treeData"
          :placeholder="'请选择父级菜单'"
          :load-data="onLoadData"
          allow-clear
          style="width: 100%"
        >
          <template #title="{ key, name }">
            <span>{{ name }}</span>
          </template>
        </a-tree-select>
      </a-form-item>

      <a-form-item label="路由地址" name="web_path">
        <a-input
          v-model:value="menuFormData.web_path"
          placeholder="请输入路由地址，请以/开头"
        />
      </a-form-item>

      <a-form-item
        v-if="menuFormData.icon !== undefined"
        label="图标"
        name="icon"
      >
        <IconSelector v-model:value="menuFormData.icon" clearable />
      </a-form-item>

      <a-row>
        <a-col :span="12">
          <a-form-item label="状态" required>
            <a-switch
              v-model:checked="menuFormData.status"
              checked-children="启用"
              un-checked-children="禁用"
            />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item v-if="menuFormData.status" label="侧边显示" required>
            <a-switch
              v-model:checked="menuFormData.visible"
              checked-children="显示"
              un-checked-children="隐藏"
            />
          </a-form-item>
        </a-col>
      </a-row>

      <a-row>
        <a-col :span="12">
          <a-form-item label="是否目录" required>
            <a-switch
              v-model:checked="menuFormData.is_catalog"
              checked-children="是"
              un-checked-children="否"
            />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item v-if="!menuFormData.is_catalog" label="外链接" required>
            <a-switch
              v-model:checked="menuFormData.is_link"
              checked-children="是"
              un-checked-children="否"
            />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item
            v-if="!menuFormData.is_catalog"
            label="是否固定"
            required
          >
            <a-switch
              v-model:checked="menuFormData.is_affix"
              checked-children="是"
              un-checked-children="否"
            />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item
            v-if="!menuFormData.is_catalog && menuFormData.is_link"
            label="是否内嵌"
            required
          >
            <a-switch
              v-model:checked="menuFormData.is_iframe"
              checked-children="是"
              un-checked-children="否"
            />
          </a-form-item>
        </a-col>
      </a-row>

      <a-form-item label="备注">
        <a-textarea
          v-model:value="menuFormData.description"
          :maxlength="200"
          show-count
          placeholder="请输入备注"
        />
      </a-form-item>

      <a-divider />

      <div style="min-height: 184px">
        <a-form-item
          v-if="!menuFormData.is_catalog && !menuFormData.is_link"
          label="组件地址"
          name="component"
        >
          <a-auto-complete
            v-model:value="menuFormData.component"
            :options="componentOptions"
            placeholder="输入组件地址"
            allow-clear
          />
        </a-form-item>

        <a-form-item
          v-if="!menuFormData.is_catalog && !menuFormData.is_link"
          label="组件名称"
          name="component_name"
        >
          <a-input
            v-model:value="menuFormData.component_name"
            placeholder="请输入组件名称"
          />
        </a-form-item>

        <a-form-item
          v-if="!menuFormData.is_catalog && menuFormData.is_link"
          label="外链接"
          name="link_url"
        >
          <a-input
            v-model:value="menuFormData.link_url"
            placeholder="请输入外链接地址"
          />
        </a-form-item>

        <a-form-item v-if="!menuFormData.is_catalog" label="缓存">
          <a-switch
            v-model:checked="menuFormData.cache"
            checked-children="启用"
            un-checked-children="禁用"
          />
        </a-form-item>
      </div>

      <a-divider />
    </a-form>

    <div class="menu-form-btns">
      <a-button type="primary" :loading="menuBtnLoading" @click="handleSubmit">
        保存
      </a-button>
      <a-button @click="handleCancel">取消</a-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted, reactive, watch, provide } from 'vue';
  import {
    RuleObject,
    ValidateErrorEntity,
  } from 'ant-design-vue/es/form/interface';
  import IconSelector from '/@/components/iconSelector/index.vue';
  import { lazyLoadMenu, AddObj, UpdateObj } from '../../api';
  import { successNotification } from '/@/utils/message';
  import {
    MenuFormDataType,
    MenuTreeItemType,
    ComponentFileItem,
    APIResponseData,
  } from '../../types';
  import type { FormInstance } from 'ant-design-vue';
  import type { DataNode, EventDataNode } from 'ant-design-vue/es/tree';

  interface IProps {
    initFormData: Partial<MenuTreeItemType> | null;
    treeData: MenuTreeItemType[];
    cacheData: MenuTreeItemType[];
  }

  interface OptionType {
    label: string;
    value: string;
  }

  interface TreeNode extends DataNode {
    level: number;
    data: {
      id: string;
    };
  }

  const defaultTreeProps: any = {
    value: 'id',
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
      lazyLoadMenu({ parent: treeNode.key }).then((res: { data: any[] }) => {
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

  const validateWebPath = (rule: any, value: string, callback: Function) => {
    const pattern = /^\/.*?/;
    const reg = pattern.test(value);
    if (reg) {
      callback();
    } else {
      callback(new Error('请输入正确的地址'));
    }
  };

  const validateLinkUrl = (rule: any, value: string, callback: Function) => {
    const patternUrl = /http(s)?:\/\/([\w-]+\.)+[\w-]+(\/[\w- .\/?%&=]*)?/;
    const reg = patternUrl.test(value);
    if (reg) {
      callback();
    } else {
      callback(new Error('请输入正确的地址'));
    }
  };

  const props = withDefaults(defineProps<IProps>(), {
    initFormData: () => ({}),
    treeData: () => [],
    cacheData: () => [],
  });
  const emit = defineEmits(['drawerClose']);

  const formRef = ref<FormInstance | null>(null);

  const rules: { [key: string]: RuleObject[] } = {
    web_path: [
      {
        required: true,
        message: '请输入正确的地址',
        validator: validateWebPath,
        trigger: 'blur',
      },
    ],
    name: [
      {
        required: true,
        message: '菜单名称必填',
        type: 'string',
        trigger: 'blur',
      },
    ],
    component: [
      {
        required: true,
        message: '请输入组件地址',
        type: 'string',
        trigger: 'blur',
      },
    ],
    component_name: [
      {
        required: true,
        message: '请输入组件名称',
        type: 'string',
        trigger: 'blur',
      },
    ],
    link_url: [
      {
        required: true,
        message: '请输入外链接地址',
        validator: validateLinkUrl,
        trigger: 'blur',
      },
    ],
  };

  const treeData = ref<MenuTreeItemType[]>([]);
  const menuFormData = reactive<MenuFormDataType>({
    parent: '',
    name: '',
    component: '',
    web_path: '',
    icon: '',
    cache: true,
    status: true,
    visible: true,
    component_name: '',
    description: '',
    is_catalog: false,
    is_link: false,
    is_iframe: false,
    is_affix: false,
    link_url: '',
  });
  const menuBtnLoading = ref(false);

  const setMenuFormData = () => {
    if (props.initFormData?.id) {
      menuFormData.id = props.initFormData?.id || '';
      menuFormData.name = props.initFormData?.name || '';
      menuFormData.parent = props.initFormData?.parent?.id || '';
      menuFormData.component = props.initFormData?.component || '';
      menuFormData.web_path = props.initFormData?.web_path || '';
      menuFormData.icon = props.initFormData?.icon || '';
      menuFormData.status = !!props.initFormData.status;
      menuFormData.visible = !!props.initFormData.visible;
      menuFormData.cache = !!props.initFormData.cache;
      menuFormData.component_name = props.initFormData?.component_name || '';
      menuFormData.description = props.initFormData?.description || '';
      menuFormData.is_catalog = !!props.initFormData.is_catalog;
      menuFormData.is_link = !!props.initFormData.is_link;
      menuFormData.is_iframe = !!props.initFormData.is_iframe;
      menuFormData.is_affix = !!props.initFormData.is_affix;
      menuFormData.link_url = props.initFormData?.link_url || '';
    }
  };

  provide('menuFormData', menuFormData);

  const querySearch = (queryString: string) => {
    const files: any = import.meta.glob('@views/**/*.vue');
    const fileLists: Array<any> = [];
    Object.keys(files).forEach((queryString: string) => {
      fileLists.push({
        label: queryString.replace(/(\.\/|\.vue)/g, ''),
        value: queryString.replace(/(\.\/|\.vue)/g, ''),
      });
    });
    const results = queryString
      ? fileLists.filter(createFilter(queryString))
      : fileLists;
    // 统一去掉/src/views/前缀
    results.forEach((val) => {
      val.label = val.label.replace('/src/views/', '');
      val.value = val.value.replace('/src/views/', '');
    });
    return results;
  };

  const componentOptions = ref<OptionType[]>([]); // 明确指定类型

  // 监听输入框的值变化，动态更新选项
  watch(
    () => menuFormData.component,
    (newValue) => {
      componentOptions.value = querySearch(newValue); // 更新选项
    },
  );

  watch(
    () => menuFormData.icon,
    (newVal) => {
      console.log('menuFormData.icon updated:', newVal); // 检查 icon 的初始值和后续更新
    },
    { immediate: true },
  );

  const createFilter = (queryString: string) => {
    return (file: ComponentFileItem) => {
      return file.value.toLowerCase().indexOf(queryString.toLowerCase()) !== -1;
    };
  };

  /**
   * 树的懒加载
   */
  const handleTreeLoad = (node: TreeNode, resolve: Function) => {
    if (node.level !== 0) {
      lazyLoadMenu({ parent: node.data.id }).then((res: APIResponseData) => {
        resolve(res.data);
      });
    }
  };

  const handleSubmit = async () => {
    if (!formRef.value) return;
    try {
      // 直接使用 await 等待验证结果
      await formRef.value.validate(); // validate 会返回一个 Promise

      let res;
      menuBtnLoading.value = true;
      console.log('menuFormData2', { menuFormData });
      if (menuFormData.id) {
        res = await UpdateObj(menuFormData);
      } else {
        res = await AddObj(menuFormData);
      }
      if (res?.code === 2000) {
        successNotification(res.msg as string);
        handleCancel();
      }
    } catch (error) {
      console.log('Validation failed:', error);
    } finally {
      menuBtnLoading.value = false;
    }
  };

  const handleCancel = () => {
    emit('drawerClose', '');
    formRef.value?.resetFields();
  };

  onMounted(async () => {
    props.treeData.map((item) => {
      treeData.value.push(item);
    });
    setMenuFormData();
  });
</script>

<style lang="scss" scoped>
  .menu-form-com {
    margin: 10px;
    overflow-y: auto;
    .menu-form-alert {
      color: #fff;
      line-height: 24px;
      padding: 8px 16px;
      margin-bottom: 20px;
      border-radius: 4px;
      background-color: var(--ant-color-primary);
    }
    .menu-form-btns {
      padding-bottom: 10px;
      box-sizing: border-box;
    }
  }
</style>
