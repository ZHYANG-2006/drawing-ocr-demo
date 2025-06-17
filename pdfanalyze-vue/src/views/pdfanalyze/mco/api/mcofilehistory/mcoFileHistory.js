import { request } from '/@/utils/service';
import { message } from 'ant-design-vue';

export const apiPrefix = '/api/system/mco_file_history/';

export const syncFileHistory = async () => {
  try {
    const response = await request({
      url: '/api/system/mco_file_history/sync_files/',
      method: 'post',
      data: {},
    });
    return response;
  } catch (error) {
    console.error('获取文件失败:', error);
    throw error;
  }
};

export const getFileHistory = (params) => {
  return request({
    url: `${apiPrefix}`,
    method: 'get',
    params, // 查询参数
  });
};
