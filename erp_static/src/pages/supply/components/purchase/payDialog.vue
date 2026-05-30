<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :cancel-btn="null"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      header="支付货款"
      show-overlay
      width="60%"
    >
      <t-form>
        <t-form-item label="采购单:" name="purchase_order_id">
          <t-input v-model="purchaseOrder.purchase_order_id" disabled />
        </t-form-item>
        <t-form-item label="供应商:" name="supplier_name">
          <t-input v-model="purchaseOrder.supplier_name" disabled />
        </t-form-item>
        <t-form-item label="采购日期:" name="purchase_date">
          <t-input v-model="purchaseOrder.purchase_date" disabled />
        </t-form-item>
        <t-form-item label="sku总价:" name="sku_amount">
          {{ purchaseOrder.sku_amount / 100.0 }}
        </t-form-item>
        <t-form-item label="付款金额:" name="pay_amount">
          <t-input v-model="purchaseOrder.pay_amount" />
        </t-form-item>
      </t-form>
      <br />
      <t-row>
        <t-col :span="9"></t-col>
        <t-col :span="3">
          <t-space>
            <t-button style="float: right" theme="primary" @click="onSavePurchaseOrder">保存</t-button>
            <t-button style="float: right" theme="success" @click="onPayOrder"> > 支付货款</t-button>
          </t-space>
        </t-col>
      </t-row>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'PayDialog',
};
</script>
<script lang="ts" setup>
import { ref, defineExpose, defineEmits } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { savePurchaseOrder } from '@/apis/supplierApis';

const emit = defineEmits(['onOrderChange']);

const visible = ref(false);
const purchaseOrder = ref(null);
const maritimePortOptions = [
  {
    label: '义乌',
    value: '义乌',
  },
  {
    label: '广州',
    value: '广州',
  },
  {
    label: '晋江',
    value: '晋江',
  },
  {
    label: '新-义乌海运',
    value: '新-义乌海运',
  },
  {
    label: '河北',
    value: '河北',
  },
];
const popupDialog = async (pOrder: any) => {
  pOrder.pay_amount /= 100.0;
  purchaseOrder.value = pOrder;
  visible.value = true;
};
const onSavePurchaseOrder = async () => {
  const req = JSON.parse(JSON.stringify(purchaseOrder.value));
  req.pay_amount = Math.round(req.pay_amount * 100.0);
  console.log(`onSavePurchaseOrder `, req);
  try {
    const res = await savePurchaseOrder(req);
    console.log(res);
    visible.value = false;
    emit('onOrderChange');
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`保存采购单异常: ${e}`);
  }
};
const onPayOrder = async () => {
  const req = JSON.parse(JSON.stringify(purchaseOrder.value));
  req.pay_amount = Math.round(req.pay_amount * 100.0);
  req.pay_state = 1;
  console.log(`onSubmitPurchaseOrder `, req);
  try {
    const res = await savePurchaseOrder(req);
    console.log(res);
    visible.value = false;
    emit('onOrderChange');
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`保存采购单异常: ${e}`);
  }
};
defineExpose({ popupDialog });
</script>

<style scoped></style>
