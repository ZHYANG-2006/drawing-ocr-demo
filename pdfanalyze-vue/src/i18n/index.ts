import { createI18n } from 'vue-i18n';
import pinia from '/@/stores/index';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';

// 引入 Ant Design Vue 的国际化语言包
import enLocaleAntd from 'ant-design-vue/es/locale/en_US';
import zhcnLocaleAntd from 'ant-design-vue/es/locale/zh_CN';
import zhtwLocaleAntd from 'ant-design-vue/es/locale/zh_TW';

// 定义变量内容
const messages: Record<string, any> = {};
const antd: Record<'en' | 'zh-cn' | 'zh-tw', any> = {
  en: enLocaleAntd,
  'zh-cn': zhcnLocaleAntd,
  'zh-tw': zhtwLocaleAntd,
};

const itemize: { [key: string]: any[] } = { en: [], 'zh-cn': [], 'zh-tw': [] };
const modules: Record<string, any> = import.meta.glob('./**/*.ts', {
  eager: true,
});

// 对自动引入的 modules 进行分类 en、zh-cn、zh-tw
for (const path in modules) {
  const key = path.match(/(\S+)\/(\S+).ts/);
  if (itemize[key![2]]) itemize[key![2]].push(modules[path].default);
  else itemize[key![2]] = modules[path];
}

// 合并数组对象
function mergeArrObj<T extends Record<string, any[]>>(list: T, key: string) {
  let obj = {};
  list[key].forEach((i: EmptyObjectType) => {
    obj = Object.assign({}, obj, i);
  });
  return obj;
}

// 处理最终格式
for (const key in itemize) {
  const localeKey = key as 'en' | 'zh-cn' | 'zh-tw'; // 限制 key 类型
  messages[key] = {
    name: key,
    antd: antd[localeKey], // 合并 Ant Design Vue 的国际化
    message: mergeArrObj(itemize, key),
  };
}

// 读取 pinia 默认语言
const stores = useThemeConfig(pinia);
const { themeConfig } = storeToRefs(stores);

// 导出语言国际化
export const i18n = createI18n({
  legacy: false,
  silentTranslationWarn: true,
  missingWarn: false,
  silentFallbackWarn: true,
  fallbackWarn: false,
  locale: themeConfig.value.globalI18n,
  fallbackLocale: 'zh-cn',
  messages,
});
