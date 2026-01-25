<template>
  <n-config-provider :theme="null">
    <n-message-provider>
      <div id="app">
        <router-view />
      </div>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
// 引入 Naive UI 必需的组件
import { NConfigProvider, NMessageProvider } from 'naive-ui';
// 如果需要中文语言支持，可额外引入（可选）
// import { zhCN, dateZhCN } from 'naive-ui';
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100%;
}
</style>
