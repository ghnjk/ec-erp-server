<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :cancel-btn="null"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      :header="isDomestic ? '选择采购商品' : '选择销售商品'"
      show-overlay
      width="80%"
    >
      <t-row>
        <t-col v-if="isDomestic" :span="12">
          <t-form layout="inline">
            <t-form-item label="供应商:" name="supplierId">
              <t-select
                v-model="supplierId"
                :options="supplierIdOptions"
                filterable
                placeholder="-请选择供应商-"
                style="width: 200px; display: inline-block; margin: 0 20px 20px 0"
              />
            </t-form-item>
          </t-form>
        </t-col>
        <t-col :span="isDomestic ? 8 : 20">
          <t-form layout="inline">
            <t-form-item label="SKU分组:" name="skuGroupName">
              <t-select
                v-model="skuGroupName"
                :options="skuGroupNameOptions"
                filterable
                placeholder="-请选择SKU分组-"
                style="width: 200px; display: inline-block; margin: 0 20px 20px 0"
              />
            </t-form-item>
            <t-form-item>
              <t-space size="small" style="align-items: center">
                <t-button theme="default" @click="onAddSkuGroup">{{ isDomestic ? '添加采购' : '添加销售' }}</t-button>
              </t-space>
            </t-form-item>
          </t-form>
        </t-col>
        <t-col :span="4">
          <h2>总金额：{{ formatCurrency(totalAmount) }}</h2>
          <h3 style="margin: 0">总打包体积：{{ formatVolumeM3(totalPackVolumeM3) }} m³</h3>
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
          <template #total_price="{ row }">
            {{ formatCurrency(row.unit_price * row.quantity) }}
          </template>
          <template #pack_volume_m3="{ row }">
            {{ formatVolumeM3(rowPackVolumeM3(row)) }}
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
                v-model="remark"
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
  name: 'SelectPurchaseSkuDialog',
};
</script>
<script lang="ts" setup>
import { ref, computed, defineExpose, defineEmits, defineProps } from 'vue';
import { TableProps, Input, InputNumber, MessagePlugin } from 'tdesign-vue-next';
import {
  skuGroupNameOptions,
  skuGroupMap,
  skuMap,
  loadSkuInfo,
  calcPackVolumeM3,
  formatVolumeM3,
} from '@/utils/skuUtil';
import { supplierIdOptions, loadSupplierInfo, getNextPurchaseAction, ORDER_TYPE_DOMESTIC } from '@/utils/supplierUtil';
import { querySkuPurchasePrice, savePurchaseOrder, submitPurchaseOrderAndNextStep } from '@/apis/supplierApis';

const props = defineProps({
  orderType: {
    type: Number,
    default: ORDER_TYPE_DOMESTIC,
  },
});
const isDomestic = computed(() => props.orderType === ORDER_TYPE_DOMESTIC);

const cnyFormatter = new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' });
const usdFormatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
const formatCurrency = (value: number) => {
  return isDomestic.value ? cnyFormatter.format(value) : usdFormatter.format(value);
};

const visible = ref(false);
const purchaseOrder = ref(null);
const supplierId = ref(null);
const remark = ref('');
const skuGroupName = ref('');
const editableNumberCell = (defaultEditable: boolean) => ({
  component: InputNumber,
  props: { autofocus: true },
  validateTrigger: 'change',
  abortEditOnEvent: ['onEnter', 'onBlur'],
  onEdited: (context) => {
    skuTableData.value.splice(context.rowIndex, 1, context.newRowData);
    calcTotalAmount();
  },
  rules: [{ required: true, message: '不能为空' }],
  defaultEditable,
});

const skuTableColumns = computed(() => [
  { width: 120, colKey: 'sku_group', title: 'sku分组', align: 'center' },
  { width: 120, colKey: 'sku_name', title: '商品名', align: 'center' },
  { width: 120, colKey: 'sku', title: '商品SKU', align: 'center' },
  { width: 120, colKey: 'inventory', title: '库存', align: 'center' },
  { width: 120, colKey: 'quantity', title: '数量', align: 'center', edit: editableNumberCell(true) },
  { width: 120, colKey: 'sku_unit_name', title: '单位', align: 'center' },
  {
    width: 120,
    colKey: 'unit_price',
    title: '单价',
    align: 'center',
    edit: editableNumberCell(!isDomestic.value),
  },
  { width: 120, colKey: 'total_price', title: '总价', align: 'center' },
  { width: 120, colKey: 'pack_volume_m3', title: '打包体积(m³)', align: 'center' },
]);
const skuTableData = ref([]);
const totalAmount = ref(0.0);
const emit = defineEmits(['onOrderChange']);

