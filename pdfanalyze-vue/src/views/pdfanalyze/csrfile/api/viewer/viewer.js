import { request } from '/@/utils/service';

export const apiPrefix = '/api/system/csrfile_vreview/';

/**
 * 查询 PDF 文件列表
 * @param {Object} params 查询参数 (如分页信息、筛选条件)
 * @returns {Promise} 返回 Promise 对象，包含文件列表和分页信息
 */
export const getPDF = async (reviewVersionId) => {
  try {
    const response = await request({
      url: '/api/system/csrfile_vreview/getpdf/',
      method: 'post',
      data: { review_version_id: reviewVersionId },
      responseType: 'blob', // 确保返回的是文件流
    });
    return response;
  } catch (error) {
    console.error('获取 PDF 文件失败:', error);
    throw error;
  }
};

export const getJson = (reviewVersionId) => {
  return request({
    url: `/api/system/csrfile_vreview/${reviewVersionId}/getjson/`,
    method: 'get',
  });
};

export const getReview = async (params) => {
  return request({
    url: `/api/system/csrfile_reviewrst/?id=${params}`,
    method: 'get',
    params, // 查询参数
  });
};

export const saveReview = async (params) => {
  return request({
    url: `/api/system/csrfile_reviewrst/savereview/`,
    method: 'post',
    data: params,
  });
};

export const deleteItem = async (id) => {
  return request({
    url: `/api/system/csrfile_reviewrst/${id}/`,
    method: 'delete',
  });
};
