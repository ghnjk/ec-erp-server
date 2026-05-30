import { defineStore } from 'pinia';
import { TOKEN_NAME } from '@/config/global';
import { store } from '@/store';
import { getLoginUserInfo, login } from '@/apis/sysApis';

export interface IRole {
  project: string;
  name: string;
  memo: string;
  level: number;
}

export interface IUserInfo {
  userName: string;
  groupName: string;
  roles: IRole[];
  admin: boolean;
  project_id: string;
}

const InitUserInfo: IUserInfo = {
  userName: '',
  groupName: '',
  roles: [],
  admin: false,
  project_id: '',
};

export const useUserStore = defineStore('user', {
  state: () => ({
    // token: localStorage.getItem(TOKEN_NAME) || 'main_token', // 默认token不走权限
    userInfo: InitUserInfo,
  }),
  getters: {
    roles: (state) => {
      return state.userInfo?.roles;
    },
    isAdmin: (state) => {
      return state.userInfo?.admin;
    },
    userName: (state) => {
      return state.userInfo?.userName;
    },
  },
  actions: {
    async getLoginAccout() {
      try {
        this.userInfo = await getLoginUserInfo();
      } catch (err) {
        console.error(err);
        throw err;
      }
    },
    async login(loginInfo) {
      try {
        this.userInfo = await login(loginInfo);
      } catch (err) {
        console.error(err);
        throw err;
      }
    },
    async logout() {
      localStorage.removeItem(TOKEN_NAME);
      this.token = '';
      this.userInfo = InitUserInfo;
    },
    async removeToken() {
      this.token = '';
    },
  },
});

export function getUserStore() {
  return useUserStore(store);
}
