<template>
  <div :class="layoutCls">
    <t-head-menu :class="menuCls" :theme="theme" :value="active" expand-type="popup">
      <template #logo>
        <span v-if="showLogo" :class="`${prefix}-side-nav-logo-wrapper`" @click="handleNav('/')">
          <component :is="getLogo()" :class="`${prefix}-side-nav-logo-${collapsed ? 't' : 'tdesign'}-logo`" />
        </span>
        <div v-else class="header-operate-left">
          <t-button shape="square" theme="default" variant="text" @click="changeCollapsed">
            <t-icon class="collapsed-icon" name="view-list" />
          </t-button>
        </div>
      </template>
      <div id="projectSelector">
        <span class="label">国家：</span>
        <t-select
          v-model="selectedProject"
          :options="projectOptions"
          placeholder="请选择项目"
          size="medium"
          style="width: 120px"
          @change="handleProjectChange"
        />
      </div>
      <template #operations>
        <div class="operations-container">
          <p v-if="currentEnv !== 'release'" class="env-font">{{ currentEnv }}</p>
          <t-divider layout="vertical" />
          <t-popup expand-animation placement="bottom-right" trigger="click">
            <template #content>
              <div class="erp-status-popup">
                <div class="erp-status-popup-title">后端 ERP 状态</div>
                <div class="erp-status-row">
                  <span class="erp-status-row-label">ERP 类型</span>
                  <span>{{ erpStatusTypeText }}</span>
                </div>
                <div class="erp-status-row">
                  <span class="erp-status-row-label">登录状态</span>
                  <t-tag :theme="erpStatusTagTheme" variant="light">{{ erpStatusLoginText }}</t-tag>
                </div>
                <div class="erp-status-row">
                  <span class="erp-status-row-label">邮箱</span>
                  <span>{{ erpStatus?.email || '-' }}</span>
                </div>
                <div class="erp-status-row">
                  <span class="erp-status-row-label">仓库 ID</span>
                  <span>{{ erpStatus?.warehouse_id || '-' }}</span>
                </div>
                <div class="erp-status-row">
                  <span class="erp-status-row-label">自动登录</span>
                  <span>{{ erpStatus?.auto_login ? '是' : '否' }}</span>
                </div>
                <div class="erp-status-message">{{ erpStatus?.message || erpStatusError || '暂无状态信息' }}</div>
              </div>
            </template>
            <t-button class="erp-status-trigger" :theme="erpStatusTagTheme" variant="text">
              <t-icon v-if="erpStatusLoading" class="erp-status-loading-icon" name="loading" />
              <t-icon v-else name="server" />
              <span class="erp-status-text">{{ erpStatusButtonText }}</span>
            </t-button>
          </t-popup>
          <t-button
            v-if="showUpSellerManualLogin"
            theme="warning"
            variant="text"
            @click="goUpSellerManualLogin"
          >
            人工登陆
          </t-button>
          <menu-content :nav-data="menu.filter((item) => item.group === undefined)" class="header-menu" />
          <t-tooltip content="个人信息" placement="bottom">
            <t-button class="header-user-btn" theme="default" variant="text">
              <template #icon>
                <t-icon class="header-user-avatar" name="user-circle" />

                <!--
                <t-avatar :image="usrImage" :hide-on-load-failed="false" size="small" />
                -->
              </template>

              <div class="header-user-account">{{ userName }}</div>
            </t-button>
          </t-tooltip>
          <t-tooltip content="系统设置" placement="bottom">
            <t-button shape="square" theme="default" variant="text">
              <t-icon name="setting" @click="toggleSettingPanel" />
            </t-button>
          </t-tooltip>
        </div>
      </template>
    </t-head-menu>
  </div>
</template>

<script lang="ts" setup>
import { computed, PropType, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useSettingStore, useUserStore } from '@/store';
import { getActive } from '@/router';
import { prefix } from '@/config/global';
import { MenuRoute } from '@/types/interface';
import { BackendErpStatus, getBackendErpStatus, getLoginUserInfo } from '@/apis/sysApis';

import MenuContent from './MenuContent.vue';
import tLogo from '@/assets/assets-t-logo.svg?component';
import tLogoFull from '@/assets/assets-logo-full.svg?component';

