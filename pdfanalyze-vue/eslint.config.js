import vue from 'eslint-plugin-vue';
import typescript from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser'; // TypeScript 解析器
import prettier from 'eslint-plugin-prettier';
import vueParser from 'vue-eslint-parser';
import { jsx } from 'vue/jsx-runtime'; // Vue 解析器

export default [
  {
    files: ['**/*.{js,mjs,cjs,ts,vue}'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      parser: vueParser, // Vue 解析器
      parserOptions: {
        parser: typescriptParser, // TypeScript 解析器
        ecmaVersion: 12,
        jsx: true,
      },
    },
    plugins: {
      vue,
      jsx,
      '@typescript-eslint': typescript,
      prettier,
    },
    extends: [
      'eslint:recommended',
      'plugin:vue/vue3-recommended',
      'plugin:jsx-a11y/recommended'
    ],
    rules: {
      // TypeScript 规则
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-var-requires': 'error',
      '@typescript-eslint/no-empty-function': 'warn',
      '@typescript-eslint/no-use-before-define': 'off',
      '@typescript-eslint/ban-ts-comment': 'off', // 替代 ban-ts-ignore
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_' },
      ],

      // Vue 相关规则
      'vue/custom-event-name-casing': 'off',
      'vue/attributes-order': 'error',
      'vue/one-component-per-file': 'error',
      'vue/html-closing-bracket-newline': 'error',
      'vue/max-attributes-per-line': 'off',
      'vue/multiline-html-element-content-newline': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      'vue/attribute-hyphenation': 'off',
      'vue/html-self-closing': [
        'error',
        {
          html: {
            void: 'always',
            normal: 'never',
            component: 'always',
          },
        },
      ],
      'vue/no-multiple-template-root': 'off',
      'vue/require-default-prop': 'off',
      'vue/no-v-model-argument': 'off',
      'linebreak-style': ['error', 'windows'],
      // 通用 JavaScript 规则
      'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
      'prefer-const': 'error',
      'no-useless-escape': 'off',
      'no-sparse-arrays': 'error',
      'no-prototype-builtins': 'off',
      'no-constant-condition': 'off',
      'no-restricted-globals': 'error',
      'generator-star-spacing': 'error',
      'no-unreachable': 'error',
      'prettier/prettier': [
        'error',
        {
          // 一行最多 80 个字符，增强代码可读性
          printWidth: 80,
          // 指定每个缩进级别的空格数
          tabWidth: 2,
          // 使用空格缩进行，而不是制表符
          useTabs: false,
          // 在语句末尾打印分号（根据团队习惯）
          semi: true,
          // 使用单引号而不是双引号
          singleQuote: true,
          // 属性需要时加引号
          quoteProps: 'as-needed',
          // 在JSX中使用双引号
          jsxSingleQuote: false,
          // 尾随逗号（推荐全部保留，避免未来的版本控制变化）
          trailingComma: 'all',
          // 在对象字面量括号之间打印空格
          bracketSpacing: true,
          // jsx 标签的反尖括号换行
          jsxBracketSameLine: false,
          // 箭头函数的参数总是加上括号
          arrowParens: 'always',
          // 指定HTML文件的全局空格敏感度
          htmlWhitespaceSensitivity: 'css',
          // Vue 文件中的 <script> 和 <style> 标签内使用缩进
          vueIndentScriptAndStyle: true,
          // 换行符设置为 lf（Linux 和 macOS 标准）
          endOfLine: 'crlf',
        },
      ],
    },
  },
  {
    ignores: [
      '*.sh',
      'node_modules',
      'lib',
      '*.md',
      '*.scss',
      '*.woff',
      '*.ttf',
      '.vscode',
      '.idea',
      'dist',
      'mock',
      'public',
      'bin',
      'build',
      'config',
      'index.html',
      'src/assets',
    ],
  },
];
