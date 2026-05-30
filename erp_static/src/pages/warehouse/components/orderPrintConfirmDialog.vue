<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      confirm-btn="确认 & 提交打印"
      header="订单打印信息确认"
      show-overlay
      width="80%"
      @cancel="onClose"
      @confirm="onSubmitPrintOrder"
    >
      <t-loading :loading="isLoading">
        <t-form>
          <t-form-item label="订单数">
            <t-input :value="orderSummary" disabled />
          </t-form-item>
          <t-form-item label="sku拣货备注">
            <t-space direction="vertical">
              <t-list :split="true" stripe>
                <t-list-item v-for="row in manualMarkSkuList" :key="row?.sku">
                  <t-list-item-meta :description="row.desc" :image="row.image_url" :title="row?.sku" />
                  <t-space direction="vertical">
                    <t-form-item label="1拣货单位=">
                      <t-input-number v-model="row.picking_unit"></t-input-number>
                      SKU
                    </t-form-item>
                    <t-form-item label="拣货单位名">
                      <t-input v-model="row.picking_unit_name"></t-input>
                    </t-form-item>
                    <t-form-item label="添加pkg打包">
                      <t-checkbox v-model="row.support_pkg_picking"></t-checkbox>
                    </t-form-item>
                    <t-form-item v-if="row.support_pkg_picking" label="1 PKG =">
                      <t-input-number v-model="row.pkg_picking_unit"></t-input-number>
                      SKU
                    </t-form-item>
                    <t-form-item v-if="row.support_pkg_picking" label="PKG打包单位">
                      <t-input v-model="row.pkg_picking_unit_name"></t-input>
                    </t-form-item>
                    <t-form-item label="拣货sku名">
                      <t-input v-model="row.picking_sku_name"></t-input>
                    </t-form-item>
                  </t-space>
                </t-list-item>
              </t-list>
            </t-space>
          </t-form-item>
          <!--          <t-form-item>-->
          <!--            <t-button theme="default" @click="onClose">关闭</t-button>-->
          <!--            <t-button :disabled="isLoading" theme="primary" @click="onSubmitPrintOrder">确认 & 提交打印</t-button>-->
          <!--          </t-form-item>-->
        </t-form>
      </t-loading>
    </t-dialog>
    <order-print-progress-dialog ref="orderPrintProgressDialog" />
  </div>
</template>

<script lang="ts">
import OrderPrintProgressDialog from './orderPrintProgressDialog.vue';

export default {
  name: 'OrderPrintConfirmDialog',
  components: {
    OrderPrintProgressDialog,
  },
};
</script>
<script lang="ts" setup>
import { ref, defineExpose } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { preSubmitPrintOrder, startRunPrintOrderTask, submitManualMarkSkuPickingNote } from '@/apis/warehouseApis';

const orderPrintProgressDialog = ref(null);
const visible = ref(false);
const orderSummary = ref('');
//     need_manual_mark_sku_list
const manualMarkSkuList = ref([]);
const waitPrintOrderList = ref([]);
const isLoading = ref(false);
const popupDialog = async (totalCount, orderList) => {
  waitPrintOrderList.value = orderList;
  orderSummary.value = `本次打印 ${orderList.length} 单 / 共 ${totalCount} 单`;
  visible.value = true;
  isLoading.value = true;
  await tryPreSubmitPrintOrderTask();
  isLoading.value = false;
};
const tryPreSubmitPrintOrderTask = async () => {
  try {
    manualMarkSkuList.value = [];
    const req = {
      order_list: waitPrintOrderList.value,
    };
    const res = await preSubmitPrintOrder(req);
    res.need_manual_mark_sku_list.forEach((item) => {
      manualMarkSkuList.value.push({
        sku: item.sku,
        image_url: item.image_url,
        desc: item.desc,
        picking_unit: 0,
        picking_unit_name: 'pcs',
        picking_sku_name: item.sku,
        support_pkg_picking: false,
        pkg_picking_unit: 0,
        pkg_picking_unit_name: 'pk',
      });
    });
    console.log('manualMarkSkuList', manualMarkSkuList.value);
    if (manualMarkSkuList.value.length > 0) {
      await MessagePlugin.info('需要补充sku拣货备注.');
      return null;
    }
    console.log('提交打印订单成功，面单id', res.task_id);
    return res.task_id;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`打印订单失败: ${e}`);
  }
  return null;
};
const onSubmitAllPickingNote = async () => {
  if (manualMarkSkuList.value.length === 0) {
    return true;
  }
  let isValid = true;
  manualMarkSkuList.value.forEach((item) => {
    if (item.picking_unit <= 0) {
      MessagePlugin.info(`${item.sku} picking_unit 未填`);
      isValid = false;
    }
    if (item.picking_unit_name === '') {
      MessagePlugin.info(`${item.sku} picking_unit_name 未填`);
      isValid = false;
    }
    if (item.picking_sku_name === '') {
      MessagePlugin.info(`${item.sku} picking_sku_name 未填`);
      isValid = false;
    }
    if (item.support_pkg_picking) {
      if (item.pkg_picking_unit <= 0) {
        MessagePlugin.info(`${item.sku} pkg_picking_unit 未填`);
        isValid = false;
      }
      if (item.pkg_picking_unit_name === '') {
        MessagePlugin.info(`${item.sku} pkg_picking_unit_name 未填`);
        isValid = false;
      }
    }
  });
  if (!isValid) {
    return false;
  }
  try {
    const req = {
      manual_mark_sku_list: manualMarkSkuList.value,
    };
    await submitManualMarkSkuPickingNote(req);
    return true;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`添加sku拣货备注失败: ${e}`);
    return false;
  }
};
const onStartupPrintTask = async (taskId) => {
  try {
    const req = {
      task_id: taskId,
    };
    const task = await startRunPrintOrderTask(req);
    console.log('task', task);
    await orderPrintProgressDialog.value.popupDialog(taskId);
    visible.value = false;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`启动后台任务失败: ${e}`);
    isLoading.value = false;
  }
};
const onClose = () => {
  visible.value = false;
};
const onSubmitPrintOrder = async () => {
  if (isLoading.value) {
    return;
  }
  isLoading.value = true;
  // 先提交备注信息
  const isOk = await onSubmitAllPickingNote();
  if (!isOk) {
    isLoading.value = false;
    return;
  }
  // 再尝试提交打印任务
  const taskId = await tryPreSubmitPrintOrderTask();
  if (taskId != null) {
    // 启动任务
    await onStartupPrintTask(taskId);
  } else {
    isLoading.value = false;
  }
};
defineExpose({ popupDialog });
</script>
<style scoped></style>
