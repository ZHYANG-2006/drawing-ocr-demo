<template>
  <a-form
    ref="formRef"
    size="large"
    class="login-content-form"
    :model="state.ruleForm"
    :rules="rules"
    @keyup.enter="loginClick"
  >
    <a-form-item class="login-animation1" name="username">
      <a-input
        v-model:value="state.ruleForm.username"
        :placeholder="$t('message.account.accountPlaceholder1')"
        clearable
        autocomplete="off"
      >
        <template #prefix>
          <UserOutlined />
        </template>
      </a-input>
    </a-form-item>
    <a-form-item class="login-animation2" name="password">
      <a-input-password
        v-model:value="state.ruleForm.password"
        :placeholder="$t('message.account.accountPlaceholder2')"
        :visibility-toggle="false"
      >
        <template #prefix>
          <UserOutlined />
        </template>
        <template #suffix>
          <i
            class="iconfont el-input__icon login-content-password"
            :class="isShowPassword ? 'icon-yincangmima' : 'icon-xianshimima'"
            @click="isShowPassword = !isShowPassword"
          ></i>
        </template>
      </a-input-password>
    </a-form-item>
    <a-form-item v-if="isShowCaptcha" class="login-animation3" name="captcha">
      <a-row>
        <a-col :span="15">
          <a-input
            v-model:value="state.ruleForm.captcha"
            type="text"
            :max-length="4"
            :placeholder="$t('message.account.accountPlaceholder3')"
            clearable
            autocomplete="off"
          >
            <template #prefix>
              <VerificationOutlined />
            </template>
          </a-input>
        </a-col>
        <a-col :span="1" />
        <a-col :span="8">
          <a-button class="login-content-captcha" @click="refreshCaptcha">
            <a-image :src="state.ruleForm.captchaImgBase" />
          </a-button>
        </a-col>
      </a-row>
    </a-form-item>
    <a-form-item class="login-animation4">
      <a-button
        type="primary"
        class="login-content-submit"
        round
        :loading="state.loading.signIn"
        @click="loginClick"
      >
        <span>{{ $t('message.account.accountBtnText') }}</span>
      </a-button>
    </a-form-item>
  </a-form>
</template>

<script lang="ts">
  import {
    toRefs,
    reactive,
    defineComponent,
    computed,
    onMounted,
    ref,
    toRaw,
  } from 'vue';
  import type { Rule } from 'ant-design-vue/es/form';
  import type { UnwrapRef } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { message } from 'ant-design-vue';
  import { useI18n } from 'vue-i18n';
  import Cookies from 'js-cookie';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import { initFrontEndControlRoutes } from '/@/router/frontEnd';
  import { initBackEndControlRoutes } from '/@/router/backEnd';
  import { Session } from '/@/utils/storage';
  import { formatAxis } from '/@/utils/formatTime';
  import { NextLoading } from '/@/utils/loading';
  import * as loginApi from '/@/views/system/login/api';
  import { useUserInfo } from '/@/stores/userInfo';
  import { DictionaryStore } from '/@/stores/dictionary';
  import { SystemConfigStore } from '/@/stores/systemConfig';
  import { hashStr } from 'ts-md5';
  import { errorMessage } from '/@/utils/message';

  export default defineComponent({
    name: 'loginAccount',
    setup() {
      const { t } = useI18n();
      const storesThemeConfig = useThemeConfig();
      const { themeConfig } = storeToRefs(storesThemeConfig);
      const { userInfos } = storeToRefs(useUserInfo());
      const route = useRoute();
      const router = useRouter();
      const state = reactive({
        isShowPassword: false,
        ruleForm: {
          username: '',
          password: '',
          captcha: '',
          captchaKey: '',
          captchaImgBase: '',
        },
        loading: {
          signIn: false,
        },
      });
      const rules: Record<string, Rule[]> = {
        username: [
          {
            required: true,
            message: '请填写账号',
            trigger: 'blur',
          },
        ],
        password: [
          {
            required: true,
            message: '请填写密码',
            trigger: 'blur',
          },
          {
            min: 6,
            message: '密码长度不能少于6个字符',
            trigger: 'blur',
          },
        ],
        captcha: [
          {
            required: true,
            message: '请填写验证码',
            trigger: 'blur',
          },
        ],
      };
      const formRef = ref();
      // 时间获取
      const currentTime = computed(() => {
        return formatAxis(new Date());
      });
      // 是否关闭验证码
      const isShowCaptcha = computed(() => {
        const state = SystemConfigStore().systemConfig['base.captcha_state'][0]
        console.log('Systemstore', state)
        return state;
      });

      const getCaptcha = async () => {
        const ret = await loginApi.getCaptcha();
        state.ruleForm.captchaImgBase = ret.data.image_base;
        state.ruleForm.captchaKey = ret.data.key;
      };
      const refreshCaptcha = async () => {
        state.ruleForm.captcha = '';
        await getCaptcha();
      };
      const loginClick = async () => {
        if (!formRef.value) return;
        const valid = await formRef.value.validate();
        if (valid) {
          try {
            const res = await loginApi.login({ ...state.ruleForm });
            if (res.code === 2000) {
              Session.set('token', res.data.access);
              Cookies.set('username', res.data.name);
              if (!themeConfig.value.isRequestRoutes) {
                initFrontEndControlRoutes();
                loginSuccess();
              } else {
                initBackEndControlRoutes();
                loginSuccess();
              }
            }
          } catch (err) {
            refreshCaptcha();
          }
        } else {
          errorMessage('请填写登录信息');
        }
      };

      const getUserInfo = () => {
        useUserInfo().setUserInfos();
      };

      const loginSuccess = () => {
        getUserInfo();
        DictionaryStore().getSystemDictionarys();
        const currentTimeInfo = currentTime.value;
        if (route.query?.redirect) {
          router.push({
            path: <string>route.query?.redirect,
            query:
              Object.keys(<string>route.query?.params).length > 0
                ? JSON.parse(<string>route.query?.params)
                : '',
          });
        } else {
          router.push('/');
        }
        state.loading.signIn = true;
        const signInText = t('message.signInText');
        message.success(`${currentTimeInfo}，${signInText}`);
        NextLoading.start();
      };

      onMounted(() => {
        getCaptcha();
        SystemConfigStore().getSystemConfigs();
      });

      return {
        refreshCaptcha,
        loginClick,
        loginSuccess,
        isShowCaptcha,
        state,
        formRef,
        rules,
        ...toRefs(state),
      };
    },
  });
</script>
<style scoped lang="scss">
  .login-content-form {
    margin-top: 20px;

    @for $i from 1 through 4 {
      .login-animation#{$i} {
        opacity: 1;
        animation-name: error-num;
        animation-duration: 0.5s;
        animation-fill-mode: forwards;
        animation-delay: calc($i / 10) + s;
      }
    }

    .login-content-password {
      display: inline-block;
      width: 20px;
      cursor: pointer;

      &:hover {
        color: #909399;
      }
    }

    .login-content-captcha {
      width: 100%;
      padding: 0;
      font-weight: bold;
      letter-spacing: 5px;
    }

    .login-content-submit {
      width: 100%;
      letter-spacing: 2px;
      font-weight: 300;
      margin-top: 15px;
    }
  }
</style>
