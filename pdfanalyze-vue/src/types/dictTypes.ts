export interface DictOptions<T = any> {
  url?: string | (() => string); // 字典数据的请求 URL，可以是字符串或函数
  getData?: () => Promise<T[]>; // 自定义获取数据的方法
  value?: string; // 字典项的值字段
  label?: string; // 字典项的标签字段
  children?: string; // 字典项的子节点字段
  color?: string; // 字典项的颜色字段
  isTree?: boolean; // 是否为树形结构
  cache?: boolean; // 是否缓存字典
  immediate?: boolean; // 是否立即请求字典数据
  data?: T[]; // 本地字典数据
}
