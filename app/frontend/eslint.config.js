/**
 * 文件路径: E:\ecommerce_platform\worktree\feature-web\app\frontend\eslint.config.js
 * 功能说明:
 * 1) 使用 FlatCompat 将旧式 eslintrc/shareable configs 转换为 ESLint Flat Config
 * 2) Vue3 + TypeScript 推荐规则
 * 3) 接入 prettier（关闭与 Prettier 冲突的 ESLint 格式类规则）
 * 4) 针对你当前项目阶段，放宽几条“阻塞开发”的规则（any、{}、单词组件名），并将 unused-vars 降为 warn
 *
 * 使用说明:
 * - 在本目录运行: npx eslint .
 * - 若要自动修复可修复项: npx eslint . --fix
 */

import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FlatCompat } from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 兼容旧版 eslintrc / shareable configs -> Flat Config
const compat = new FlatCompat({
  baseDirectory: __dirname,
});

export default [
  // 忽略不需要 lint 的目录
  {
    ignores: ['node_modules/**', 'dist/**', 'build/**', '.vite/**'],
  },

  // 旧式配置（插件/共享配置）统一走 compat 转换
  ...compat.extends(
    'plugin:vue/vue3-recommended',
    '@vue/eslint-config-typescript/recommended',
    'prettier',
  ),

  // ===== 项目阶段性覆盖：减少阻塞开发的规则（以你当前目标为准）=====
  {
    files: ['**/*.{ts,tsx,vue,d.ts}'],
    rules: {
      // 现阶段允许 any（否则会报大量历史代码错误，阻塞推进）
      '@typescript-eslint/no-explicit-any': 'off',

      // 现阶段允许 {} 类型（d.ts 模板代码里很常见，后续再逐步收紧）
      '@typescript-eslint/ban-types': 'off',

      // 现阶段不强制 Vue 组件名必须多词（Header/Sidebar/Dashboard 会被卡）
      'vue/multi-word-component-names': 'off',

      // 未使用变量先降为警告（不阻塞），以后要全绿再改回 error
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
    },
  },
];