const props = defineProps({
  theme: {
    type: String,
    default: '',
  },
  layout: {
    type: String,
    default: 'top',
  },
  showLogo: {
    type: Boolean,
    default: true,
  },
  menu: {
    type: Array as PropType<MenuRoute[]>,
    default: () => [],
  },
  isFixed: {
    type: Boolean,
    default: false,
  },
  isCompact: {
    type: Boolean,
    default: false,
  },
  maxLevel: {
    type: Number,
    default: 3,
  },
});

const selectedProject = ref('');
const erpStatus = ref<BackendErpStatus | null>(null);
const erpStatusLoading = ref(false);
const erpStatusError = ref('');
const projectOptions = [
  { label: '菲律宾', value: 'philipine' },
  { label: '马来西亚', value: 'malaysia' },
  { label: '印度尼西亚', value: 'indonesia' },
  { label: '泰国', value: 'thailand' },
  { label: '巴西', value: 'brazil' },
];

const handleProjectChange = (value: string) => {
  const urlMap = {
    philipine: 'http://8.210.60.7:2083/index.html',
    malaysia: 'http://8.210.60.7:2080/index.html',
    indonesia: 'http://8.210.60.7:2081/index.html',
    thailand: 'http://8.210.60.7:2082/index.html',
    brazil: 'http://8.210.60.7:2084/index.html',
  };
  const targetUrl = urlMap[value];
  if (targetUrl) {
    window.open(targetUrl, '_self');
  }
};

const { userName } = useUserStore();
const currentEnv = import.meta.env.MODE;
const router = useRouter();
const settingStore = useSettingStore();
const collapsed = computed(() => useSettingStore().isSidebarCompact);

const toggleSettingPanel = () => {
  settingStore.updateConfig({
    showSettingPanel: true,
  });
};

const active = computed(() => getActive());

const formatErpType = (type?: string) => {
  if (type === 'big_seller') return 'BigSeller';
  if (type === 'up_seller') return 'UpSeller';
  return type || '-';
};

const erpStatusTypeText = computed(() => formatErpType(erpStatus.value?.erp_type));
const erpStatusLoginText = computed(() => {
  if (erpStatusLoading.value) return '检测中';
  if (!erpStatus.value) return erpStatusError.value ? '检测失败' : '未检测';
  return erpStatus.value.is_login ? '已登录' : '未登录';
});
const erpStatusTagTheme = computed(() => {
  if (erpStatusLoading.value) return 'default';
  if (!erpStatus.value) return erpStatusError.value ? 'danger' : 'default';
  if (!erpStatus.value.is_login) return 'danger';
  return 'success';
});
const erpStatusButtonText = computed(() => {
  if (erpStatusLoading.value) return 'ERP 检测中';
  if (!erpStatus.value) return erpStatusError.value ? 'ERP 检测失败' : 'ERP 未检测';
  return `${erpStatusTypeText.value} · ${erpStatusLoginText.value}`;
});

const showUpSellerManualLogin = computed(() => {
  return Boolean(
    erpStatus.value
    && erpStatus.value.erp_type === 'up_seller'
    && !erpStatus.value.is_login,
  );
});

const goUpSellerManualLogin = () => {
  router.push({ name: 'UpSellerManualLogin' });
};

const refreshErpStatus = async () => {
  if (erpStatusLoading.value) return;
  erpStatusLoading.value = true;
  erpStatusError.value = '';
  try {
    erpStatus.value = await getBackendErpStatus();
  } catch (error) {
    erpStatus.value = null;
    erpStatusError.value = `${error}`;
    console.error('获取后端 ERP 状态失败:', error);
  } finally {
    erpStatusLoading.value = false;
  }
};

