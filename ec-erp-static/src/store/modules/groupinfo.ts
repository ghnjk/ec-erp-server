import { defineStore } from 'pinia';
import { store } from '@/store';
import { queryStaffInfo } from '@/apis/cmdbApis';

export const useGroupInfoStore = defineStore('groupInfo', {
  state: () => ({
    groupStaffInfo: [],
  }),
  actions: {
    async getStaffInfo() {
      try {
        const staffInfo = await queryStaffInfo();
        this.groupStaffInfo = staffInfo.filter((e) => e.mainGroupID === '18532' || e.mainGroupName === '基础平台SRE组');
      } catch (err) {
        console.error(err);
      }
    },
  },
});

export function getGroupInfoStore() {
  return useGroupInfoStore(store);
}
