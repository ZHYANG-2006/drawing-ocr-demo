import axios from 'axios';
import get from 'lodash-es/get';
import { Modal } from 'ant-design-vue'; // 替换为 Ant Design Vue
// import type { ModalFuncProps } from 'ant-design-vue/lib/modal/Modal';
// @ts-ignore
import { errorLog, errorCreate } from './tools.ts';
import { Session } from '/@/utils/storage';
import qs from 'qs';
import { getBaseURL } from './baseUrl';

/**
 * @description 创建请求实例
 */
function createService() {
  const service = axios.create({
    timeout: 20000,
    headers: {
      'Content-Type': 'application/json;charset=utf-8',
    },
    paramsSerializer: {
      serialize(params) {
        interface paramsObj {
          [key: string]: any;
        }
        const result: paramsObj = {};
        for (const [key, value] of Object.entries(params)) {
          if (value !== '') {
            result[key] = value;
          }
          if (typeof value === 'boolean') {
            result[key] = value ? 'True' : 'False';
          }
        }
        return qs.stringify(result);
      },
    },
  });

  // 请求拦截
  service.interceptors.request.use(
    (config) => {
      const token = Session.get('token');
      if (token) {
        config.headers['Authorization'] = `JWT ${token}`;
      }
      return config;
    },
    (error) => {
      console.log(error);
      return Promise.reject(error);
    },
  );

  // 响应拦截
  service.interceptors.response.use(
    (response) => {
      if (response.config.responseType === 'blob') {
        return response;
      }

      const dataAxios = response.data;
      const { code } = dataAxios;

      if (dataAxios.swagger != undefined) {
        return dataAxios;
      }

      if (code === undefined) {
        errorCreate(`非标准返回：${dataAxios}， ${response.config.url}`, false);
        return dataAxios;
      } else {
        switch (code) {
          case 400:
            errorCreate(`${dataAxios.msg}: ${response.config.url}`);
            break;
          case 401:
            Session.clear();
            dataAxios.msg = '登录认证失败，请重新登录';
            Modal.confirm({
              title: '提示',
              content: dataAxios.msg,
              onOk() {
                window.location.reload();
              },
            });
            errorCreate(`${dataAxios.msg}: ${response.config.url}`);
            break;
          case 2000:
            // @ts-ignore
            if (response.config.unpack === false) {
              return dataAxios;
            }
            return dataAxios;
          case 4000:
            errorCreate(`${dataAxios.msg}: ${response.config.url}`);
            break;
          default:
            errorCreate(`${dataAxios.msg}: ${response.config.url}`);
            break;
        }
        return Promise.reject(dataAxios);
      }
    },
    (error) => {
      const status = get(error, 'response.status');
      switch (status) {
        case 400:
          error.message = '请求错误';
          break;
        case 401:
          Session.clear();
          error.message = '登录授权过期，请重新登录';
          Modal.confirm({
            title: '提示',
            content: error.message,
            onOk() {
              window.location.reload();
            },
          });
          break;
        case 403:
          error.message = '拒绝访问';
          break;
        case 404:
          error.message = `请求地址出错: ${error.response.config.url}`;
          break;
        case 408:
          error.message = '请求超时';
          break;
        case 500:
          error.message = '服务器内部错误';
          break;
        case 501:
          error.message = '服务未实现';
          break;
        case 502:
          error.message = '网关错误';
          break;
        case 503:
          error.message = '服务不可用';
          break;
        case 504:
          error.message = '网关超时';
          break;
        case 505:
          error.message = 'HTTP版本不受支持';
          break;
        default:
          break;
      }
      errorLog(error);
      return Promise.reject(error);
    },
  );
  return service;
}

/**
 * 创建请求方法
 */
function createRequestFunction(service: any) {
  return function (config: any) {
    const configDefault = {
      headers: {
        'Content-Type': get(config, 'headers.Content-Type', 'application/json'),
      },
      timeout: 500000,
      baseURL: getBaseURL(),
      data: {},
    };

    const token = Session.get('token');
    if (token != null) {
      // @ts-ignore
      configDefault.headers.Authorization = 'JWT ' + token;
    }
    return service(Object.assign(configDefault, config));
  };
}

export const service = createService();
export const request = createRequestFunction(service);

// 模拟网络请求的实例和请求方法
export const serviceForMock = createService();
export const requestForMock = createRequestFunction(serviceForMock);

/**
 * 下载文件
 */
export const downloadFile = function ({
  url,
  params,
  method,
  filename = '文件导出',
}: any) {
  request({
    url: url,
    method: method,
    params: params,
    responseType: 'blob',
  }).then((res: any) => {
    const xlsxName = window.decodeURI(
      res.headers['content-disposition'].split('=')[1],
    );
    const fileName = xlsxName || `${filename}.xlsx`;
    if (res) {
      const blob = new Blob([res.data], { type: 'charset=utf-8' });
      const elink = document.createElement('a');
      elink.download = fileName;
      elink.style.display = 'none';
      elink.href = URL.createObjectURL(blob);
      document.body.appendChild(elink);
      elink.click();
      URL.revokeObjectURL(elink.href);
      document.body.removeChild(elink);
    }
  });
};
