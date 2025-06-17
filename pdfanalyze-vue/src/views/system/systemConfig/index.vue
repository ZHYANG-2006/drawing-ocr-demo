<template>
  <div class="system-config-page">
    <a-form
      :model="formState"
      label-col="{ span: 6 }"
      wrapper-col="{ span: 12 }"
    >
      <a-form-item
        v-for="item in configList"
        :key="item.id"
        :label="item.title"
      >
        <component
          :is="getComponent(item.form_item_type)"
          v-model:value="formState[item.key]"
          v-model:checked="formState[item.key]"
          :options="item.data_options || []"
        />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="handleSave">保存</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts" name="systemConfig">
import { ref, reactive, onMounted } from "vue";
import { GetList, SaveContent } from "./api";
import { successNotification } from "/@/utils/message";
import { SystemConfigStore } from "/@/stores/systemConfig";

const configList = ref<any[]>([]);
const formState = reactive<Record<string, any>>({});

function getComponent(type: number) {
  switch (type) {
    case 9:
      return "a-switch";
    case 4:
      return "a-select";
    default:
      return "a-input";
  }
}

async function fetchData() {
  const res = await GetList({ parent__isnull: true });
  configList.value = res.data || [];
  configList.value.forEach((item) => {
    formState[item.key] = item.value;
  });
}

async function handleSave() {
  const payload = configList.value.map((item) => ({
    id: item.id,
    key: item.key,
    value: formState[item.key],
  }));
  const ret = await SaveContent(payload);
  if (ret?.code === 2000) {
    successNotification(ret.msg as string);
    SystemConfigStore().getSystemConfigs();
  }
}

onMounted(fetchData);
</script>

<style scoped>
.system-config-page {
  padding: 20px;
  background: #fff;
}
</style>
