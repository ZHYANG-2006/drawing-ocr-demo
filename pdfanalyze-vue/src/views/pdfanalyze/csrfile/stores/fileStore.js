import { defineStore } from 'pinia';

export const useFileStore = defineStore('fileCSR', {
  state: () => ({
    fileId: null, // 用于存储文件 ID
    process: null,
  }),
  actions: {
    setFileId(id) {
      this.fileId = id; // 更新文件 ID
    },
    setProcess(process) {
      this.process = process;
    },
  },
});
