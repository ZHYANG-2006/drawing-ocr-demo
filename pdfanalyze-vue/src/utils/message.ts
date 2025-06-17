import {
  message as AntMessage,
  notification as AntNotification,
} from 'ant-design-vue';

// 修改消息提示为 Ant Design Vue 的 message
export function message(content: string, option?: any) {
  AntMessage.open({ content, ...option });
}
export function successMessage(content: string, option?: any) {
  AntMessage.success({ content, ...option });
}
export function warningMessage(content: string, option?: any) {
  AntMessage.warning({ content, ...option });
}
export function errorMessage(content: string, option?: any) {
  AntMessage.error({ content, ...option });
}
export function infoMessage(content: string, option?: any) {
  AntMessage.info({ content, ...option });
}

// 修改通知提示为 Ant Design Vue 的 notification
export function notification(content: string) {
  AntNotification.open({ message: content });
}
export function successNotification(content: string) {
  AntNotification.success({ message: content });
}
export function warningNotification(content: string) {
  AntNotification.warning({ message: content });
}
export function errorNotification(content: string) {
  AntNotification.error({ message: content });
}
export function infoNotification(content: string) {
  AntNotification.info({ message: content });
}
