<template>
  <div class="layout-breadcrumb-seting">
    <a-drawer
      :visible="getThemeConfig.isDrawer"
      :title="$t('message.layout.configTitle')"
      placement="right"
      :width="560"
      :destroy-on-close="true"
      @close="onDrawerClose"
    >
      <PerfectScrollbar class="layout-breadcrumb-setting-bar">
        <!-- 全局主题 -->
        <a-divider>
          {{ $t('message.layout.oneTitle') }}
        </a-divider>
        <div class="layout-breadcrumb-setting-bar-flex">
          <div class="layout-breadcrumb-setting-bar-flex-label">Primary</div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.primary"
              @change="onColorPickerChange"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-setting-bar-flex mt15">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.fourIsDark') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isIsDark"
              size="small"
              @change="onAddDarkChange"
            />
          </div>
        </div>

        <!-- 顶栏设置 -->
        <a-divider>{{ $t('message.layout.twoTopTitle') }}</a-divider>
        <div class="layout-breadcrumb-setting-bar-flex">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoTopBar') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.topBar"
              @change="onBgColorPickerChange('topBar')"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-setting-bar-flex">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoTopBarColor') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.topBarColor"
              @change="onBgColorPickerChange('topBarColor')"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-setting-bar-flex mt10">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoIsTopBarColorGradual') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isTopBarColorGradual"
              size="small"
              @change="onTopBarGradualChange"
            />
          </div>
        </div>

        <!-- 菜单设置 -->
        <a-divider>{{ $t('message.layout.twoMenuTitle') }}</a-divider>
        <div class="layout-breadcrumb-setting-bar-flex">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoMenuBar') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.menuBar"
              @change="onBgColorPickerChange('menuBar')"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-setting-bar-flex">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoMenuBarColor') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.menuBarColor"
              @change="onBgColorPickerChange('menuBarColor')"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-setting-bar-flex">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoMenuBarActiveColor') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.menuBarActiveColor"
              show-alpha
              @change="onBgColorPickerChange('menuBarActiveColor')"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-setting-bar-flex mt14">
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoIsMenuBarColorGradual') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isMenuBarColorGradual"
              size="small"
              @change="onMenuBarGradualChange"
            />
          </div>
        </div>

        <!-- 分栏设置 -->
        <a-divider
          :style="{ opacity: getThemeConfig.layout !== 'columns' ? 0.5 : 1 }"
        >
          {{ $t('message.layout.twoColumnsTitle') }}
        </a-divider>
        <div
          class="layout-breadcrumb-setting-bar-flex"
          :style="{ opacity: getThemeConfig.layout !== 'columns' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.twoColumnsMenuBar') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.columnsMenuBar"
              :disabled="getThemeConfig.layout !== 'columns'"
              @change="onBgColorPickerChange('columnsMenuBar')"
            />
          </div>
        </div>

        <div
          class="layout-breadcrumb-seting-bar-flex"
          :style="{ opacity: getThemeConfig.layout !== 'columns' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.twoColumnsMenuBarColor') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <ChromePicker
              v-model="getThemeConfig.columnsMenuBarColor"
              :disabled="getThemeConfig.layout !== 'columns'"
              @change="onBgColorPickerChange('columnsMenuBarColor')"
            />
          </div>
        </div>
        <div
          class="layout-breadcrumb-seting-bar-flex mt14"
          :style="{ opacity: getThemeConfig.layout !== 'columns' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.twoIsColumnsMenuBarColorGradual') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isColumnsMenuBarColorGradual"
              :disabled="getThemeConfig.layout !== 'columns'"
              size="small"
              @change="onColumnsMenuBarGradualChange"
            />
          </div>
        </div>
        <div
          class="layout-breadcrumb-seting-bar-flex mt14"
          :style="{ opacity: getThemeConfig.layout !== 'columns' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.twoIsColumnsMenuHoverPreload') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isColumnsMenuHoverPreload"
              :disabled="getThemeConfig.layout !== 'columns'"
              size="small"
              @change="onColumnsMenuHoverPreloadChange"
            />
          </div>
        </div>

        <!-- 界面设置 -->
        <a-divider>{{ $t('message.layout.threeTitle') }}</a-divider>
        <div
          class="layout-breadcrumb-seting-bar-flex"
          :style="{ opacity: getThemeConfig.layout === 'transverse' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.threeIsCollapse') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isCollapse"
              :disabled="getThemeConfig.layout === 'transverse'"
              size="small"
              @change="onThemeConfigChange"
            />
          </div>
        </div>
        <div
          class="layout-breadcrumb-seting-bar-flex mt15"
          :style="{ opacity: getThemeConfig.layout === 'transverse' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.threeIsUniqueOpened') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isUniqueOpened"
              :disabled="getThemeConfig.layout === 'transverse'"
              size="small"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.threeIsFixedHeader') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isFixedHeader"
              size="small"
              @change="onIsFixedHeaderChange"
            />
          </div>
        </div>
        <div
          class="layout-breadcrumb-seting-bar-flex mt15"
          :style="{ opacity: getThemeConfig.layout !== 'classic' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.threeIsClassicSplitMenu') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isClassicSplitMenu"
              :disabled="getThemeConfig.layout !== 'classic'"
              size="small"
              @change="onClassicSplitMenuChange"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.threeIsLockScreen') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isLockScreen"
              size="small"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>
        <div class="layout-breadcrumb-seting-bar-flex mt11">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.threeLockScreenTime') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-input-number
              v-model="getThemeConfig.lockScreenTime"
              controls-position="right"
              :min="1"
              :max="9999"
              size="default"
              style="width: 90px"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>

        <!-- 界面显示 -->
        <a-divider>{{ $t('message.layout.fourTitle') }}</a-divider>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsShowLogo') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isShowLogo"
              size="small"
              @change="onIsShowLogoChange"
            />
          </div>
        </div>

        <div
          class="layout-breadcrumb-seting-bar-flex mt15"
          :style="{
            opacity:
              getThemeConfig.layout === 'classic' ||
              getThemeConfig.layout === 'transverse'
                ? 0.5
                : 1,
          }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsBreadcrumb') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isBreadcrumb"
              :disabled="
                getThemeConfig.layout === 'classic' ||
                getThemeConfig.layout === 'transverse'
              "
              size="small"
              @change="onIsBreadcrumbChange"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsBreadcrumbIcon') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isBreadcrumbIcon"
              size="small"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsTagsview') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isTagsview"
              size="small"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsTagsviewIcon') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isTagsviewIcon"
              size="small"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsCacheTagsView') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isCacheTagsView"
              size="small"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>

        <div
          class="layout-breadcrumb-seting-bar-flex mt15"
          :style="{ opacity: state.isMobile ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsSortableTagsView') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isSortableTagsView"
              :disabled="state.isMobile"
              size="small"
              @change="onSortableTagsViewChange"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsShareTagsView') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isShareTagsView"
              size="small"
              @change="onShareTagsViewChange"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsFooter') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isFooter"
              size="small"
              @change="setLocalThemeConfig"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsGrayscale') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isGrayscale"
              size="small"
              @change="onAddFilterChange('grayscale')"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsInvert') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isInvert"
              size="small"
              @change="onAddFilterChange('invert')"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourIsWartermark') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-switch
              v-model="getThemeConfig.isWartermark"
              size="small"
              @change="onWartermarkChange"
            />
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt14">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fourWartermarkText') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-input
              v-model="getThemeConfig.wartermarkText"
              size="default"
              style="width: 90px"
              @input="onWartermarkTextInput"
            />
          </div>
        </div>

        <!-- 其它设置 -->
        <a-divider>{{ $t('message.layout.fiveTitle') }}</a-divider>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fiveTagsStyle') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-select
              v-model="getThemeConfig.tagsStyle"
              placeholder="请选择"
              size="default"
              style="width: 90px"
              @change="setLocalThemeConfig"
            >
              <a-select-option value="tags-style-one">风格1</a-select-option>
              <a-select-option value="tags-style-four">风格4</a-select-option>
              <a-select-option value="tags-style-five">风格5</a-select-option>
            </a-select>
          </div>
        </div>

        <div class="layout-breadcrumb-seting-bar-flex mt15">
          <div class="layout-breadcrumb-seting-bar-flex-label">
            {{ $t('message.layout.fiveAnimation') }}
          </div>
          <div class="layout-breadcrumb-seting-bar-flex-value">
            <a-select
              v-model="getThemeConfig.animation"
              placeholder="请选择"
              size="default"
              style="width: 90px"
              @change="setLocalThemeConfig"
            >
              <a-select-option value="slide-right">slide-right</a-select-option>
              <a-select-option value="slide-left">slide-left</a-select-option>
              <a-select-option value="opacitys">opacitys</a-select-option>
            </a-select>
          </div>
        </div>

        <div
          class="layout-breadcrumb-setting-bar-flex mt15"
          :style="{ opacity: getThemeConfig.layout !== 'columns' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.fiveColumnsAsideStyle') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <a-select
              v-model="getThemeConfig.columnsAsideStyle"
              placeholder="请选择"
              style="width: 90px"
              :disabled="getThemeConfig.layout !== 'columns'"
              @change="setLocalThemeConfig"
            >
              <a-select-option value="columns-round">圆角</a-select-option>
              <a-select-option value="columns-card">卡片</a-select-option>
            </a-select>
          </div>
        </div>

        <div
          class="layout-breadcrumb-setting-bar-flex mt15 mb27"
          :style="{ opacity: getThemeConfig.layout !== 'columns' ? 0.5 : 1 }"
        >
          <div class="layout-breadcrumb-setting-bar-flex-label">
            {{ $t('message.layout.fiveColumnsAsideLayout') }}
          </div>
          <div class="layout-breadcrumb-setting-bar-flex-value">
            <a-select
              v-model="getThemeConfig.columnsAsideLayout"
              placeholder="请选择"
              style="width: 90px"
              :disabled="getThemeConfig.layout !== 'columns'"
              @change="setLocalThemeConfig"
            >
              <a-select-option value="columns-horizontal">水平</a-select-option>
              <a-select-option value="columns-vertical">垂直</a-select-option>
            </a-select>
          </div>
        </div>

        <!-- 布局切换 -->
        <a-divider orientation="left">{{
          $t('message.layout.sixTitle')
        }}</a-divider>
        <div class="layout-drawer-content-flex">
          <!-- defaults 布局 -->
          <div
            class="layout-drawer-content-item"
            @click="onSetLayout('defaults')"
          >
            <section
              class="el-container el-circular"
              :class="{
                'drawer-layout-active': getThemeConfig.layout === 'defaults',
              }"
            >
              <aside class="el-aside" style="width: 20px"></aside>
              <section class="el-container is-vertical">
                <header class="el-header" style="height: 10px"></header>
                <main class="el-main"></main>
              </section>
            </section>
            <div
              class="layout-tips-warp"
              :class="{
                'layout-tips-warp-active': getThemeConfig.layout === 'defaults',
              }"
            >
              <div class="layout-tips-box">
                <p class="layout-tips-txt">
                  {{ $t('message.layout.sixDefaults') }}
                </p>
              </div>
            </div>
          </div>

          <!-- classic 布局 -->
          <div
            class="layout-drawer-content-item"
            @click="onSetLayout('classic')"
          >
            <section
              class="el-container is-vertical el-circular"
              :class="{
                'drawer-layout-active': getThemeConfig.layout === 'classic',
              }"
            >
              <header class="el-header" style="height: 10px"></header>
              <section class="el-container">
                <aside class="el-aside" style="width: 20px"></aside>
                <section class="el-container is-vertical">
                  <main class="el-main"></main>
                </section>
              </section>
            </section>
            <div
              class="layout-tips-warp"
              :class="{
                'layout-tips-warp-active': getThemeConfig.layout === 'classic',
              }"
            >
              <div class="layout-tips-box">
                <p class="layout-tips-txt">
                  {{ $t('message.layout.sixClassic') }}
                </p>
              </div>
            </div>
          </div>

          <!-- transverse 布局 -->
          <div
            class="layout-drawer-content-item"
            @click="onSetLayout('transverse')"
          >
            <section
              class="el-container is-vertical el-circular"
              :class="{
                'drawer-layout-active': getThemeConfig.layout === 'transverse',
              }"
            >
              <header class="el-header" style="height: 10px"></header>
              <section class="el-container">
                <section class="el-container is-vertical">
                  <main class="el-main"></main>
                </section>
              </section>
            </section>
            <div
              class="layout-tips-warp"
              :class="{
                'layout-tips-warp-active':
                  getThemeConfig.layout === 'transverse',
              }"
            >
              <div class="layout-tips-box">
                <p class="layout-tips-txt">
                  {{ $t('message.layout.sixTransverse') }}
                </p>
              </div>
            </div>
          </div>

          <!-- columns 布局 -->
          <div
            class="layout-drawer-content-item"
            @click="onSetLayout('columns')"
          >
            <section
              class="el-container el-circular"
              :class="{
                'drawer-layout-active': getThemeConfig.layout === 'columns',
              }"
            >
              <aside class="el-aside-dark" style="width: 10px"></aside>
              <aside class="el-aside" style="width: 20px"></aside>
              <section class="el-container is-vertical">
                <header class="el-header" style="height: 10px"></header>
                <main class="el-main"></main>
              </section>
            </section>
            <div
              class="layout-tips-warp"
              :class="{
                'layout-tips-warp-active': getThemeConfig.layout === 'columns',
              }"
            >
              <div class="layout-tips-box">
                <p class="layout-tips-txt">
                  {{ $t('message.layout.sixColumns') }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="copy-config">
          <a-alert
            :message="$t('message.layout.tipText')"
            type="warning"
            show-icon
            :closable="false"
          />
          <a-button
            ref="copyConfigBtnRef"
            type="primary"
            @click="onCopyConfigClick"
          >
            <CopyOutlined />
            {{ $t('message.layout.copyText') }}
          </a-button>
          <a-button type="default" @click="onResetConfigClick">
            <ReloadOutlined />
            {{ $t('message.layout.resetText') }}
          </a-button>
        </div>
      </PerfectScrollbar>
    </a-drawer>
  </div>
</template>

<script setup lang="ts" name="layoutBreadcrumbSeting">
  import { nextTick, onUnmounted, onMounted, computed, reactive } from 'vue';
  import { notification } from 'ant-design-vue';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import { useThemeConfig } from '/@/stores/themeConfig';
  import { useChangeColor } from '/@/utils/theme';
  import { verifyAndSpace } from '/@/utils/toolsValidate';
  import { Local } from '/@/utils/storage';
  import Watermark from '/@/utils/wartermark';
  import commonFunction from '/@/utils/commonFunction';
  import other from '/@/utils/other';
  import mittBus from '/@/utils/mitt';
  import { ChromePicker } from 'vue-color';

  // 定义变量内容
  const { locale } = useI18n();
  const storesThemeConfig = useThemeConfig();
  const { themeConfig } = storeToRefs(storesThemeConfig);
  const { copyText } = commonFunction();
  const { getLightColor, getDarkColor } = useChangeColor();
  const state = reactive({
    isMobile: false,
  });

  // 获取布局配置信息
  const getThemeConfig = computed(() => {
    return themeConfig.value;
  });
  // 1、全局主题
  const onColorPickerChange = () => {
    if (!getThemeConfig.value.primary)
      return notification.warning({
        message: '警告',
        description: '全局主题 primary 颜色值不能为空',
      });
    // 颜色加深
    document.documentElement.style.setProperty(
      '--ant-color-primary-dark-2',
      `${getDarkColor(getThemeConfig.value.primary, 0.1)}`,
    );
    document.documentElement.style.setProperty(
      '--ant-color-primary',
      getThemeConfig.value.primary,
    );
    // 颜色变浅
    for (let i = 1; i <= 9; i++) {
      document.documentElement.style.setProperty(
        `--ant-color-primary-light-${i}`,
        `${getLightColor(getThemeConfig.value.primary, i / 10)}`,
      );
    }
    setDispatchThemeConfig();
  };
  // 2、菜单 / 顶栏
  const onBgColorPickerChange = (bg: keyof typeof themeConfig.value) => {
    document.documentElement.style.setProperty(
      `--next-bg-${bg}`,
      String(themeConfig.value[bg]), // 将值转换为字符串
    );
    if (bg === 'menuBar') {
      document.documentElement.style.setProperty(
        `--next-bg-menuBar-light-1`,
        getLightColor(String(getThemeConfig.value.menuBar), 0.05), // 转换为字符串
      );
    }
    onTopBarGradualChange();
    onMenuBarGradualChange();
    onColumnsMenuBarGradualChange();
    setDispatchThemeConfig();
  };

  // 2、菜单 / 顶栏 --> 顶栏背景渐变
  const onTopBarGradualChange = () => {
    setGraduaFun(
      '.layout-navbars-breadcrumb-index',
      getThemeConfig.value.isTopBarColorGradual,
      getThemeConfig.value.topBar,
    );
  };
  // 2、菜单 / 顶栏 --> 菜单背景渐变
  const onMenuBarGradualChange = () => {
    setGraduaFun(
      '.layout-container .ant-aside',
      getThemeConfig.value.isMenuBarColorGradual,
      getThemeConfig.value.menuBar,
    );
  };
  // 2、菜单 / 顶栏 --> 分栏菜单背景渐变
  const onColumnsMenuBarGradualChange = () => {
    setGraduaFun(
      '.layout-container .layout-columns-aside',
      getThemeConfig.value.isColumnsMenuBarColorGradual,
      getThemeConfig.value.columnsMenuBar,
    );
  };
  // 2、菜单 / 顶栏 --> 背景渐变函数
  const setGraduaFun = (el: string, bool: boolean, color: string) => {
    setTimeout(() => {
      const els = document.querySelector(el);
      if (!els) return false;
      document.documentElement.style.setProperty(
        '--ant-menu-bg-color',
        document.documentElement.style.getPropertyValue('--next-bg-menuBar'),
      );
      if (bool)
        els.setAttribute(
          'style',
          `background:linear-gradient(to bottom left , ${color}, ${getLightColor(color, 0.6)}) !important;`,
        );
      else els.setAttribute('style', ``);
      setLocalThemeConfig();
    }, 200);
  };
  // 2、分栏设置 ->
  const onColumnsMenuHoverPreloadChange = () => {
    setLocalThemeConfig();
  };
  // 3、界面设置 --> 菜单水平折叠
  const onThemeConfigChange = () => {
    setDispatchThemeConfig();
  };
  // 3、界面设置 --> 固定 Header
  const onIsFixedHeaderChange = () => {
    getThemeConfig.value.isFixedHeaderChange = getThemeConfig.value
      .isFixedHeader
      ? false
      : true;
    setLocalThemeConfig();
  };
  // 3、界面设置 --> 经典布局分割菜单
  const onClassicSplitMenuChange = () => {
    getThemeConfig.value.isBreadcrumb = false;
    setLocalThemeConfig();
    mittBus.emit('getBreadcrumbIndexSetFilterRoutes');
  };
  // 4、界面显示 --> 侧边栏 Logo
  const onIsShowLogoChange = () => {
    getThemeConfig.value.isShowLogoChange = getThemeConfig.value.isShowLogo
      ? false
      : true;
    setLocalThemeConfig();
  };
  // 4、界面显示 --> 面包屑 Breadcrumb
  const onIsBreadcrumbChange = () => {
    if (getThemeConfig.value.layout === 'classic') {
      getThemeConfig.value.isClassicSplitMenu = false;
    }
    setLocalThemeConfig();
  };
  // 4、界面显示 --> 开启 TagsView 拖拽
  const onSortableTagsViewChange = () => {
    mittBus.emit('openOrCloseSortable');
    setLocalThemeConfig();
  };
  // 4、界面显示 --> 开启 TagsView 共用
  const onShareTagsViewChange = () => {
    mittBus.emit('openShareTagsView');
    setLocalThemeConfig();
  };
  // 4、界面显示 --> 灰色模式/色弱模式
  const onAddFilterChange = (attr: string) => {
    if (attr === 'grayscale') {
      if (getThemeConfig.value.isGrayscale)
        getThemeConfig.value.isInvert = false;
    } else {
      if (getThemeConfig.value.isInvert)
        getThemeConfig.value.isGrayscale = false;
    }
    const cssAttr =
      attr === 'grayscale'
        ? `grayscale(${getThemeConfig.value.isGrayscale ? 1 : 0})`
        : `invert(${getThemeConfig.value.isInvert ? '80%' : '0%'})`;
    const appEle = document.body;
    appEle.setAttribute('style', `filter: ${cssAttr}`);
    setLocalThemeConfig();
  };
  // 4、界面显示 --> 深色模式
  const onAddDarkChange = () => {
    const body = document.documentElement as HTMLElement;
    if (getThemeConfig.value.isIsDark) body.setAttribute('data-theme', 'dark');
    else body.setAttribute('data-theme', '');
  };
  // 4、界面显示 --> 开启水印
  const onWartermarkChange = () => {
    getThemeConfig.value.isWartermark
      ? Watermark.set(getThemeConfig.value.wartermarkText)
      : Watermark.del();
    setLocalThemeConfig();
  };
  // 4、界面显示 --> 水印文案
  const onWartermarkTextInput = (val: string) => {
    getThemeConfig.value.wartermarkText = verifyAndSpace(val);
    if (getThemeConfig.value.wartermarkText === '') return false;
    if (getThemeConfig.value.isWartermark)
      Watermark.set(getThemeConfig.value.wartermarkText);
    setLocalThemeConfig();
  };
  // 5、布局切换
  const onSetLayout = (layout: string) => {
    Local.set('oldLayout', layout);
    if (getThemeConfig.value.layout === layout) return false;
    if (layout === 'transverse') getThemeConfig.value.isCollapse = false;
    getThemeConfig.value.layout = layout;
    getThemeConfig.value.isDrawer = false;
    initLayoutChangeFun();
  };
  // 设置布局切换函数
  const initLayoutChangeFun = () => {
    onBgColorPickerChange('menuBar');
    onBgColorPickerChange('menuBarColor');
    onBgColorPickerChange('menuBarActiveColor');
    onBgColorPickerChange('topBar');
    onBgColorPickerChange('topBarColor');
    onBgColorPickerChange('columnsMenuBar');
    onBgColorPickerChange('columnsMenuBarColor');
  };
  // 关闭弹窗时，初始化变量。变量用于处理 layoutScrollbarRef.value.update() 更新滚动条高度
  const onDrawerClose = () => {
    getThemeConfig.value.isFixedHeaderChange = false;
    getThemeConfig.value.isShowLogoChange = false;
    getThemeConfig.value.isDrawer = false;
    setLocalThemeConfig();
  };
  // 布局配置弹窗打开
  const openDrawer = () => {
    getThemeConfig.value.isDrawer = true;
  };
  // 触发 store 布局配置更新
  const setDispatchThemeConfig = () => {
    setLocalThemeConfig();
    setLocalThemeConfigStyle();
  };
  // 存储布局配置
  const setLocalThemeConfig = () => {
    Local.remove('themeConfig');
    Local.set('themeConfig', getThemeConfig.value);
  };
  // 存储布局配置全局主题样式（html根标签）
  const setLocalThemeConfigStyle = () => {
    Local.set('themeConfigStyle', document.documentElement.style.cssText);
  };
  // 一键复制配置
  const onCopyConfigClick = () => {
    const copyThemeConfig = Local.get('themeConfig');
    copyThemeConfig.isDrawer = false;
    copyText(JSON.stringify(copyThemeConfig)).then(() => {
      getThemeConfig.value.isDrawer = false;
    });
  };
  // 一键恢复默认
  const onResetConfigClick = () => {
    Local.clear();
    window.location.reload();
    // @ts-ignore
    Local.set('version', __VERSION__);
  };
  // 初始化菜单样式等
  const initSetStyle = () => {
    // 2、菜单 / 顶栏 --> 顶栏背景渐变
    onTopBarGradualChange();
    // 2、菜单 / 顶栏 --> 菜单背景渐变
    onMenuBarGradualChange();
    // 2、菜单 / 顶栏 --> 分栏菜单背景渐变
    onColumnsMenuBarGradualChange();
  };
  onMounted(() => {
    nextTick(() => {
      // 判断当前布局是否不相同，不相同则初始化当前布局的样式，防止监听窗口大小改变时，布局配置logo、菜单背景等部分布局失效问题
      if (!Local.get('frequency')) initLayoutChangeFun();
      Local.set('frequency', 1);
      // 监听窗口大小改变，非默认布局，设置成默认布局（适配移动端）
      mittBus.on('layoutMobileResize', (res: LayoutMobileResize) => {
        getThemeConfig.value.layout = res.layout;
        getThemeConfig.value.isDrawer = false;
        initLayoutChangeFun();
        state.isMobile = other.isMobile();
      });
      setTimeout(() => {
        // 默认样式
        onColorPickerChange();
        // 灰色模式
        if (getThemeConfig.value.isGrayscale) onAddFilterChange('grayscale');
        // 色弱模式
        if (getThemeConfig.value.isInvert) onAddFilterChange('invert');
        // 深色模式
        if (getThemeConfig.value.isIsDark) onAddDarkChange();
        // 开启水印
        onWartermarkChange();
        // 语言国际化
        if (Local.get('themeConfig'))
          locale.value = Local.get('themeConfig').globalI18n;
        // 初始化菜单样式等
        initSetStyle();
      }, 100);
    });
  });
  onUnmounted(() => {
    mittBus.off('layoutMobileResize', () => {});
  });

  // 暴露变量
  defineExpose({
    openDrawer,
  });
</script>

<style scoped lang="scss">
  .layout-breadcrumb-seting-bar {
    height: calc(100vh - 50px);
    padding: 0 15px;
    :deep(.ant-scrollbar__view) {
      overflow-x: hidden !important;
    }
    .layout-breadcrumb-seting-bar-flex {
      display: flex;
      align-items: center;
      margin-bottom: 5px;
      &-label {
        flex: 1;
        color: var(--ant-text-color-primary);
      }
    }
    .layout-drawer-content-flex {
      overflow: hidden;
      display: flex;
      flex-wrap: wrap;
      align-content: flex-start;
      margin: 0 -5px;
      .layout-drawer-content-item {
        width: 50%;
        height: 70px;
        cursor: pointer;
        border: 1px solid transparent;
        position: relative;
        padding: 5px;
        .ant-container {
          height: 100%;
          .ant-aside-dark {
            background-color: var(--next-color-seting-header);
          }
          .ant-aside {
            background-color: var(--next-color-seting-aside);
          }
          .ant-header {
            background-color: var(--next-color-seting-header);
          }
          .ant-main {
            background-color: var(--next-color-seting-main);
          }
        }
        .ant-circular {
          border-radius: 2px;
          overflow: hidden;
          border: 1px solid transparent;
          transition: all 0.3s ease-in-out;
        }
        .drawer-layout-active {
          border: 1px solid;
          border-color: var(--ant-color-primary);
        }
        .layout-tips-warp,
        .layout-tips-warp-active {
          transition: all 0.3s ease-in-out;
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          border: 1px solid;
          border-color: var(--ant-color-primary-light-5);
          border-radius: 100%;
          padding: 4px;
          .layout-tips-box {
            transition: inherit;
            width: 30px;
            height: 30px;
            z-index: 9;
            border: 1px solid;
            border-color: var(--ant-color-primary-light-5);
            border-radius: 100%;
            .layout-tips-txt {
              transition: inherit;
              position: relative;
              top: 5px;
              font-size: 12px;
              line-height: 1;
              letter-spacing: 2px;
              white-space: nowrap;
              color: var(--ant-color-primary-light-5);
              text-align: center;
              transform: rotate(30deg);
              left: -1px;
              background-color: var(--next-color-seting-main);
              width: 32px;
              height: 17px;
              line-height: 17px;
            }
          }
        }
        .layout-tips-warp-active {
          border: 1px solid;
          border-color: var(--ant-color-primary);
          .layout-tips-box {
            border: 1px solid;
            border-color: var(--ant-color-primary);
            .layout-tips-txt {
              color: var(--ant-color-primary) !important;
              background-color: var(--next-color-seting-main) !important;
            }
          }
        }
        &:hover {
          .ant-circular {
            transition: all 0.3s ease-in-out;
            border: 1px solid;
            border-color: var(--ant-color-primary);
          }
          .layout-tips-warp {
            transition: all 0.3s ease-in-out;
            border-color: var(--ant-color-primary);
            .layout-tips-box {
              transition: inherit;
              border-color: var(--ant-color-primary);
              .layout-tips-txt {
                transition: inherit;
                color: var(--ant-color-primary) !important;
                background-color: var(--next-color-seting-main) !important;
              }
            }
          }
        }
      }
    }
    .copy-config {
      margin: 10px 0;
      .copy-config-btn {
        width: 100%;
        margin-top: 15px;
      }
      .copy-config-btn-reset {
        width: 100%;
        margin: 10px 0 0;
      }
    }
  }
</style>
