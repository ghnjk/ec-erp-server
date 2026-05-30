import { defineStore } from 'pinia';
import { store } from '@/store';

const powerDev = 'https://power-dev.woa.com/v/index/auth?systemId=624&roleId=9012';
const powerOnline = 'https://power.woa.com/v/index/auth?systemId=975&roleId=7985';

const state = {
  env: import.meta.env.MODE || 'development',
  powerDirectUrl: '',
};

export const useConstantStore = defineStore('constant', {
  state: () => state,
  getters: {
    getEnv: (state) => state.env,
    getPowerDirectUrl: (state) => {
      if (state.env !== 'release') {
        return powerDev;
      }
      return powerOnline;
    },
  },
  actions: {},
});

export function getConstantStore() {
  return useConstantStore(store);
}
