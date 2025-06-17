// 声明路由当前项类型
declare type RouteItem<T = any> = {
  path?: string;
  name?: string | symbol | undefined | null;
  redirect?: string;
  k?: T;
  meta?: {
    title?: string;
    isLink?: string;
    isHide?: boolean;
    isKeepAlive?: boolean;
    isAffix?: boolean;
    isIframe?: boolean;
    roles?: string[];
    icon?: string;
    isDynamic?: boolean;
    isDynamicPath?: string;
    isIframeOpen?: string;
    loading?: boolean;
  };
  children?: T[];
  query?: { [key: string]: T };
  params?: { [key: string]: T };
  contextMenuClickId?: string | number;
  commonUrl?: string;
  isFnClick?: boolean;
  url?: string;
  transUrl?: string;
  title?: string;
  id?: string | number;
};

// 声明路由 to from
declare interface RouteToFrom<T = any> extends RouteItem {
  path?: string;
  children?: T[];
}

// 声明路由当前项类型集合
declare type RouteItems<T extends RouteItem = any> = T[];

// 声明 ref
declare type RefType<T = any> = T | null;

// 声明 HTMLElement
declare type HtmlType = HTMLElement | string | undefined | null;

// 申明 children 可选
declare type ChilType<T = any> = {
  children?: T[];
};

// 申明 数组
declare type EmptyArrayType<T = any> = T[];

// 申明 对象
declare type EmptyObjectType<T = any> = {
  [key: string]: T;
};

// 申明 select option
declare type SelectOptionType = {
  value: string | number;
  label: string | number;
};

// 鼠标滚轮滚动类型
declare interface WheelEventType extends WheelEvent {
  wheelDelta: number;
}

// table 数据格式公共类型
interface ParamType {
  pageNum: number;
  pageSize: number;
  [key: string]: any;
}

interface TableType<T extends ParamType = ParamType> {
  total: number;
  loading: boolean;
  param: T;
}
