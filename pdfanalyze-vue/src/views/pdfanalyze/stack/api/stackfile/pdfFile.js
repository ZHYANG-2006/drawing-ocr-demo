import { request } from '/@/utils/service';

export const apiPrefix = '/api/system/stack_pdf/';

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

export const uploadPDF = (params) => {
  return request({
    url: `${apiPrefix}`,
    method: 'post',
    data: params,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getTask = (params) => {
  return request({
    url: `/stack_schedule_parse/?id=${params}`,
    method: 'get',
    params, // 查询参数
  });
};

export const deleteItem = async (id) => {
  return request({
    url: `${apiPrefix}${id}/`,
    method: 'delete',
  });
};

/**
 * 查询 PDF 文件列表
 * @param {Object} params 查询参数 (如分页信息、筛选条件)
 * @returns {Promise} 返回 Promise 对象，包含文件列表和分页信息
 */
export const getPDF = async (id) => {
  try {
    const response = await request({
      url: '/api/system/stack_pdf/getpdf/',
      method: 'post',
      data: { id: id },
      responseType: 'blob', // 确保返回的是文件流
    });
    return response;
  } catch (error) {
    console.error('获取 PDF 文件失败:', error);
    throw error;
  }
};

export const getJson = (id) => {
  return request({
    url: `/api/system/stack_pdf/${id}/getjson/`,
    method: 'get',
  });
};
