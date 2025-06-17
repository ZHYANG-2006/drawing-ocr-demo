import { request, downloadFile } from '/@/utils/service';
import {
  PageQuery,
  DelReq,
  AddReq,
  EditReq,
  InfoReq, UserPageQuery,
} from '/@/types/crudTypes';

export const apiPrefix = '/api/system/user/';

export function GetDept(query: PageQuery) {
  return request({
    url: '/api/system/dept/dept_lazy_tree/',
    method: 'get',
    params: query,
  });
}

export function GetRoles(id: Number) {
  return request({
    url: '/api/system/role/',
    method: 'get',
    params: id,
  });
}

export function GetList(query: PageQuery) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  });
}

export function GetObj(id: InfoReq) {
  return request({
    url: apiPrefix + id,
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
    url: `${apiPrefix}${obj.id}/`,
    method: 'put',
    data: obj,
  });
}

export function DelObj(obj: DelReq) {
  return request({
    url: `${apiPrefix}${obj.id}/`,
    method: 'delete',
  });
}

export function lazyLoadDept(query: UserPageQuery) {
  return request({
    url: '/api/system/dept/',
    method: 'get',
    params: query,
  }).then((res: { data: any[] }) => {
    const processedData = res.data.map((item: any) => {
      return {
        ...item,
        parentId: item.parent,
        parent: undefined,
      };
    });

    return {
      ...res,
      data: processedData,
    };
  });
}

export function ResetPassword(id: number) {
  return request({
    url: `${apiPrefix}${id}/reset_to_default_password/`,
    method: 'put',
  });
}