// 获取用户信息并设置默认项目，登录态确认后自动检测后端 ERP 状态
const initializeProject = async () => {
  try {
    const res: any = await getLoginUserInfo();
    selectedProject.value = res.project_id;
    refreshErpStatus();
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
};

onMounted(() => {
  initializeProject();
});

const layoutCls = computed(() => [`${prefix}-header-layout`]);

const menuCls = computed(() => {
  const { isFixed, layout, isCompact } = props;
  return [
    {
      [`${prefix}-header-menu`]: !isFixed,
      [`${prefix}-header-menu-fixed`]: isFixed,
      [`${prefix}-header-menu-fixed-side`]: layout === 'side' && isFixed,
      [`${prefix}-header-menu-fixed-side-compact`]: layout === 'side' && isFixed && isCompact,
    },
  ];
});
const getLogo = () => {
  if (collapsed.value) return tLogo;
  return tLogoFull;
};

const changeCollapsed = () => {
  settingStore.updateConfig({
    isSidebarCompact: !settingStore.isSidebarCompact,
  });
};

const handleNav = (url) => {
  router.push(url);
};

// const handleLogout = () => {
//   router.push(`/login?redirect=${router.currentRoute.value.fullPath}`);
// };
</script>
<style lang="less" scoped>
.@{starter-prefix}-header {
  &-layout {
    height: 64px;
  }

  &-menu-fixed {
    position: fixed;
    top: 0;
    z-index: 1001;

    &-side {
      left: 232px;
      right: 0;
      z-index: 10;
      width: auto;
      transition: all 0.3s;

      &-compact {
        left: 64px;
      }
    }
  }

  &-logo-container {
    cursor: pointer;
    display: inline-flex;
    height: 64px;
  }
}

.header-menu {
  flex: 1 1 1;
  display: inline-flex;

  :deep(.t-menu__item) {
    min-width: unset;
    padding: 0px 16px;
  }
}

.operations-container {
  display: flex;
  align-items: center;
  margin-right: 12px;

  .t-popup__reference {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .t-button {
    margin: 0 8px;

    &.header-user-btn {
      margin: 0;
    }
  }

  .t-icon {
    font-size: 20px;

    &.general {
      margin-right: 16px;
    }
  }
}

.header-operate-left {
  display: flex;
  margin-left: 20px;
  align-items: normal;
  line-height: 0;

  .collapsed-icon {
    font-size: 20px;
  }
}

.header-logo-container {
  width: 184px;
  height: 26px;
  display: flex;
  margin-left: 24px;
  color: var(--td-text-color-primary);

  .t-logo {
    width: 100%;
    height: 100%;

    &:hover {
      cursor: pointer;
    }
  }

  &:hover {
    cursor: pointer;
  }
}

.header-user-account {
  display: inline-flex;
  align-items: center;
  color: var(--td-text-color-primary);

  .t-icon {
    margin-left: 4px;
    font-size: 16px;
  }
}

.erp-status-trigger {
  display: inline-flex;
  align-items: center;

  .erp-status-text {
    margin-left: 4px;
    font-size: 13px;
  }
}

.erp-status-loading-icon {
  animation: erp-status-spin 1s linear infinite;
}

.erp-status-popup {
  width: 280px;
  padding: 12px 14px;
  color: var(--td-text-color-primary);
}

.erp-status-popup-title {
  margin-bottom: 10px;
  font-weight: 600;
}

.erp-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 28px;
  font-size: 13px;
}

.erp-status-row-label {
  margin-right: 16px;
  color: var(--td-text-color-secondary);
}

.erp-status-message {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--td-border-level-1-color);
  color: var(--td-text-color-secondary);
  font-size: 12px;
  line-height: 18px;
  word-break: break-all;
}

@keyframes erp-status-spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

:deep(.t-head-menu__inner) {
  border-bottom: 1px solid var(--td-border-level-1-color);
}

.t-menu--light {
  .header-user-account {
    color: var(--td-text-color-primary);
  }
}

.t-menu--dark {
  .t-head-menu__inner {
    border-bottom: 1px solid var(--td-gray-color-10);
  }

  .header-user-account {
    color: rgba(255, 255, 255, 0.55);
  }

  .t-button {
    --ripple-color: var(--td-gray-color-10) !important;

    &:hover {
      background: var(--td-gray-color-12) !important;
    }
  }
}

.operations-dropdown-container-item {
  width: 100%;
  display: flex;
  align-items: center;

  .t-icon {
    margin-right: 8px;
  }

  :deep(.t-dropdown__item) {
    .t-dropdown__item__content {
      display: flex;
      justify-content: center;
    }

    .t-dropdown__item__content__text {
      display: flex;
      align-items: center;
      font-size: 14px;
    }
  }

  :deep(.t-dropdown__item) {
    width: 100%;
    margin-bottom: 0px;
  }

  &:last-child {
    :deep(.t-dropdown__item) {
      margin-bottom: 8px;
    }
  }
}

.operations-container {
  .env-font {
    color: #d6d6d6;
    font-family: TencentSansW7;
  }
}

#projectSelector {
  margin: 0 8px;
  display: flex;
  align-items: center;

  .label {
    margin-right: 4px;
    color: var(--td-text-color-primary);
    font-size: 14px;
  }
}
</style>
