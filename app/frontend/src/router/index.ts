import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  // 更多路由将在后续开发中添加
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;