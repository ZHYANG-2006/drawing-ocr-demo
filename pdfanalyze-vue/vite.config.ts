import { defineConfig, loadEnv, ConfigEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import Components from 'unplugin-vue-components/vite';
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';
import { resolve } from 'path';
import vueJsx from '@vitejs/plugin-vue-jsx';

export default defineConfig((mode: ConfigEnv) => {
  const env = loadEnv(mode.mode, process.cwd());

  return {
    plugins: [
      vue(),
      vueJsx(),
      Components({
        resolvers: [
          AntDesignVueResolver({
            importStyle: false, // 自动引入 Ant Design Vue 样式
          }),
        ],
      }),
    ],
    esbuild: {
      jsxFactory: 'h',
      jsxFragment: 'Fragment'
    },
    resolve: {
      alias: {
        '/@': resolve(__dirname, 'src'), // 设置别名
        '@views': resolve(__dirname, './src/views'), // 为 views 设置别名
      },
    },
    base: mode.command === 'serve' ? './' : env.VITE_PUBLIC_PATH, // 区分开发环境和生产环境的基础路径
    css: {
      postcss: {
        plugins: [tailwindcss(), autoprefixer()],
      },
    },
    server: {
      host: '0.0.0.0', // 允许外部访问
      port: env.VITE_PORT ? parseInt(env.VITE_PORT) : 3000, // 从环境变量获取端口，默认 3000
      open: true, // 自动打开浏览器
      hmr: {
        overlay: false, // 禁用 HMR 错误的叠加层显示
      },
    },
    build: {
      outDir: env.VITE_DIST_PATH || 'dist', // 输出目录
      chunkSizeWarningLimit: 500, // 提高 chunk size 警告的阈值
      rollupOptions: {
        output: {
          entryFileNames: `assets/[name].[hash].js`,
          chunkFileNames: `assets/[name].[hash].js`,
          assetFileNames: `assets/[name].[hash].[ext]`,
          manualChunks: {
            vue: ['vue', 'vue-router', 'pinia'], // 拆分 vue 相关代码
            antd: ['ant-design-vue'], // 拆分 Ant Design Vue 代码
          },
        },
      },
    },
    define: {
      __VUE_I18N_LEGACY_API__: JSON.stringify(false),
      __VUE_I18N_FULL_INSTALL__: JSON.stringify(false),
      __INTLIFY_PROD_DEVTOOLS__: JSON.stringify(false),
      __VERSION__: JSON.stringify(process.env.npm_package_version),
    },
  };
});
