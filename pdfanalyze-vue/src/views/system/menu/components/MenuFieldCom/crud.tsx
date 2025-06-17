import * as api from './api';
import { ref } from 'vue';
import { auth } from "/@/utils/authFunction";

export const useCrudOptions = () => {
  const selectOptions = ref({ name: null });

  const pageRequest = async (query: any) => {
    if (selectOptions.value.name) {
      return await api.GetList({ menu: selectOptions.value.name });
    }
  };

  const editRequest = async (form: any) => {
    return await api.UpdateObj(form);
  };

  const delRequest = async (id: any) => {
    return await api.DelObj(id);
  };

  const addRequest = async (form: any) => {
    return await api.AddObj(form);
  };

  return {
    pageRequest,
    editRequest,
    delRequest,
    addRequest,
    selectOptions,
  };
};
