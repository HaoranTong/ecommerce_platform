import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import ProductList from '../views/ProductList.vue';
import DefaultLayout from '../layouts/DefaultLayout.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
      },
      {
        path: 'products',
        name: 'ProductList',
        component: ProductList,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
