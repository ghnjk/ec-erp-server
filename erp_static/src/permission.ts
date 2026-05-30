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

  // 当前会话已有权限信息, 页面内跳转直接放行 (注意: 每个分支必须保证 next 只被调用一次)
  if ((roles && roles.length > 0) || isAdmin) {
    next();
    return;
  }

  // 白名单路由直接放行
  if (whiteListRouters.includes(to.path)) {
    next();
    return;
  }

  // 首次进入或刷新页面, 需要拉取用户信息并初始化路由权限
  const authMsg = MessagePlugin.loading({ content: '校验用户权限中...', duration: 0 });
  try {
    if (!userInfo) {
      await sleep(800);
    }
    await userStore.getLoginAccout();

    const { roles: newRoles, isAdmin: newIsAdmin, userInfo: newUserInfo } = userStore;
    console.log('permission get user info: userInfo', newUserInfo);

    await permissionStore.initRoutes(newRoles, newIsAdmin);
    MessagePlugin.close(authMsg);

    if ((newRoles && newRoles.length > 0) || newIsAdmin) {
      next(router.hasRoute(to.name) ? undefined : '/');
    } else {
      MessagePlugin.error('无用户信息');
      next(false);
    }
  } catch (error) {
    MessagePlugin.close(authMsg);
    next(false);
    setTimeout(() => {
      MessagePlugin.closeAll();
      window.location.href = '#/login';
    }, 800);
  } finally {
    NProgress.done();
  }
});

router.afterEach(() => {
  NProgress.done();
});
