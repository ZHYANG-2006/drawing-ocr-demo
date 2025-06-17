import * as api from './api';
import {
    UserPageQuery,
    AddReq,
    DelReq,
    EditReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    dict
} from '@fast-crud/fast-crud';
// import {commonCrudConfig} from "/@/utils/commonCrud";
import {computed,shallowRef} from "vue";
export const createCrudOptions = function ({
                                               crudExpose,
                                               isEcharts,
                                               initChart
                                           }: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        return await api.GetList(query);
    };
    const editRequest = async ({form, row}: EditReq) => {
        form.id = row.id;
        return await api.UpdateObj(form);
    };
    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({form}: AddReq) => {
        return await api.AddObj(form);
    };
    return {
        crudOptions: {
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            actionbar: {
                buttons: {
                    add: {
                        show: true,
                    },
                    showEcharts: {
                        type: 'warning',
                        text: computed(() => {
                            return isEcharts.value ? '隐藏图表' : '显示图表'
                        }),
                        click: () => {
                            isEcharts.value = !isEcharts.value;
                        }
                    }
                },
            },
            rowHandle: {
                fixed: 'right',
                width: 100,
                buttons: {
                    view: {
                        type: 'text',
                    },
                    edit: {
                        show: false,
                    },
                    remove: {
                        show: false,
                    },
                },
            },
            columns: {
                _index: {
                    title: '序号',
                    form: {show: false},
                    column: {
                        //type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                        formatter: (context) => {
                            //计算序号,你可以自定义计算规则，此处为翻页累加
                            let index = context.index ?? 1;
                            let pagination = crudExpose!.crudBinding.value.pagination;
                            return ((pagination!.currentPage ?? 1) - 1) * pagination!.pageSize + index + 1;
                        },
                    },
                },
                search: {
                    title: '关键词',
                    column: {
                        show: false,
                    },
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                            placeholder: '请输入关键词',
                        },
                    },
                    form: {
                        show: false,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                },
                username: {
                    title: '测试自定义组件',
                    dict:dict({
                        url({form}){
                            return  '/api/system/role/'
                        },
                        label:'name',
                        value:'id'
                        }),
                    form: {
                        component: {
                            //局部引用子表格，要用shallowRef包裹
                        }
                    }
                },
                ip: {
                    title: '登录ip',
                    search: {
                        disabled: false,
                    },
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        disabled: true,
                        component: {
                            placeholder: '请输入登录ip',
                        },
                    },
                },
                login_type: {
                    title: '登录类型',
                    type: 'dict-select',
                    search: {
                        disabled: false,
                    },
                    dict: dict({
                        data: [
                            {label: '普通登录', value: 1},
                            {label: '微信扫码登录', value: 2},
                        ],
                    }),
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请选择登录类型',
                        },
                    },
                },
                os: {
                    title: '操作系统',
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入操作系统',
                        },
                    },
                },
                browser: {
                    title: '浏览器名',
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入浏览器名',
                        },
                    },
                },
                agent: {
                    title: 'agent信息',
                    disabled: true,
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入agent信息',
                        },
                    },
                },
                ...commonCrudConfig({
                    create_datetime: {
                        search: true
                    }
                })
            },
        },
    };
};
