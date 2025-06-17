import { request } from '/@/utils/service';

export const apiPrefix = '/api/system/mco_para/';


/**
 * 查询 PDF 文件列表
 * @param {Object} params 查询参数 (如分页信息、筛选条件)
 * @returns {Promise} 返回 Promise 对象，包含文件列表和分页信息
 */
export const getPara = async (query, page, pageSize) => {
  try {
    const response = await request({
      url: '/api/system/mco_para/search_paragraphs/',
      method: 'post',
      data: {
        query: query,
        page: page,
        page_size: pageSize,
      },
      // responseType: 'blob', // 确保返回的是文件流
    });
    return response;
  } catch (error) {
    console.error('获取 PDF 文件失败:', error);
    throw error;
  }
};

/**
 * 查询 PDF 文件列表
 * @param {Object} params 查询参数 (如分页信息、筛选条件)
 * @returns {Promise} 返回 Promise 对象，包含文件列表和分页信息
 */
export const getFilterPara = async (query) => {
  try {
    const response = await request({
      url: '/api/system/mco_para/search_paragraphs_filter/',
      method: 'post',
      data: {
        query: query,
      },
    });
    return response;
  } catch (error) {
    console.error('获取 PDF 文件失败:', error);
    throw error;
  }
};

/**
 * 查询 PDF 文件列表
 * @param {Object} params 查询参数 (如分页信息、筛选条件)
 * @returns {Promise} 返回 Promise 对象，包含文件列表和分页信息
 */
export const downloadPDF = async (pdf_id) => {
  try {
    const response = await request({
      url: '/api/system/mco_para/download_pdf/',
      method: 'post',
      data: { pdf_id: pdf_id },
      responseType: 'blob', // 确保返回的是文件流
    });
    return response;
  } catch (error) {
    console.error('获取 PDF 文件失败:', error);
    throw error;
  }
};
