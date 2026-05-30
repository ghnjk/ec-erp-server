<template>
  <router-view :class="[mode]" />
</template>
<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

import config from '@/config/style';
import { useSettingStore } from '@/store';

const store = useSettingStore();

const mode = computed(() => {
  return store.displayMode;
});
const router = useRouter();

// eslint-disable-next-line no-restricted-globals
if (self !== top && self.name === 'ftp-aopx') {
  if (window.FTP_EVENT) {
    window.FTP_EVENT.routeChange = router.push;
  }
}

onMounted(() => {
  store.updateConfig({ ...config });
});
</script>
<style lang="less">
#nprogress .bar {
  background: var(--td-brand-color) !important;
}
</style>
