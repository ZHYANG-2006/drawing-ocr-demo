// src/api/monitorConfig.js
import { request } from '/@/utils/service';

const apiPrefix = '/api/system/monitor-config/';

/**
 * 拉取配置列表（支持分页）
 * @param {Object} params  { page, page_size }
 */
export function fetchMonitorConfigs(params) {
  return request({
    url: apiPrefix,
    method: 'get',
    params,
  });
}

/**
 * 新增一条监控配置
 * @param {Object} data  { directory_path, cron_hour, cron_minute, enabled }
 */
export function createMonitorConfig(data) {
  return request({
    url: apiPrefix,
    method: 'post',
    data,
  });
}

/**
 * 修改一条监控配置
 * @param {Number|String} id
 * @param {Object} data
 */
export function updateMonitorConfig(id, data) {
  return request({
    url: `${apiPrefix}${id}/`,
    method: 'patch',
    data,
  });
}

/**
 * 删除一条监控配置
 * @param {Number|String} id
 */
export function deleteMonitorConfig(id) {
  return request({
    url: `${apiPrefix}${id}/`,
    method: 'delete',
  });
}
