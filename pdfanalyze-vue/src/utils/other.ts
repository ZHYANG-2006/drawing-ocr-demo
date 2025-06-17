import { nextTick, defineAsyncComponent } from 'vue';
import type { App } from 'vue';
// 替换为 Ant Design Vue 的图标库（如需引入）
import * as antIcons from '@ant-design/icons-vue';
import router from '/@/router/index';
import pinia from '/@/stores/index';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { i18n } from '/@/i18n/index';
import { Local } from '/@/utils/storage';
import { verifyUrl } from '/@/utils/toolsValidate';
import { SystemConfigStore } from '/@/stores/systemConfig';

/**
 * 全局注册 ant-design-vue 图标
 * @param app vue 实例
 */
export function registerAntIcons(app: App) {
  Object.keys(antIcons).forEach((key) => {
    const iconComponent = antIcons[key as keyof typeof antIcons];
    // 判断是否是有效的 Vue 组件，然后注册
    if (
      typeof iconComponent === 'function' ||
      typeof iconComponent === 'object'
    ) {
      app.component(key, iconComponent);
    }
  });
}

/**
 * 设置浏览器标题国际化
 */
export function useTitle() {
  const stores = SystemConfigStore(pinia);
  const { systemConfig }: { systemConfig: any } = storeToRefs(stores);
  nextTick(() => {
    let webTitle = '';
    const globalTitle: string = systemConfig['base.web_title'];
    const { path, meta } = router.currentRoute.value;
    if (path === '/login') {
      webTitle = <string>meta.title;
    } else {
      webTitle = setTagsViewNameI18n(router.currentRoute.value);
    }
    document.title = `${webTitle}` || 'DVAdmin';
  });
}

/**
 * 设置网站 favicon 图标
 */
export function useFavicon() {
  const stores = SystemConfigStore(pinia);
  const { systemConfig } = storeToRefs(stores);
  nextTick(() => {
    const iconUrl = systemConfig.value['base.web_favicon'];
    if (iconUrl) {
      const faviconUrl = `${iconUrl}?t=${new Date().getTime()}`;
      const link = document.querySelector(
        "link[rel~='icon']",
      ) as HTMLLinkElement;
      if (!link) {
        const newLink = document.createElement('link') as HTMLLinkElement;
        newLink.rel = 'shortcut icon';
        newLink.href = faviconUrl;
        document.head.appendChild(newLink);
      } else {
        link.href = faviconUrl;
      }
    }
  });
}

/**
 * 设置自定义 tagsView 名称、国际化处理
 */
export function setTagsViewNameI18n(item: any) {
  let tagsViewName = '';
  const { query, params, meta } = item;
  if (query?.tagsViewName || params?.tagsViewName) {
    if (
      /\/zh-cn|en|zh-tw\//.test(query?.tagsViewName) ||
      /\/zh-cn|en|zh-tw\//.test(params?.tagsViewName)
    ) {
      const urlTagsParams =
        (query?.tagsViewName && JSON.parse(query?.tagsViewName)) ||
        (params?.tagsViewName && JSON.parse(params?.tagsViewName));
      tagsViewName = urlTagsParams[i18n.global.locale.value];
    } else {
      tagsViewName = query?.tagsViewName || params?.tagsViewName;
    }
  } else {
    tagsViewName = i18n.global.t(meta.title);
  }
  return tagsViewName;
}

/**
 * 图片懒加载
 */
export const lazyImg = (el: string, arr: EmptyArrayType) => {
  const io = new IntersectionObserver((res) => {
    res.forEach((v: any) => {
      if (v.isIntersecting) {
        const { img, key } = v.target.dataset;
        v.target.src = img;
        v.target.onload = () => {
          io.unobserve(v.target);
          arr[key]['loading'] = false;
        };
      }
    });
  });
  nextTick(() => {
    document.querySelectorAll(el).forEach((img) => io.observe(img));
  });
};

/**
 * 全局组件大小
 */
export const globalComponentSize = (): string => {
  const stores = useThemeConfig(pinia);
  const { themeConfig } = storeToRefs(stores);
  return (
    Local.get('themeConfig')?.globalComponentSize ||
    themeConfig.value?.globalComponentSize
  );
};

/**
 * 对象深拷贝
 */
export function deepClone(obj: EmptyObjectType) {
  let newObj: EmptyObjectType;
  try {
    newObj = obj.push ? [] : {};
  } catch (error) {
    newObj = {};
  }
  for (const attr in obj) {
    if (obj[attr] && typeof obj[attr] === 'object') {
      newObj[attr] = deepClone(obj[attr]);
    } else {
      newObj[attr] = obj[attr];
    }
  }
  return newObj;
}

/**
 * 判断是否是移动端
 */
export function isMobile() {
  return /phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile/i.test(
    navigator.userAgent,
  );
}

/**
 * 判断数组对象中所有属性是否为空，为空则删除当前行对象
 */
export function handleEmpty(list: EmptyArrayType) {
  const arr = [];
  for (const i in list) {
    const d = [];
    for (const j in list[i]) {
      d.push(list[i][j]);
    }
    const leng = d.filter((item) => item === '').length;
    if (leng !== d.length) {
      arr.push(list[i]);
    }
  }
  return arr;
}

/**
 * 打开外部链接
 */
export function handleOpenLink(val: RouteItem) {
  const { origin, pathname } = window.location;
  // 检查 val.path 是否存在且为字符串
  if (val.path) {
    router.push(val.path);
  } else {
    router.push('');
  }

  if (verifyUrl(<string>val.meta?.isLink)) window.open(val.meta?.isLink);
  else window.open(`${origin}${pathname}#${val.meta?.isLink}`);
}

/**
 * 统一批量导出
 */
const other = {
  registerAntIcons: (app: App) => {
    registerAntIcons(app);
  },
  useTitle: () => {
    useTitle();
  },
  useFavicon: () => {
    useFavicon();
  },
  setTagsViewNameI18n: (route: RouteToFrom) => {
    return setTagsViewNameI18n(route);
  },
  lazyImg: (el: string, arr: EmptyArrayType) => {
    lazyImg(el, arr);
  },
  globalComponentSize: () => {
    return globalComponentSize();
  },
  deepClone: (obj: EmptyObjectType) => {
    return deepClone(obj);
  },
  isMobile: () => {
    return isMobile();
  },
  handleEmpty: (list: EmptyArrayType) => {
    return handleEmpty(list);
  },
  handleOpenLink: (val: RouteItem) => {
    handleOpenLink(val);
  },
};

// 统一批量导出
export default other;
