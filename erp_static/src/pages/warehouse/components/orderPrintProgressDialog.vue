<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      header="打印订单中..."
      show-overlay
      width="80%"
      @cancel="onClose"
    >
      <t-form>
        <t-form-item label="任务id">
          <t-input :value="taskInfo?.task_id" disabled />
        </t-form-item>
        <t-form-item label="当前步骤">
          <t-input :value="taskInfo?.current_step" current_step disabled />
        </t-form-item>
        <t-form-item v-if="isPdfReady" label="打印链接">
          <t-link :href="taskInfo?.pdf_file_url" target="_blank" theme="primary" underline>
            <template #prefix-icon>
              <link-icon />
            </template>
            打印PDF
          </t-link>
        </t-form-item>
        <t-form-item label="进度">
          <div style="width: 80%">
            <t-progress :percentage="taskInfo?.progress" theme="plump" />
          </div>
        </t-form-item>
        <t-collapse :default-value="[]">
          <t-collapse-panel header="处理日志">
            <pre>{{ taskInfo?.logs.join('\n') }}</pre>
          </t-collapse-panel>
        </t-collapse>
      </t-form>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'OrderPrintProgressDialog',
};
</script>
<script lang="ts" setup>
import { ref, defineExpose } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { queryPrintOrderTask } from '@/apis/warehouseApis';

const taskId = ref('');
const visible = ref(false);
const taskInfo = ref(null);
const timer = ref(null);
const isPdfReady = ref(false);

const refreshTaskInfo = async () => {
  if (timer.value !== null) {
    clearTimeout(timer.value);
  }
  const isOk = await onQueryTaskInfo();
  if (!isOk) {
    timer.value = setTimeout(refreshTaskInfo, 1000);
  }
};
const isPrintTaskOk = () => {
  if (taskInfo.value === null) {
    return false;
  }
  return (
    taskInfo.value.pdf_file_url !== null &&
    taskInfo.value.pdf_file_url !== undefined &&
    taskInfo.value.pdf_file_url !== ''
  );
};
const onQueryTaskInfo = async () => {
  try {
    const req = {
      task_id: taskId.value,
    };
    const res = await queryPrintOrderTask(req);
    taskInfo.value = res.task;
    if (isPrintTaskOk()) {
      isPdfReady.value = true;
      console.log('url', taskInfo.value.pdf_file_url);
      window.open(taskInfo.value.pdf_file_url, '_blank');
      return true;
    }
    return false;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询打印进度异常: ${e}`);
    return false;
  }
};
const popupDialog = async (tid) => {
  taskId.value = tid;
  isPdfReady.value = false;
  visible.value = true;
  await refreshTaskInfo();
};
const onClose = () => {
  if (timer.value !== null) {
    clearTimeout(timer.value);
  }
  visible.value = false;
};
defineExpose({ popupDialog });
</script>

<style scoped></style>
