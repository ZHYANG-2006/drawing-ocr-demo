import { DictOptions } from '/@/types/dictTypes';
import { reactive, UnwrapNestedRefs } from 'vue';

export class Dict<T = any> {
  private _data: T[] = [];
  public loading = false;

  constructor(private options: DictOptions<T>) {}

  get data(): T[] {
    return this._data;
  }

  async loadDict() {
    if (this.options.getData) {
      this.loading = true;
      try {
        this._data = await this.options.getData();
      } finally {
        this.loading = false;
      }
    }
  }
}

export function dict<T = any>(
  config: DictOptions<T>,
): UnwrapNestedRefs<Dict<T>> {
  const dictInstance = reactive(new Dict<T>(config));
  if (config.immediate) {
    dictInstance.loadDict(); // 如果 immediate 为 true，立即加载数据
  }
  return dictInstance as UnwrapNestedRefs<Dict<T>>;
}
