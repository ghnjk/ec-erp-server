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

  // 是否为免登录白名单路由 (允许匿名访问)
  const isWhiteList = whiteListRouters.includes(to.path);

  // 首次进入或刷新页面, 需要拉取用户信息并初始化路由权限
  // 注意: 白名单路由也要尝试初始化, 否则已登录用户(如仓库角色首页恰好在白名单内)菜单不会生成
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
      // 已登录用户落在登录页, 或目标路由不可访问时, 跳转到(此时已初始化的)首个有权限页面
      // 注意: 路由级别的重定向先于守卫执行, 那时 routers 还是空, 因此首页/兜底重定向只能算出 /login, 这里再纠正一次
      if (to.path === '/login' || !router.hasRoute(to.name)) {
        next(permissionStore.getFirstAuthRoutePath);
      } else {
        next();
      }
    } else if (isWhiteList) {
      // 无登录态但属于白名单页面, 允许匿名访问
      next();
    } else {
      MessagePlugin.error('无用户信息');
      next(false);
    }
  } catch (error) {
    MessagePlugin.close(authMsg);
    // 拉取用户信息失败时, 白名单页面仍允许匿名访问, 其余跳转登录
    if (isWhiteList) {
      next();
    } else {
      next(false);
      setTimeout(() => {
        MessagePlugin.closeAll();
        window.location.href = '#/login';
      }, 800);
    }
  } finally {
    NProgress.done();
  }
});

router.afterEach(() => {
  NProgress.done();
});
