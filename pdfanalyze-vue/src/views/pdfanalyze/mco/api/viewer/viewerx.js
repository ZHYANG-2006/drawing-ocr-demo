import { request } from '/@/utils/service';

export const apiPrefix = '/api/system/mco_view/';

/**
 * 查询 PDF 文件列表
 * @param {Object} params 查询参数 (如分页信息、筛选条件)
 * @returns {Promise} 返回 Promise 对象，包含文件列表和分页信息
 */
export const getPDF = async (id) => {
  try {
    const response = await request({
      url: '/api/system/mco_view/getpdf/',
      method: 'post',
      data: { Id: id },
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
    url: `/api/system/mco_view/${id}/getjson/`,
    method: 'get',
  });
};