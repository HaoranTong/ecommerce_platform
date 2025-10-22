<template>
  <n-layout has-sider class="layout-container">
    <!-- 侧边栏 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      show-trigger
      class="sidebar"
    >
      <div class="logo">
        <h2>电商平台</h2>
      </div>
      <n-menu
        ref="menu"
        :collapsed="false"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="currentRoute.name"
        @update:value="handleMenuSelect"
      />
    </n-layout-sider>

    <!-- 主内容区 -->
    <n-layout class="main-layout">
      <n-layout-header bordered>
        <div class="header">
          <h1>{{ currentPageTitle }}</h1>
        </div>
      </n-layout-header>
      <n-layout-content class="content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { NLayout, NLayoutSider, NLayoutHeader, NLayoutContent, NMenu } from 'naive-ui';
import type { MenuOption } from 'naive-ui';
import { h } from 'vue';

const router = useRouter();
const currentRoute = useRoute();

// 简单的图标渲染函数（实际项目中可以使用真正的图标库）
function renderIcon(iconName: string) {
  // 不显示任何图标文字，只保留图标占位
  return () => {
    return h('div', { style: 'font-size: 16px; text-align: center; width: 16px; height: 16px;' }, '');
  };
}

// 菜单选项
const menuOptions: MenuOption[] = [
  {
    label: '仪表盘',
    key: 'Dashboard',
    icon: renderIcon('dashboard')
  },
  {
    label: '商品管理',
    key: 'ProductList',
    icon: renderIcon('product')
  }
];

// 当前页面标题
const currentPageTitle = computed(() => {
  const currentMenu = menuOptions.find(option => option.key === currentRoute.name);
  return currentMenu ? currentMenu.label : '未知页面';
});

// 处理菜单选择
const handleMenuSelect = (key: string) => {
  router.push({ name: key });
};
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #f5f5f5;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #ddd;
}

.logo h2 {
  margin: 0;
  color: #333;
}

.header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #ddd;
}

.content {
  padding: 24px;
  height: calc(100% - 64px);
  overflow: auto;
}
</style>