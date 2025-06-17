import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, EditReq, InfoReq } from '/@/types/crudTypes';

export const apiPrefix = '/api/system/menu/';

export function GetList(query: UserPageQuery) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  });
}

export function GetObj(id: InfoReq) {
  return request({
    url: apiPrefix + id + '/',
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
  return request({
    url: apiPrefix + obj.id + '/',
    method: 'put',
    data: obj,
  });
}

export function DelObj(id: string | number) {
  return request({
    url: apiPrefix + id + '/',
    method: 'delete',
  });
}

export function GetAllMenu(query: UserPageQuery) {
  return request({
    url: apiPrefix + 'get_all_menu/',
    method: 'get',
    params: query,
  });
}

export function lazyLoadMenu(query: UserPageQuery) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  }).then((res: { data: any[] }) => {
    // 假设 res.data 是你从 API 得到的菜单列表
    const processedData = res.data.map((item: any) => {
      return {
        ...item,
        parentId: item.parent, // 将 parent 字段映射为 parentId
        parent: undefined, // 删除原有的 parent 字段
      };
    });

    return {
      ...res,
      data: processedData, // 返回处理后的数据
    };
  });
}

export function dragMenu(obj: AddReq) {
  return request({
    url: apiPrefix + 'drag_menu/',
    method: 'post',
    data: obj,
  });
}

export function menuMoveUp(obj: AddReq) {
  return request({
    url: apiPrefix + 'move_up/',
    method: 'post',
    data: obj,
  });
}

export function menuMoveDown(obj: AddReq) {
  return request({
    url: apiPrefix + 'move_down/',
    method: 'post',
    data: obj,
  });
}
