import { request } from '/@/utils/service';

/**
 * 后端控制菜单模拟HTTPS
 * 后端控制路由，isRequestRoutes 为 true，则开启后端控制路由
 * @method getMenuAdmin 获取后端动态路由菜单(admin)
 * @method getMenuTest 获取后端动态路由菜单(test)
 */
export function useMenuApi() {
  return {
    getSystemMenu: (params?: object) => {
      return request({
        url: '/api/system/menu/web_router/',
        method: 'get',
        params,
      });
    },
    getMenuAdmin: (params?: object) => {
      return request({
        url: '',
        method: 'get',
        params,
      });
    },
    getMenuTest: (params?: object) => {
      return request({
        url: '',
        method: 'get',
        params,
      });
    },
  };
}
