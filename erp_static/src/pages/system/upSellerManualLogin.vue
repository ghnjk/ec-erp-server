<template>
  <div class="up-seller-manual-login">
    <t-card title="UpSeller 人工登录" :bordered="true">
      <t-loading :loading="statusLoading" text="加载 ERP 状态...">
        <div class="status-panel">
          <div class="status-row">
            <span class="label">ERP 类型</span>
            <span>{{ erpTypeText }}</span>
          </div>
          <div class="status-row">
            <span class="label">登录状态</span>
            <t-tag :theme="erpStatus?.is_login ? 'success' : 'danger'" variant="light">
              {{ erpStatus?.is_login ? '已登录' : '未登录' }}
            </t-tag>
          </div>
          <div class="status-row">
            <span class="label">邮箱</span>
            <span>{{ erpStatus?.email || '-' }}</span>
          </div>
          <div class="status-row">
            <span class="label">仓库 ID</span>
            <span>{{ erpStatus?.warehouse_id || '-' }}</span>
          </div>
          <div class="status-row">
            <span class="label">状态说明</span>
            <span>{{ erpStatus?.message || statusError || '-' }}</span>
          </div>
        </div>
      </t-loading>

      <t-divider />

      <div v-if="erpStatus?.is_login" class="relogin-row">
        <t-checkbox v-model="forceRelogin">重新登陆</t-checkbox>
        <span class="hint">当前已登录，勾选后方可再次发送邮箱验证码并强制登录</span>
      </div>

      <div class="action-row">
        <t-button
          theme="primary"
          :loading="sendLoading"
          :disabled="!canSendCode"
          @click="onSendEmailCode"
        >
          发送邮箱验证码
        </t-button>
        <t-button theme="default" variant="outline" :disabled="statusLoading" @click="refreshStatus">
          刷新状态
        </t-button>
      </div>

      <div v-if="showEmailCodeForm" class="email-code-panel">
        <t-form layout="inline">
          <t-form-item label="邮箱验证码">
            <t-input
              v-model="emailCode"
              placeholder="请输入邮箱验证码"
              clearable
              style="width: 220px"
              :disabled="loginLoading"
            />
          </t-form-item>
          <t-form-item>
            <t-button
              theme="primary"
              :loading="loginLoading"
              :disabled="!emailCode.trim()"
              @click="onSubmitEmailCode"
            >
              登录
            </t-button>
          </t-form-item>
        </t-form>
      </div>

      <div v-if="lastResult" class="result-panel">
        <div class="status-row">
          <span class="label">登录结果</span>
          <t-tag :theme="resultTagTheme" variant="light">{{ lastResult.login_status }}</t-tag>
          <span class="result-message">{{ lastResult.message }}</span>
        </div>
        <div class="status-row">
          <span class="label">退出码</span>
          <span>{{ lastResult.exit_code }}</span>
        </div>
        <div class="logs-title">完整日志</div>
        <pre class="logs">{{ lastResult.logs || '(无输出)' }}</pre>
      </div>
    </t-card>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import {
  BackendErpStatus,
  UpSellerManualLoginResult,
  getBackendErpStatus,
  upSellerManualLogin,
} from '@/apis/sysApis';

const erpStatus = ref<BackendErpStatus | null>(null);
const statusLoading = ref(false);
const statusError = ref('');
const forceRelogin = ref(false);
const sendLoading = ref(false);
const loginLoading = ref(false);
const emailCode = ref('');
const showEmailCodeForm = ref(false);
const lastResult = ref<UpSellerManualLoginResult | null>(null);

const erpTypeText = computed(() => {
  const type = erpStatus.value?.erp_type;
  if (type === 'up_seller') return 'UpSeller';
  if (type === 'big_seller') return 'BigSeller';
  return type || '-';
});

const canSendCode = computed(() => {
  if (statusLoading.value || sendLoading.value || loginLoading.value) return false;
  if (!erpStatus.value) return false;
  if (erpStatus.value.erp_type !== 'up_seller') return false;
  if (erpStatus.value.is_login && !forceRelogin.value) return false;
  return true;
});

const resultTagTheme = computed(() => {
  const status = lastResult.value?.login_status;
  if (status === 'logged_in') return 'success';
  if (status === 'need_email_code') return 'warning';
  return 'danger';
});

const refreshStatus = async () => {
  statusLoading.value = true;
  statusError.value = '';
  try {
    erpStatus.value = await getBackendErpStatus();
  } catch (error) {
    erpStatus.value = null;
    statusError.value = `${error}`;
    MessagePlugin.error(`获取 ERP 状态失败: ${error}`);
  } finally {
    statusLoading.value = false;
  }
};

const applyLoginResult = async (result: UpSellerManualLoginResult) => {
  lastResult.value = result;
  if (result.login_status === 'need_email_code') {
    showEmailCodeForm.value = true;
    MessagePlugin.warning(result.message || '需要邮箱验证码');
  } else if (result.login_status === 'logged_in') {
    showEmailCodeForm.value = false;
    emailCode.value = '';
    MessagePlugin.success(result.message || '登录成功');
    await refreshStatus();
  } else {
    MessagePlugin.error(result.message || '登录失败');
  }
};

const onSendEmailCode = async () => {
  if (!canSendCode.value || sendLoading.value) return;
  sendLoading.value = true;
  try {
    const result = await upSellerManualLogin({});
    await applyLoginResult(result);
  } catch (error) {
    MessagePlugin.error(`发送邮箱验证码失败: ${error}`);
  } finally {
    sendLoading.value = false;
  }
};

const onSubmitEmailCode = async () => {
  const code = emailCode.value.trim();
  if (!code || loginLoading.value) return;
  loginLoading.value = true;
  try {
    const result = await upSellerManualLogin({ email_code: code });
    await applyLoginResult(result);
  } catch (error) {
    MessagePlugin.error(`登录失败: ${error}`);
  } finally {
    loginLoading.value = false;
  }
};

onMounted(() => {
  refreshStatus();
});
</script>

<style lang="less" scoped>
.up-seller-manual-login {
  padding: 16px;
}

.status-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  line-height: 22px;

  .label {
    width: 88px;
    color: var(--td-text-color-secondary);
    flex-shrink: 0;
  }
}

.relogin-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;

  .hint {
    color: var(--td-text-color-secondary);
    font-size: 13px;
  }
}

.action-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.email-code-panel {
  margin-bottom: 16px;
}

.result-panel {
  margin-top: 8px;
}

.result-message {
  color: var(--td-text-color-secondary);
}

.logs-title {
  margin: 12px 0 8px;
  font-weight: 600;
}

.logs {
  margin: 0;
  max-height: 420px;
  overflow: auto;
  padding: 12px;
  background: var(--td-bg-color-container-hover);
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
