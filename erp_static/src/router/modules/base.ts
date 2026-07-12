import Layout from '@/layouts/index.vue';
import DashboardIcon from '@/assets/assets-slide-dashboard.svg';
import FormIcon from '@/assets/assets-slide-form.svg';
import ListIcon from '@/assets/assets-slide-list.svg';

import { USER_ROLE_ADMIN, USER_ROLE_SUPPLIER, USER_ROLE_WAREHOUSE } from '@/config/global';

export default [
  {
    path: '/supply',
    component: Layout,
    redirect: '/supply/skuList',
    name: 'supply',
    group: 'supply',
    meta: { title: '供应链', icon: FormIcon, hidden: false },
    children: [
      {
        path: 'supplierList',
        name: 'supplierList',
        component: () => import('@/pages/supply/supplierList.vue'),
        meta: { title: '供应商', roleCode: [USER_ROLE_ADMIN] },
      },
      {
        path: 'skuList',
        name: 'skuList',
        component: () => import('@/pages/supply/skuList.vue'),
        meta: { title: '商品SKU', roleCode: [USER_ROLE_SUPPLIER] },
      },
      {
        path: 'skuPurchasePriceList',
        name: 'skuPurchasePriceList',
        component: () => import('@/pages/supply/skuPurchasePriceList.vue'),
        meta: { title: '采购价', roleCode: [USER_ROLE_ADMIN] },
      },
      {
        path: 'purchaseOrderList',
        name: 'purchaseOrderList',
        component: () => import('@/pages/supply/purchaseOrderList.vue'),
        meta: { title: '采购单', roleCode: [USER_ROLE_SUPPLIER], orderType: 1 },
      },
      {
        path: 'offlineSaleOrderList',
        name: 'offlineSaleOrderList',
        component: () => import('@/pages/supply/purchaseOrderList.vue'),
        meta: { title: '境外线下销售单', roleCode: [USER_ROLE_SUPPLIER], orderType: 2 },
      },
    ],
  },
  {
    path: '/sales',
    component: Layout,
    redirect: '/sales/saleOrderList',
    name: 'sales',
    group: 'sales',
    meta: { title: '销售管理', icon: FormIcon, hidden: false },
    children: [
      {
        path: 'saleOrderList',
        name: 'saleOrderList',
        component: () => import('@/pages/sales/saleOrderList.vue'),
        meta: { title: '销售订单', roleCode: [USER_ROLE_ADMIN, USER_ROLE_SUPPLIER] },
      },
    ],
  },
  {
    path: '/warehouse',
    component: Layout,
    redirect: '/warehouse/printOrder',
    name: 'printOrder',
    group: 'printOrder',
    meta: { title: '仓库管理', icon: DashboardIcon, hidden: false },
    children: [
      {
        path: '/warehouse/printOrder',
        name: 'printOrder',
        component: () => import('@/pages/warehouse/printOrder.vue'),
        meta: { title: '订单打印', icon: ListIcon, roleCode: [USER_ROLE_WAREHOUSE] },
      },
      {
        path: '/warehouse/pickingNote',
        name: 'pickingNote',
        component: () => import('@/pages/warehouse/skuPickingNote.vue'),
        meta: { title: '拣货备注', icon: ListIcon, roleCode: [USER_ROLE_WAREHOUSE] },
      },
      {
        path: '/warehouse/stock',
        name: 'stock',
        component: () => import('@/pages/warehouse/stocktaking.vue'),
        meta: { title: '仓库盘点', icon: ListIcon, roleCode: [USER_ROLE_SUPPLIER] },
      },
    ],
  },
  {
    path: '/dashboard',
    component: Layout,
    redirect: '/dashboard/shopSale',
    name: 'dashboard',
    group: 'dashboard',
    meta: { title: '销售报表', icon: ListIcon, roleCode: [USER_ROLE_ADMIN] , hidden: false },
    children: [
      {
        path: 'shopSale',
        name: 'shopSale',
        component: () => import('@/pages/dashboard/shopSale.vue'),
        meta: { title: '店铺销售报表', roleCode: [USER_ROLE_SUPPLIER] },
      },
      {
        path: 'skuSale',
        name: 'skuSale',
        component: () => import('@/pages/dashboard/skuSale.vue'),
        meta: { title: '商品销售报表', roleCode: [USER_ROLE_SUPPLIER] },
      },
    ],
  },
  {
    path: '/mobile/stocktaking',
    name: 'stocktaking',
    component: () => import('@/pages/warehouse/stocktaking.vue'),
    meta: { title: '仓库盘点', hidden: false, icon: ListIcon, roleCode: [USER_ROLE_SUPPLIER] },
  },
  {
    path: '/system',
    component: Layout,
    name: 'system',
    meta: { title: '系统', hidden: true },
    children: [
      {
        path: 'upSellerManualLogin',
        name: 'UpSellerManualLogin',
        component: () => import('@/pages/system/upSellerManualLogin.vue'),
        meta: {
          title: 'UpSeller人工登录',
          hidden: true,
          roleCode: [USER_ROLE_ADMIN, USER_ROLE_SUPPLIER, USER_ROLE_WAREHOUSE],
        },
      },
    ],
  },
];
