import { request } from '/@/utils/service';

export const apiPrefix = '/api/system/iqa_dir/';

/**
 * 查询 PDF 文件列表
 * @param {Object} params 查询参数 (如分页信息、筛选条件)
 * @returns {Promise} 返回 Promise 对象，包含文件列表和分页信息
 */
export const getList = (params) => {
  return request({
    url: `${apiPrefix}`,
    method: 'get',
    params, // 查询参数
  });
};

export const uploadIQA = (params) => {
  return request({
    url: `${apiPrefix}`,
    method: 'post',
    data: params,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const deleteItem = async (id) => {
  return request({
    url: `${apiPrefix}${id}/`,
    method: 'delete',
  });
};

export const exportExcel = async (id) => {
  return request({
    url: `${apiPrefix}exportExcel/`,   // 对应后端的 /exportExcel/ 路由
    method: 'get',                     // 通常 GET 更直观
    params: { id },                           // 你要传给后端的查询参数
    responseType: 'blob',              // 关键：告诉 axios 这是二进制文件
  })
};
