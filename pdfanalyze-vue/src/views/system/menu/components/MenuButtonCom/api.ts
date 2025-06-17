// api.ts
import { request } from '/@/utils/service';
import {
  PageQuery,
  AddReq,
  DelReq,
  InfoReq,
  EditReq,
  UserPageQuery,
} from '/@/types/crudTypes';

export const apiPrefix = '/api/system/menu_button/';

export function GetList(query: UserPageQuery) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  });
}

export function GetObj(id: InfoReq) {
  return request({
    url: `${apiPrefix}${id}`,
    method: 'get',
  });
}

export function AddObj(obj: AddReq) {
  return request({
    url: apiPrefix,
    method: 'post',
    data: obj,
  });
}

export function UpdateObj(obj: EditReq) {
  console.log('object', obj);
  return request({
    url: `${apiPrefix}${obj.id}/`, // 使用 EditReq 中的 row.id
    method: 'put',
    data: obj, // 使用 EditReq 类型的数据
  });
}

export function DelObj(obj: DelReq) {
  return request({
    url: `${apiPrefix}${obj.id}/`, // 使用 DelReq 中的 row.id
    method: 'delete',
    data: obj, // 传递 DelReq 类型的 id
  });
}

export function BatchAdd(obj: { menu: AddReq }) {
  return request({
    url: `${apiPrefix}batch_create/`,
    method: 'post',
    data: obj,
  });
}

// 加载接口地址数据
export function LoadApiOptions() {
  return request({
    url: '/swagger.json',
    method: 'get',
  }).then((res: any) => {
    const paths = Object.keys(res.paths || {});
    return paths.map((path) => ({
      label: path, // 显示的文本
      value: path, // 选中的值
    }));
  });
}
