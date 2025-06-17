import { request } from '/@/utils/service';
import { getBaseURL } from '/@/utils/baseUrl';
import { successNotification } from '/@/utils/message';

export default {
  async install(app: any, options: any) {
    // 设置全局的请求和响应处理
    app.config.globalProperties.$request = request;

    // 处理上传文件的逻辑
    app.config.globalProperties.$uploadFile = async (file: any) => {
      const data = new FormData();
      data.append('file', file);
      const ret = await request({
        url: '/api/system/file/',
        method: 'post',
        data,
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return {
        url: getBaseURL(ret.data.url),
        key: ret.data.id,
        ...ret.data,
      };
    };

    // 其他通用设置
    // 占位符和对齐设置
    const placeholderSettings = [
      { key: 'text', placeholder: '请输入' },
      { key: 'textarea', placeholder: '请输入' },
      { key: 'input', placeholder: '请输入' },
      { key: 'password', placeholder: '请输入' },
    ];
    placeholderSettings.forEach((val) => {
      // 根据需要设置占位符和对齐
      app.config.globalProperties.$setPlaceholder(val.key, val.placeholder);
    });
  },
};
