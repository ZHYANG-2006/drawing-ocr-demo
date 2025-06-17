/**
 * 判断两数组字符串是否相同（用于按钮权限验证），数组字符串中存在相同时会自动去重（按钮权限标识不会重复）
 * @param news 新数据
 * @param old 源数据
 * @returns 两数组相同返回 `true`，反之则反
 */
export function judementSameArr(
  newArr: unknown[] | string[],
  oldArr: string[],
): boolean {
  const news = removeDuplicate(newArr); // 直接传递字符串数组
  const olds = removeDuplicate(oldArr);
  let count = 0;
  const leng = news.length;

  for (let i = 0; i < olds.length; i++) {
    for (let j = 0; j < news.length; j++) {
      if (olds[i] === news[j]) count++;
    }
  }

  return count === leng;
}

/**
 * 判断两个对象是否相同
 * @param a 要比较的对象一
 * @param b 要比较的对象二
 * @returns 相同返回 true，反之则反
 */
export function isObjectValueEqual<T extends { [key: string]: any }>(
  a: T,
  b: T,
): boolean {
  if (!a || !b) return false;
  const aProps = Object.getOwnPropertyNames(a);
  const bProps = Object.getOwnPropertyNames(b);
  if (aProps.length != bProps.length) return false;
  for (let i = 0; i < aProps.length; i++) {
    const propName = aProps[i];
    const propA = a[propName];
    const propB = b[propName];
    if (!b.hasOwnProperty(propName)) return false;
    if (propA instanceof Object) {
      if (!isObjectValueEqual(propA, propB)) return false;
    } else if (propA !== propB) {
      return false;
    }
  }
  return true;
}

/**
 * 数组、数组对象去重
 * @param arr 数组内容
 * @param attr 需要去重的键值（数组对象）
 * @returns
 */
export function removeDuplicate<T>(arr: T[], attr?: keyof T): T[] {
  if (!arr.length) {
    return arr;
  }

  if (attr) {
    const obj: { [key: string]: boolean } = {};
    return arr.reduce((cur: T[], item: T) => {
      const key = item[attr];
      if (!obj[key as any]) {
        obj[key as any] = true;
        if (key) cur.push(item);
      }
      return cur;
    }, []);
  } else {
    return [...new Set(arr)];
  }
}
