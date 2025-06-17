import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { notification, Modal } from 'ant-design-vue'; // 使用 Ant Design Vue 的通知和弹框
import { Session } from '/@/utils/storage';
import qs from 'qs';

// 配置新建一个 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 500000,
  headers: { 'Content-Type': 'application/json' },
  paramsSerializer: {
    serialize(params) {
      return qs.stringify(params, { allowDots: true });
    },
  },
});

// 添加请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 Session 中获取 token
    const token = Session.get('token');
    console.log('token:');
    console.log(token);
    if (token) {
      config.headers['Authorization'] = `JWT ${token}`; // 确保加上 JWT 前缀
    }
    return config;
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error);
  },
);

// 添加响应拦截器
service.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    const res = response.data;
    if (res.code && res.code !== 0) {
      // `token` 过期或者账号已在别处登录
      if (res.code === 401 || res.code === 4001) {
        Session.clear(); // 清除浏览器全部临时缓存
        window.location.href = '/'; // 去登录页
        Modal.confirm({
          title: '提示',
          content: '你已被登出，请重新登录',
          onOk() {
            // 处理确认操作
            window.location.href = '/'; // 重定向到登录页
          },
        });
      }
      return Promise.reject(service.interceptors.response);
    } else {
      return response.data;
    }
  },
  (error) => {
    // 对响应错误做点什么
    if (error.message.indexOf('timeout') !== -1) {
      notification.error({
        message: '错误',
        description: '网络超时',
      });
    } else if (error.message === 'Network Error') {
      notification.error({
        message: '错误',
        description: '网络连接错误',
      });
    } else {
      if (error.response?.data) {
        notification.error({
          message: '错误',
          description: error.response.statusText,
        });
      } else {
        notification.error({
          message: '错误',
          description: '接口路径找不到',
        });
      }
    }
    return Promise.reject(error);
  },
);

// 导出 axios 实例
export default service;
