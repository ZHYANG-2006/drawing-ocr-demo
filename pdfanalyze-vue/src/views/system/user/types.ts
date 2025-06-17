import type {
  DataNode,
  DirectoryTreeProps,
  EventDataNode,
} from 'ant-design-vue/lib/tree';

export interface TreeTypes {
  id?: number;
  name?: string;
  status?: boolean;
  is_catalog?: boolean;
  children?: TreeTypes[];
}

export interface APIResponseData {
  code?: number;
  data: [];
  msg?: string;
}

export interface FormTypes<T> {
  [key: string]: T;
}

export interface ComponentFileItem {
  value: string;
  label: string;
}
/*
export interface DeptTreeItemType extends EventDataNode {
  id?: number | string;
  modifier_name?: string;
  creator_name?: string;
  create_datetime?: string;
  update_datetime?: string;
  parent_name?: string;
  status_label?: string;
  has_children?: number;
  hasChild?: false,
  description?: string;
  modifier?: string;
  dept_belong_id?: string;
  name?: string;
  key?: string;
  sort?: number;
  owner?: string;
  phone?: string;
  email?: string;
  status?: boolean;
  creator?: number;
  parent?: DeptTreeItemType;
}*/
