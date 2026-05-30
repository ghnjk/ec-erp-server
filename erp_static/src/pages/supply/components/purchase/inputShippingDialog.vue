<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :cancel-btn="null"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      header="供应商发货"
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
        <t-form-item label="海运公司:" name="shipping_company">
          <t-select
            v-model="purchaseOrder.shipping_company"
            :options="shippingCompanyOptions"
            filterable
            placeholder="-请选择海运公司-"
          />
        </t-form-item>
        <t-form-item label="港口:" name="maritime_port">
          <t-select
            v-model="purchaseOrder.maritime_port"
            :options="maritimePortOptions"
            filterable
            placeholder="-请选择港口-"
          />
        </t-form-item>
        <t-form-item label="运费:" name="shipping_fee">
          <t-input v-model="purchaseOrder.shipping_fee" />
        </t-form-item>
        <t-form-item label="预期抵达日期:" name="expect_arrive_warehouse_date">
          <t-date-picker v-model="purchaseOrder.expect_arrive_warehouse_date" allow-input />
        </t-form-item>
      </t-form>
      <t-row>
        <t-col :span="9"></t-col>
        <t-col :span="3">
          <t-space>
            <t-button style="float: right" theme="primary" @click="onSavePurchaseOrder">保存</t-button>
            <t-button style="float: right" theme="success" @click="onSubmitPurchaseOrder">
              > 提交：{{ getNextPurchaseAction(purchaseOrder?.purchase_step, props.orderType) }}
            </t-button>
          </t-space>
        </t-col>
      </t-row>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'InputShippingDialog',
};
</script>
<script lang="ts" setup>
import { ref, defineExpose, defineEmits, defineProps } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { savePurchaseOrder, submitPurchaseOrderAndNextStep } from '@/apis/supplierApis';
import { getNextPurchaseAction, ORDER_TYPE_DOMESTIC } from '@/utils/supplierUtil';

const props = defineProps({
  orderType: {
    type: Number,
    default: ORDER_TYPE_DOMESTIC,
  },
});
const emit = defineEmits(['onOrderChange']);

const visible = ref(false);
const purchaseOrder = ref(null);
const shippingCompanyOptions = [
  {
    label: '环世',
    value: '环世',
  },
  {
    label: '通达',
    value: '通达',
  },
  {
    label: '恒盛',
    value: '恒盛',
  },
  {
    label: '信誉',
    value: '信誉',
  },
  {
    label: '悦希',
    value: '悦希',
  },
  {
    label: '喜运达',
    value: '喜运达',
  },
  {
    label: '速凡国际',
    value: '速凡国际',
  },
  {
    label: '羊驼帮',
    value: '羊驼帮',
  },
  {
    label: '德羽',
    value: '德羽',
  },
  {
    label: '宇佳安',
    value: '宇佳安',
  },
  {
    label: '百世',
    value: '百世',
  },
  {
    label: '中印通达',
    value: '中印通达',
  }
];
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
  {
    label: '天津',
    value: '天津',
  },
  {
    label: '深圳',
    value: '深圳',
  },
  {
    label: '山东',
    value: '山东',
  },
];
const popupDialog = async (pOrder: any) => {
  purchaseOrder.value = pOrder;
  if (
    purchaseOrder.value.expect_arrive_warehouse_date === undefined ||
    purchaseOrder.value.expect_arrive_warehouse_date === null ||
    purchaseOrder.value.expect_arrive_warehouse_date === ''
  ) {
    const currentDate = new Date();
    const futureDate = new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000);
    const year = futureDate.getFullYear();
    const month = String(futureDate.getMonth() + 1).padStart(2, '0');
    const day = String(futureDate.getDate()).padStart(2, '0');
    purchaseOrder.value.expect_arrive_warehouse_date = `${year}-${month}-${day}`;
  }
  visible.value = true;
};
const onSavePurchaseOrder = async () => {
  const req = { ...purchaseOrder.value, order_type: props.orderType };
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
const onSubmitPurchaseOrder = async () => {
  const req = { ...purchaseOrder.value, order_type: props.orderType };
  console.log(`onSubmitPurchaseOrder `, req);
  try {
    const res = await submitPurchaseOrderAndNextStep(req);
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