const rowPackVolumeM3 = (row: any) =>
  calcPackVolumeM3(row.quantity, row.sku_unit_quantity, row.sku_pack_length, row.sku_pack_width, row.sku_pack_height);

const totalPackVolumeM3 = computed(() => {
  let total = 0;
  skuTableData.value.forEach((item: any) => {
    total += rowPackVolumeM3(item);
  });
  return total;
});

const onAddSkuGroup = async () => {
  const skuList = skuGroupMap.value.get(skuGroupName.value);
  if (skuList !== null && skuList !== undefined) {
    for (let i = 0; i < skuList.length; i++) {
      const item = skuList[i];
      let unitPrice = 0;
      const req = {
        supplier_id: supplierId.value,
        sku: item.sku,
      };
      const purchasePrice = await querySkuPurchasePrice(req);
      unitPrice = purchasePrice.unit_price / 100.0;
      let skuUnitName = item.sku_unit_name;
      let skuUnitQuantity = item.sku_unit_quantity;
      if(! isDomestic.value) {
        // 线下销售，需要对草地的单位进行特殊处理
        if (skuUnitName && skuUnitName.includes('卷') && skuUnitQuantity > 2 && skuUnitQuantity % 2 === 0) {
          skuUnitName = 'm';
          skuUnitQuantity = 2;
        }
      }
      skuTableData.value.push({
        idx: skuTableData.value.length + 1,
        sku_group: item.sku_group,
        sku_name: item.sku_name,
        sku: item.sku,
        erp_sku_image_url: item.erp_sku_image_url,
        inventory: item.inventory,
        sku_unit_name: skuUnitName,
        sku_unit_quantity: skuUnitQuantity,
        sku_pack_length: item.sku_pack_length,
        sku_pack_width: item.sku_pack_width,
        sku_pack_height: item.sku_pack_height,
        avg_sell_quantity: item.avg_sell_quantity,
        shipping_stock_quantity: item.shipping_stock_quantity,
        quantity: 0,
        unit_price: unitPrice,
      });
    }
  }
};

const popupDialog = async (pOrder: any) => {
  if (isDomestic.value) {
    await loadSupplierInfo();
  }
  await loadSkuInfo();
  if (pOrder !== null) {
    purchaseOrder.value = pOrder;
    supplierId.value = pOrder.supplier_id;
    remark.value = pOrder.remark;
    skuTableData.value = [];
    pOrder.purchase_skus.forEach((item) => {
      const sku = skuMap.value.get(item.sku);
      skuTableData.value.push({
        idx: skuTableData.value.length + 1,
        sku_group: item.sku_group,
        sku_name: item.sku_name,
        sku: item.sku,
        erp_sku_image_url: sku?.erp_sku_image_url,
        inventory: sku?.inventory,
        sku_unit_name: item.sku_unit_name,
        sku_unit_quantity: item.sku_unit_quantity,
        // 体积来自 sku 主数据（snapshot 不冗余，符合后端 add-sku-pack-volume 设计 D4）
        sku_pack_length: sku?.sku_pack_length,
        sku_pack_width: sku?.sku_pack_width,
        sku_pack_height: sku?.sku_pack_height,
        avg_sell_quantity: item.avg_sell_quantity,
        shipping_stock_quantity: item.shipping_stock_quantity,
        quantity: item.quantity,
        unit_price: item.unit_price / 100.0,
      });
    });
  } else {
    purchaseOrder.value = null;
    supplierId.value = null;
    remark.value = '';
    skuTableData.value = [];
  }
  calcTotalAmount();
  visible.value = true;
};
const calcTotalAmount = () => {
  totalAmount.value = 0;
  skuTableData.value.forEach((item) => {
    totalAmount.value += item.quantity * item.unit_price;
  });
};
const buildSubmitOrderReq = () => {
  let req: any = {};
  if (purchaseOrder.value === null) {
    req.purchase_order_id = -1;
    req.supplier_id = supplierId.value;
    req.purchase_step = '草稿';
    req.remark = remark.value;
  } else {
    req = purchaseOrder.value;
    req.supplier_id = supplierId.value;
    req.remark = remark.value;
  }
  req.order_type = props.orderType;
  req.purchase_skus = [];
  skuTableData.value.forEach((item) => {
    const s = JSON.parse(JSON.stringify(item));
    s.unit_price = Math.round(s.unit_price * 100.0);
    req.purchase_skus.push(s);
  });
  return req;
};
const onSubmitPurchaseOrder = async () => {
  if (isDomestic.value && supplierId.value <= 0) {
    await MessagePlugin.error('请先选择供应商');
    return;
  }
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
const onSavePurchaseOrder = async () => {
  if (isDomestic.value && supplierId.value <= 0) {
    await MessagePlugin.error('请先选择供应商');
    return;
  }
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
