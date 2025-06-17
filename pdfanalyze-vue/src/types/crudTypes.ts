// 分页查询类型
export interface Page {
  pageNumber: number;
  pageSize: number;
}

export interface PageSort {
  field: string;
  order: 'ascend' | 'descend'; // 定义排序方式
}

// PageQuery 接口定义
export interface PageQuery<R = any> {
  page?: Page; // 可选的分页信息
  form?: R; // 可选的查询表单，类型为 R
  sort?: PageSort; // 可选的排序信息
}

// PageQuery 接口定义
export interface UserPageQuery<R = any> {
  [key: string]: any; // 允许动态字段
}

// InfoReq 接口定义
export interface InfoReq<R = any> {
  [key: string]: any; // 允许动态字段
  mode?: string; // 可选的操作模式字段
  row?: R; // 可选的行信息，类型为 R
}

// DelReq 接口定义
export interface DelReq<R = any> {
  [key: string]: any; // 允许动态字段
  row?: R; // 可选的行信息，类型为 R
}

// 新增对象请求类型
export interface AddReq<R = any> {
  [key: string]: any; // 允许动态字段
  form?: R; // 可选的表单字段，类型为 R
}

// EditReq 接口定义
export interface EditReq<R = any> {
  [key: string]: any; // 允许其他动态字段
  form?: R; // 可选的表单数据，类型为 R
  row?: R; // 可选的行数据，类型为 R
}
