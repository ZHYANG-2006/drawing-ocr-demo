import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { directive } from '/@/directive/index';
import { i18n } from '/@/i18n';
import other from '/@/utils/other';
import '/@/assets/style/tailwind.css';
import '/@/theme/index.scss';
import Antd from 'ant-design-vue';
import mitt from 'mitt';
import VueGridLayout from 'vue-grid-layout';
import piniaPersist from 'pinia-plugin-persist';
import pinia from './stores';
import { RegisterPermission } from '/@/plugin/permission/index';
import { message, notification } from 'ant-design-vue'; // 引入 Ant Design Vue 的 message 和 notification
import { PerfectScrollbarPlugin } from 'vue3-perfect-scrollbar';
import 'vue3-perfect-scrollbar/style.css';
// 自动注册插件
import VXETable from 'vxe-table';
import 'vxe-table/lib/style.css';

import '/@/assets/style/reset.scss';
import * as Icons from '@ant-design/icons-vue';


const app = createApp(App);

pinia.use(piniaPersist);
directive(app);
// other.registerAntIcons(app); // 替换为 Ant Design Vue 图标注册方法

// 注册所有图标组件
for (const key in Icons) {
  app.component(key, (Icons as Record<string, any>)[key]);
}

app
  .use(VXETable)
  .use(Antd)
  .use(pinia)
  .use(router)
  .use(i18n)
  .use(PerfectScrollbarPlugin)
  .mount('#app');

// 注册 Ant Design Vue 的全局 message 和 notification
app.config.globalProperties.$message = message;
app.config.globalProperties.$notification = notification;
app.config.globalProperties.$icons = Icons;
app.config.globalProperties.mittBus = mitt();
