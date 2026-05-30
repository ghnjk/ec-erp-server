import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';

import uniq from 'lodash/uniq';
import baseRouters from './modules/base';
import userRouters from './modules/user';
import { getPermissionStore } from '@/store/modules/permission';

// 动态重定向: 跳转到当前用户第一个有权限访问的路由, 避免写死路径导致无权限用户进入死循环
const redirectToFirstAuthRoute = (): string => {
  try {
    return getPermissionStore().getFirstAuthRoutePath;
  } catch (e) {
    return '/login';
  }
};

// 关于单层路由，meta 中设置 { single: true } 即可为单层路由，{ hidden: true } 即可在侧边栏隐藏该路由

// 存放动态路由
export const asyncRouterList: Array<RouteRecordRaw> = [
  ...baseRouters,
  ...userRouters,
];

// 存放固定的路由
const defaultRouterList: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: redirectToFirstAuthRoute,
  },
  {
    path: '/:w+',
    name: '404Page',
    redirect: redirectToFirstAuthRoute,
  },
];

export const allRoutes = [...defaultRouterList, ...asyncRouterList];

const router = createRouter({
  history: createWebHashHistory(),
  routes: allRoutes,
  scrollBehavior() {
    return {
      el: '#app',
      top: 0,
      behavior: 'smooth',
    };
  },
});

export const getRoutesExpanded = () => {
  const expandedRoutes = [];

  allRoutes.forEach((item) => {
    if (item.meta && item.meta.expanded) {
      expandedRoutes.push(item.path);
    }
    if (item.children && item.children.length > 0) {
      item.children
        .filter((child) => child.meta && child.meta.expanded)
        .forEach((child: RouteRecordRaw) => {
          expandedRoutes.push(item.path);
          expandedRoutes.push(`${item.path}/${child.path}`);
        });
    }
  });
  return uniq(expandedRoutes);
};

export const getActive = (maxLevel = 3): string => {
  const route = router.currentRoute.value;
  if (!route || !route.path) {
    return '';
  }
  return route.path
    .split('/')
    .filter((_item: string, index: number) => index <= maxLevel && index > 0)
    .map((item: string) => `/${item}`)
    .join('');
};

export default router;
