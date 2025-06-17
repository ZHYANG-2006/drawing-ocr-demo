<template>
  <div class="personal layout-pd">
    <a-row>
      <!-- 个人信息 -->
      <a-col :xs="24" :sm="16">
        <a-card title="个人信息" bordered>
          <div class="personal-user">
            <div class="personal-user-left">
              <avatarSelector
                ref="avatarSelectorRef"
                v-model="selectImgVisible"
                @uploadImg="uploadImg"
              />
            </div>
            <div class="personal-user-right">
              <a-row>
                <a-col :span="24" class="personal-title mb18">
                  {{ currentTime }}，{{ state.personalForm.username }}！
                </a-col>
                <a-col :span="24">
                  <a-row>
                    <a-col :xs="24" :sm="8" class="personal-item mb6">
                      <div class="personal-item-label">昵称：</div>
                      <div class="personal-item-value">
                        {{ state.personalForm.name }}
                      </div>
                    </a-col>
                    <a-col :xs="24" :sm="16" class="personal-item mb6">
                      <div class="personal-item-label">部门：</div>
                      <div class="personal-item-value">
                        <a-tag>{{
                          state.personalForm.dept_info.dept_name
                        }}</a-tag>
                      </div>
                    </a-col>
                  </a-row>
                </a-col>
                <a-col :span="24">
                  <a-row>
                    <a-col :xs="24" :sm="24" class="personal-item mb6">
                      <div class="personal-item-label">角色：</div>
                      <div class="personal-item-value">
                        <a-tag
                          v-for="(item, index) in state.personalForm.role_info"
                          :key="index"
                        >
                          {{ item.name }}
                        </a-tag>
                      </div>
                    </a-col>
                  </a-row>
                </a-col>
              </a-row>
            </div>
          </div>
        </a-card>
      </a-col>

      <!-- 消息通知 -->
      <a-col :xs="24" :sm="8" class="pl15 personal-info">
        <a-card bordered>
          <template #title>
            <span>消息通知</span>
            <a class="personal-info-more" @click="msgMore">更多</a>
          </template>
          <div class="personal-info-box">
            <ul class="personal-info-ul">
              <li
                v-for="(v, k) in state.newsInfoList"
                :key="k"
                class="personal-info-li"
              >
                <div class="personal-info-li-title">
                  [{{ v.creator_name }},{{ v.create_datetime }}] {{ v.title }}
                </div>
              </li>
            </ul>
          </div>
        </a-card>
      </a-col>

      <!-- 更新信息 -->
      <a-col :span="24">
        <a-card title="更新信息" class="mt15 personal-edit">
          <div class="personal-edit-title">基本信息</div>
          <a-form
            ref="userInfoFormRef"
            :model="state.personalForm"
            :rules="rules"
            layout="inline"
            class="mt35 mb35"
          >
            <a-row :gutter="35">
              <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb20">
                <a-form-item label="昵称" prop="name">
                  <a-input
                    v-model="state.personalForm.name"
                    placeholder="请输入昵称"
                    allow-clear
                  />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb20">
                <a-form-item label="邮箱">
                  <a-input
                    v-model="state.personalForm.email"
                    placeholder="请输入邮箱"
                    allow-clear
                  />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb20">
                <a-form-item label="手机" prop="mobile">
                  <a-input
                    v-model="state.personalForm.mobile"
                    placeholder="请输入手机"
                    allow-clear
                  />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb20">
                <a-form-item label="性别">
                  <a-select
                    v-model="state.personalForm.gender"
                    placeholder="请选择性别"
                    allow-clear
                  >
                    <a-select-option
                      v-for="(item, index) in genderList"
                      :key="index"
                      :value="item.value"
                    >
                      {{ item.label }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
                <a-form-item>
                  <a-button type="primary" @click="submitForm">
                    更新个人信息
                  </a-button>
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
          <div class="personal-edit-title mb15">账号安全</div>
          <div class="personal-edit-safe-box">
            <div class="personal-edit-safe-item">
              <div class="personal-edit-safe-item-left">
                <div class="personal-edit-safe-item-left-label">账户密码</div>
                <div class="personal-edit-safe-item-left-value">
                  当前密码强度：强
                </div>
              </div>
              <div class="personal-edit-safe-item-right">
                <a-button type="link" @click="passwordFormShow = true">
                  立即修改
                </a-button>
              </div>
            </div>
          </div>
          <div class="personal-edit-safe-box">
            <div class="personal-edit-safe-item">
              <div class="personal-edit-safe-item-left">
                <div class="personal-edit-safe-item-left-label">手机</div>
                <div class="personal-edit-safe-item-left-value">
                  已注册手机：{{ state.personalForm.mobile }}
                </div>
              </div>
            </div>
          </div>

          <div class="personal-edit-safe-box">
            <div class="personal-edit-safe-item">
              <div class="personal-edit-safe-item-left">
                <div class="personal-edit-safe-item-left-label">绑定邮箱</div>
                <div class="personal-edit-safe-item-left-value">
                  已绑定邮箱：{{ state.personalForm.email }}
                </div>
              </div>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 密码修改 -->
    <a-modal v-model="passwordFormShow" title="密码修改">
      <a-form
        ref="userPasswordFormRef"
        :model="userPasswordInfo"
        :rules="passwordRules"
        layout="vertical"
      >
        <a-form-item label="原密码" required prop="oldPassword">
          <a-input
            v-model="userPasswordInfo.oldPassword"
            placeholder="请输入原始密码"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="新密码" required prop="newPassword">
          <a-input
            v-model="userPasswordInfo.newPassword"
            type="password"
            placeholder="请输入新密码"
            allow-clear
            show-password
          />
        </a-form-item>
        <a-form-item label="确认密码" required prop="newPassword2">
          <a-input
            v-model="userPasswordInfo.newPassword2"
            type="password"
            placeholder="请再次输入新密码"
            allow-clear
            show-password
          />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button type="primary" @click="settingPassword">提交</a-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup lang="ts" name="personal">
  import {
    reactive,
    computed,
    onMounted,
    ref,
    defineAsyncComponent,
  } from 'vue';
  import { formatAxis } from '/@/utils/formatTime';
  import * as api from './api';
  import { message } from 'ant-design-vue'; // 使用 Ant Design Vue 的消息组件
  import { getBaseURL } from '/@/utils/baseUrl';
  import { Session } from '/@/utils/storage';
  import { useRouter } from 'vue-router';
  import { useUserInfo } from '/@/stores/userInfo';
  import { dictionary } from '/@/utils/dictionary';
  import { hashStr } from 'ts-md5';

  const router = useRouter();

  // 头像裁剪组件
  const avatarSelector = defineAsyncComponent(
    () => import('/@/components/avatarSelector/index.vue'),
  );
  const avatarSelectorRef = ref(null);

  // 当前时间提示语
  const currentTime = computed(() => {
    return formatAxis(new Date());
  });

  const userInfoFormRef = ref();

  const rules = reactive({
    name: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
    mobile: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确手机号' }],
  });

  const selectImgVisible = ref(false);

  const state = reactive<PersonalState>({
    newsInfoList: [],
    personalForm: {
      avatar: '',
      username: '',
      name: '',
      email: '',
      mobile: '',
      gender: '',
      dept_info: {
        dept_id: 0,
        dept_name: '',
      },
      role_info: [
        {
          id: 0,
          name: '',
        },
      ],
    },
  });

  /**
   * 跳转消息中心
   */
  const msgMore = () => {
    router.push({ path: '/messageCenter' });
  };

  const genderList = ref();
  /**
   * 获取用户个人信息
   */
  const getUserInfo = function () {
    api.GetUserInfo({}).then((res: any) => {
      const { data } = res;
      genderList.value = dictionary('gender', undefined);
      state.personalForm.avatar = data.avatar || '';
      state.personalForm.username = data.username || '';
      state.personalForm.name = data.name || '';
      state.personalForm.email = data.email || '';
      state.personalForm.mobile = data.mobile || '';
      state.personalForm.gender = data.gender;
      state.personalForm.dept_info.dept_name = data.dept_info.dept_name || '';
      state.personalForm.role_info = data.role_info || [];
    });
  };

  /**
   * 更新用户信息
   */
  const submitForm = async () => {
    if (!userInfoFormRef.value) return;
    await userInfoFormRef.value.validate((valid: any, fields: any) => {
      if (valid) {
        api.updateUserInfo(state.personalForm).then(() => {
          message.success('更新成功');
          getUserInfo();
        });
      } else {
        message.error('表单验证失败,请检查~');
      }
    });
  };

  /**
   * 获取消息通知
   */
  const getMsg = () => {
    api.GetSelfReceive({}).then((res: any) => {
      const { data } = res;
      state.newsInfoList = data || [];
    });
  };

  onMounted(() => {
    getUserInfo();
    getMsg();
  });

  /**************************密码修改部分************************/
  const passwordFormShow = ref(false);
  const userPasswordFormRef = ref();

  const userPasswordInfo = reactive({
    oldPassword: '',
    newPassword: '',
    newPassword2: '',
  });

  const validatePass = (
    rule: any,
    value: string,
    callback: (arg0: Error | undefined) => void,
  ) => {
    const pwdRegex = new RegExp('(?=.*[0-9])(?=.*[a-zA-Z]).{8,30}');
    if (value === '') {
      callback(new Error('请输入密码'));
    } else if (value === userPasswordInfo.oldPassword) {
      callback(new Error('原密码与新密码一致'));
    } else if (!pwdRegex.test(value)) {
      callback(new Error('您的密码复杂度太低(密码中必须包含字母、数字)'));
    } else {
      if (userPasswordInfo.newPassword2 !== '') {
        userPasswordFormRef.value.validateField('newPassword2');
      }
      callback(undefined);
    }
  };

  const validatePass2 = (
    rule: any,
    value: string,
    callback: (arg0: Error | undefined) => void,
  ) => {
    if (value === '') {
      callback(new Error('请再次输入密码'));
    } else if (value !== userPasswordInfo.newPassword) {
      callback(new Error('两次输入密码不一致!'));
    } else {
      callback(undefined);
    }
  };

  const passwordRules = reactive({
    oldPassword: [
      {
        required: true,
        message: '请输入原密码',
        trigger: 'blur',
      },
    ],
    newPassword: [{ validator: validatePass, trigger: 'blur' }],
    newPassword2: [{ validator: validatePass2, trigger: 'blur' }],
  });

  /**
   * 重新设置密码
   */
  const settingPassword = () => {
    userPasswordFormRef.value.validate((valid: any) => {
      if (valid) {
        api.UpdatePassword(userPasswordInfo).then(() => {
          message.success('密码修改成功');
          setTimeout(() => {
            Session.remove('token');
            router.push('/login');
          }, 1000);
        });
      } else {
        message.error('表单校验失败，请检查');
      }
    });
  };

  const uploadImg = (data: any) => {
    const formdata = new FormData();
    formdata.append('file', data);
    api.uploadAvatar(formdata).then((res: any) => {
      if (res.code === 2000) {
        selectImgVisible.value = false;
        let avatarUrl = res.data.url;
        if (avatarUrl.startsWith('/')) {
          avatarUrl = avatarUrl.substring(1);
        }
        state.personalForm.avatar = getBaseURL() + avatarUrl;
        api.updateUserInfo(state.personalForm).then(() => {
          message.success('更新成功');
          getUserInfo();
          useUserInfo().updateUserInfos();
          // @ts-ignore
          avatarSelectorRef.value.updateAvatar(state.personalForm.avatar);
        });
      }
    });
  };
</script>

<style scoped lang="scss">
  @import '/@/theme/mixins/index.scss';

  .personal {
    .personal-user {
      height: 130px;
      display: flex;
      align-items: center;

      .personal-user-left {
        width: 100px;
        height: 130px;
        border-radius: 3px;

        :deep(.ant-upload) {
          height: 100%;
        }

        .personal-user-left-upload {
          img {
            width: 100%;
            height: 100%;
            border-radius: 3px;
          }

          &:hover {
            img {
              animation: logoAnimation 0.3s ease-in-out;
            }
          }
        }
      }

      .personal-user-right {
        flex: 1;
        padding: 0 15px;

        .personal-title {
          font-size: 18px;
          @include text-ellipsis(1);
        }

        .personal-item {
          display: flex;
          align-items: center;
          font-size: 13px;

          .personal-item-label {
            color: var(--ant-text-color-secondary);
            @include text-ellipsis(1);
          }

          .personal-item-value {
            @include text-ellipsis(1);
          }
        }
      }
    }

    .personal-info {
      .personal-info-more {
        float: right;
        color: var(--ant-text-color-secondary);
        font-size: 13px;

        &:hover {
          color: var(--ant-color-primary);
          cursor: pointer;
        }
      }

      .personal-info-box {
        height: 130px;
        overflow: hidden;

        .personal-info-ul {
          list-style: none;

          .personal-info-li {
            font-size: 13px;
            padding-bottom: 10px;

            .personal-info-li-title {
              display: inline-block;
              @include text-ellipsis(1);
              color: var(--ant-text-color-secondary);
              text-decoration: none;

              &:hover {
                color: var(--ant-color-primary);
                cursor: pointer;
              }
            }
          }
        }
      }
    }

    .personal-recommend-row {
      .personal-recommend-col {
        .personal-recommend {
          position: relative;
          height: 100px;
          border-radius: 3px;
          overflow: hidden;
          cursor: pointer;

          &:hover {
            i {
              right: 0px !important;
              bottom: 0px !important;
              transition: all ease 0.3s;
            }
          }

          i {
            position: absolute;
            right: -10px;
            bottom: -10px;
            font-size: 70px;
            transform: rotate(-30deg);
            transition: all ease 0.3s;
          }

          .personal-recommend-auto {
            padding: 15px;
            position: absolute;
            left: 0;
            top: 5%;
            color: var(--next-color-white);

            .personal-recommend-msg {
              font-size: 12px;
              margin-top: 10px;
            }
          }
        }
      }
    }

    .personal-edit {
      .personal-edit-title {
        position: relative;
        padding-left: 10px;
        color: var(--ant-text-color-regular);

        &::after {
          content: '';
          width: 2px;
          height: 10px;
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          background: var(--ant-color-primary);
        }
      }

      .personal-edit-safe-box {
        border-bottom: 1px solid var(--ant-border-color-light, #ebeef5);
        padding: 15px 0;

        .personal-edit-safe-item {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: space-between;

          .personal-edit-safe-item-left {
            flex: 1;
            overflow: hidden;

            .personal-edit-safe-item-left-label {
              color: var(--ant-text-color-regular);
              margin-bottom: 5px;
            }

            .personal-edit-safe-item-left-value {
              color: var(--ant-text-color-secondary);
              @include text-ellipsis(1);
              margin-right: 15px;
            }
          }
        }

        &:last-of-type {
          padding-bottom: 0;
          border-bottom: none;
        }
      }
    }
  }
</style>
