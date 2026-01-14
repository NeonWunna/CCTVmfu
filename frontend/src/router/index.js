import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../pages/LoginPage.vue';
import CctvMonitoring from '../pages/CctvMonitoring.vue';

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginPage },
    { path: '/monitoring', component: CctvMonitoring },
  ],
});

