import { request } from "/@/utils/service";

export const apiPrefix = "/api/system/system_config/";

export function GetList(query: any) {
  return request({
    url: apiPrefix,
    method: "get",
    params: query,
  });
}

export function SaveContent(data: any) {
  return request({
    url: apiPrefix + "save_content/",
    method: "put",
    data,
  });
}
