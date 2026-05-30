<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :cancel-btn="null"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      header="点货入库"
      show-overlay
      width="80%"
    >
      <t-row>
        <t-col :span="12">
          <t-form layout="inline">
            <t-form-item label="采购单:" name="purchase_order_id">
              <t-input v-model="purchaseOrder.purchase_order_id" disabled />
            </t-form-item>
            <t-form-item label="供应商:" name="supplier_name">
              <t-input v-model="purchaseOrder.supplier_name" disabled />
            </t-form-item>
            <t-form-item label="采购日期:" name="purchase_date">
              <t-input v-model="purchaseOrder.purchase_date" disabled />
            </t-form-item>
          </t-form>
        </t-col>
      </t-row>
      <br />
      <div class="table-container">
        <t-table
          :bordered="true"
          :columns="skuTableColumns"
          :data="skuTableData"
          :rowspan-and-colspan="skuTableRowspanAndColspan"
          lazy-load
          resizable
          row-key="idx"
          table-layout="fixed"
        >
          <template #quantity="{ row }">
            <div v-if="row.quantity !== row.check_in_quantity" style="background-color: yellow">
              {{ row.quantity }}
            </div>
            <div v-else>
              {{ row.quantity }}
            </div>
          </template>
          <template #sku="{ row }">
            <t-space>
              <t-image :src="row.erp_sku_image_url" :style="{ width: '30px', height: '30px' }" />
              {{ row.sku }}
            </t-space>
          </template>
        </t-table>
        <br />
        <t-row>
          <t-col :span="12">
            <t-form-item label="备注:" name="remark">
              <t-textarea
                v-model="purchaseOrder.remark"
                :autosize="{ minRows: 3, maxRows: 10 }"
                name="remark"
                placeholder="采购单备注"
              />
            </t-form-item>
          </t-col>
        </t-row>
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
      </div>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'CheckInWareHouseDialog•',
};
</script>
<script lang="ts" setup>
import { ref, defineExpose, defineEmits, defineProps } from 'vue';
import { TableProps, Checkbox, InputNumber, MessagePlugin } from 'tdesign-vue-next';
import { skuGroupNameOptions, skuGroupMap, skuMap, loadSkuInfo } from '@/utils/skuUtil';
import { supplierIdOptions, loadSupplierInfo, getNextPurchaseAction, ORDER_TYPE_DOMESTIC } from '@/utils/supplierUtil';
import { querySkuPurchasePrice, savePurchaseOrder, submitPurchaseOrderAndNextStep } from '@/apis/supplierApis';

const props = defineProps({
  orderType: {
    type: Number,
    default: ORDER_TYPE_DOMESTIC,
  },
});

const skuTableData = ref([]);

const visible = ref(false);
const purchaseOrder = ref(null);
const skuTableColumns = [
  {
    width: 120,
    colKey: 'sku_group',
    title: 'sku分组',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'sku_name',
    title: '商品名',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'sku',
    title: '商品SKU',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'quantity',
    title: '采购数量',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'check_in_quantity',
    title: '入库数量',
    align: 'center',
    // 编辑状态相关配置，全部集中在 edit
    edit: {
      // 1. 支持任意组件。需保证组件包含 `value` 和 `onChange` 两个属性，且 onChange 的第一个参数值为 new value。
      // 2. 如果希望支持校验，组件还需包含 `status` 和 `tips` 属性。具体 API 含义参考 Input 组件
      component: InputNumber,
      // props, 透传全部属性到 Input 组件。可以是一个函数，不同行有不同的 props 属性 时，使用 Function）
      props: {
        autofocus: true,
      },
      // 触发校验的时机（when to validate)
      validateTrigger: 'change',
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      abortEditOnEvent: ['onEnter', 'onBlur'],
      // 编辑完成，退出编辑态后触发
      onEdited: (context) => {
        console.log(context);
        skuTableData.value.splice(context.rowIndex, 1, context.newRowData);
      },
      // 校验规则，此处同 Form 表单。https://tdesign.tencent.com/vue-next/components/form
      rules: [
        {
          required: true,
          message: '不能为空',
        },
      ],
      // 默认是否为编辑状态
      defaultEditable: true,
    },
  },
  {
    width: 120,
    colKey: 'sku_unit_name',
    title: '单位',
    align: 'center',
  },
];
const emit = defineEmits(['onOrderChange']);

const popupDialog = async (pOrder: any) => {
  await loadSkuInfo();
  console.log(pOrder);
  purchaseOrder.value = pOrder;
  skuTableData.value = [];
  purchaseOrder.value.store_skus.forEach((item) => {
    const sku = skuMap.value.get(item.sku);
    skuTableData.value.push({
      idx: skuTableData.value.length + 1,
      sku_group: item.sku_group,
      sku_name: item.sku_name,
      sku: item.sku,
      erp_sku_image_url: sku?.erp_sku_image_url,
      unit_price: item.unit_price,
      quantity: item.quantity,
      sku_unit_name: item.sku_unit_name,
      sku_unit_quantity: item.sku_unit_quantity,
      avg_sell_quantity: item.avg_sell_quantity,
      shipping_stock_quantity: item.shipping_stock_quantity,
      check_in_quantity: item.check_in_quantity,
    });
  });
  visible.value = true;
};
const buildSubmitOrderReq = () => {
  purchaseOrder.value.store_skus = skuTableData.value;
  purchaseOrder.value.order_type = props.orderType;
  return purchaseOrder.value;
};
const onSavePurchaseOrder = async () => {
  const req = buildSubmitOrderReq();
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
  const req = buildSubmitOrderReq();
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
const skuTableRowspanAndColspan: TableProps['rowspanAndColspan'] = ({ col, rowIndex, colIndex }) => {
  if (colIndex !== 0) {
    return;
  }
  if (rowIndex > 0 && skuTableData.value[rowIndex - 1].sku_group === skuTableData.value[rowIndex].sku_group) {
    return;
  }
  // console.log(`skuTableRowspanAndColspan ${rowIndex}-${colIndex}: ${col}`);
  let rowspan = 1;
  for (let i = rowIndex + 1; i < skuTableData.value.length; i++) {
    if (skuTableData.value[i].sku_group === skuTableData.value[rowIndex].sku_group) {
      rowspan += 1;
    } else {
      break;
    }
  }
  if (rowspan <= 1) {
    return;
  }
  console.log(
    `skuTableRowspanAndColspan ${rowIndex}-${colIndex}`,
    {
      rowspan,
    },
    skuTableData.value,
  );
  return {
    rowspan,
  };
};
defineExpose({ popupDialog });
</script>
<style scoped></style>
