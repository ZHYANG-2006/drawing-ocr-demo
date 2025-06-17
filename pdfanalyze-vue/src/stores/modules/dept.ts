import { defineStore } from 'pinia';
import { request } from '/@/utils/service';
import XEUtils from 'xe-utils';
import { toRaw } from 'vue';
interface DeptInfo {
  id: number;
  name: string;
  parent: number | null; // 假设父级部门的 ID 是数字或空
  [key: string]: any; // 可以包含其他属性
}

export const useDeptInfoStore = defineStore('deptInfo', {
  state: () => ({
    list: [] as DeptInfo[], // 定义 list 的类型为 DeptInfo 数组
    tree: [] as DeptInfo[], // 定义 tree 的类型为 DeptInfo 数组
  }),
  actions: {
    async requestDeptInfo() {
      // 请求部门信息
      const ret = await request({
        url: '/api/system/dept/all_dept/',
      });
      this.list = ret.data;
      this.tree = XEUtils.toArrayTree(ret.data, {
        parentKey: 'parent',
        strict: true,
      }) as DeptInfo[]; // 将返回结果强制转换为 DeptInfo 数组类型
    },
    async getDeptById(id: number) {
      const dept = this.list.find((dept) => dept.id === id);
      return dept || null;
    },
    async getParentDeptById(id: number) {
      const tree = toRaw(this.tree) as DeptInfo[]; // 强制转换 tree 为 DeptInfo 数组
      const obj = XEUtils.findTree(tree, (item) => item.id == id);
      return obj || null;
    },
  },
});
