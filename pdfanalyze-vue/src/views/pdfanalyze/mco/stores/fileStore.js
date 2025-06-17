import { defineStore } from 'pinia';

export const useFileStore = defineStore('fileMCO', {
  state: () => ({
    fileId: null, // 用于存储文件 ID
  }),
  actions: {
    setFileId(id) {
      this.fileId = id; // 更新文件 ID
    },
  },
});
