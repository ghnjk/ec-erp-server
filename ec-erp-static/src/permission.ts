import { DialogPlugin, MessagePlugin } from 'tdesign-vue-next';
import NProgress from 'nprogress'; // progress bar
import 'nprogress/nprogress.css'; // progress bar style
import { getPermissionStore, getUserStore } from '@/store';
import router from '@/router';
import { getConstantStore } from '@/store/modules/constant';
import { getGroupInfoStore } from '@/store/modules/groupinfo';

declare global {
  interface Window {
    FTP_EVENT: any;
  }
}

const permissionStore = getPermissionStore();
const userStore = getUserStore();
const constantStore = getConstantStore();
const sleep = (time) =>
  new Promise((resolve) => {
    setTimeout(resolve, time);
  });

NProgress.configure({ showSpinner: false });

const { whiteListRouters } = permissionStore;

router.beforeEach(async (to, from, next) => {
  // eslint-disable-next-line no-restricted-globals
  NProgress.start();
  const { userInfo } = userStore;
  console.log('permission check: userInfo', userInfo, 'to', to);
  const { roles, isAdmin } = userStore;

  if ((roles && roles.length > 0) || isAdmin) {
    // 当已经在页面中, 跳转到其他页面, 会走这个逻辑
    next();
  } else {
    try {
      await userStore.getLoginAccout();

      const { roles, isAdmin, userInfo } = userStore;

      console.log('permission get user info: userInfo', userInfo);
      await permissionStore.initRoutes(roles, isAdmin);
      if ((roles && roles.length > 0) || isAdmin) {
        // 当已经在页面中, 跳转到其他页面, 会走这个逻辑
        next();
      }
    } catch (e) {}
  }
  if (whiteListRouters.includes(to.path)) {
    next();
  } else if (userInfo) {
    const { roles, isAdmin } = userStore;

    if ((roles && roles.length > 0) || isAdmin) {
      // 当已经在页面中, 跳转到其他页面, 会走这个逻辑
      next();
    } else {
      // 浏览器第一次输入url, 会进入这个逻辑
      const authMsg = MessagePlugin.loading({ content: '校验用户权限中...', duration: 0 });
      try {
        await sleep(800);

        await userStore.getLoginAccout();

        const { roles, isAdmin, userInfo } = userStore;

        console.log('permission get user info: userInfo', userInfo);

        await permissionStore.initRoutes(roles, isAdmin);
        if (router.hasRoute(to.name)) {
          next();
        } else {
          next('/');
        }
        MessagePlugin.close(authMsg);
      } catch (error) {
        setTimeout(() => {
          MessagePlugin.closeAll();
          window.location.href = '#/login';
        }, 800);
        NProgress.done();
      }
    }
  } else {
    /* white list router */
    if (whiteListRouters.includes(to.path)) {
      next();
    } else {
      MessagePlugin.error('无用户信息, 请到power平台申请平台权限');
    }

    NProgress.done();
  }
});

router.afterEach(() => {
  NProgress.done();
});
