import { defineStore } from 'pinia';
import { ConfigStates } from './interface';
import { request } from '../utils/service';
export const urlPrefix = '/api/init/settings/';

/**
 * 系统配置数据
 * @methods getSystemConfig 获取系统配置数据
 */
export const SystemConfigStore = defineStore('SystemConfig', {
  state: (): ConfigStates => ({
    systemConfig: {},
  }),
  actions: {
    async getSystemConfigs() {
      request({
        url: urlPrefix,
        method: 'get',
      }).then((ret: { data: [] }) => {
        // 转换数据格式并保存到pinia
        this.systemConfig = JSON.parse(JSON.stringify(ret.data));
        console.log("retdata", this.systemConfig)
      });
    },
    async saveSystemConfigs(data: any) {
      await request({
        url: '/api/system/system_config/save_content/',
        method: 'put',
        data,
      });
      await this.getSystemConfigs();
    },
  },
  persist: {
    enabled: true,
  },
});
