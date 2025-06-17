import useClipboard from 'vue-clipboard3';
import { message } from 'ant-design-vue'; // 使用 Ant Design Vue 的 message 组件
import { formatDate } from '/@/utils/formatTime';
import { useI18n } from 'vue-i18n';

export default function () {
  const { t } = useI18n();
  const { toClipboard } = useClipboard();

  // 百分比格式化
  const percentFormat = (
    row: EmptyArrayType,
    column: number,
    cellValue: string,
  ) => {
    return cellValue ? `${cellValue}%` : '-';
  };

  // 列表日期时间格式化
  const dateFormatYMD = (
    row: EmptyArrayType,
    column: number,
    cellValue: string,
  ) => {
    if (!cellValue) return '-';
    return formatDate(new Date(cellValue), 'YYYY-mm-dd');
  };

  // 列表日期时间格式化
  const dateFormatYMDHMS = (
    row: EmptyArrayType,
    column: number,
    cellValue: string,
  ) => {
    if (!cellValue) return '-';
    return formatDate(new Date(cellValue), 'YYYY-mm-dd HH:MM:SS');
  };

  // 列表日期时间格式化
  const dateFormatHMS = (
    row: EmptyArrayType,
    column: number,
    cellValue: string,
  ) => {
    if (!cellValue) return '-';
    let time = 0;
    if (typeof row === 'number') time = row;
    if (typeof cellValue === 'number') time = cellValue;
    return formatDate(new Date(time * 1000), 'HH:MM:SS');
  };

  // 小数格式化
  const scaleFormat = (value: string = '0', scale: number = 4) => {
    return Number.parseFloat(value).toFixed(scale);
  };

  // 小数格式化
  const scale2Format = (value: string = '0') => {
    return Number.parseFloat(value).toFixed(2);
  };

  // 点击复制文本
  const copyText = (text: string) => {
    return new Promise((resolve, reject) => {
      try {
        // 复制
        toClipboard(text);
        // 复制成功的提示框
        message.success(t('message.layout.copyTextSuccess')); // 使用 Ant Design Vue 的 message
        resolve(text);
      } catch (e) {
        // 复制失败的提示框
        message.error(t('message.layout.copyTextError')); // 使用 Ant Design Vue 的 message
        reject(e);
      }
    });
  };

  return {
    percentFormat,
    dateFormatYMD,
    dateFormatYMDHMS,
    dateFormatHMS,
    scaleFormat,
    scale2Format,
    copyText,
  };
}
