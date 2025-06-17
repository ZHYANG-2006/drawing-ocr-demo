import { request } from '/@/utils/service';

export const apiPrefix = '/api/system/cppqcp_vreview/';

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

export const createReview = (params) => {
  return request({
    url: `${apiPrefix}`,
    method: 'post',
    data: params,
  });
};

export const deleteItem = async (id) => {
  return request({
    url: `/api/system/cppqcp_vreview/${id}/`,
    method: 'delete',
  });
};

export const closeStatus = async (reviewVersionId) => {
  try {
    const response = await request({
      url: '/api/system/cppqcp_vreview/closestatus/',
      method: 'post',
      data: { review_version_id: reviewVersionId },
    });
    return response;
  } catch (error) {
    throw error;
  }
};
