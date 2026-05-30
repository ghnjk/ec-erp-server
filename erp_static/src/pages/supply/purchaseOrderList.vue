<template>
  <div>
    <t-card>
      <t-row>
        <t-col :span="12">
          <t-form layout="inline">
            <t-form-item v-if="isDomestic" label="供应商:" name="supplier_name">
              <t-input v-model="queryParam.supplier_name" placeholder="供应商" />
            </t-form-item>
            <t-form-item :label="isDomestic ? '采购进度:' : '销售进度:'" name="purchase_state">
              <t-input v-model="queryParam.purchase_state" :placeholder="isDomestic ? '采购进度' : '销售进度'" />
            </t-form-item>
            <t-form-item v-if="isDomestic" label="国内港口:" name="maritime_port">
              <t-input v-model="queryParam.maritime_port" placeholder="国内港口" />
            </t-form-item>
            <t-form-item>
              <t-space size="small" style="align-items: center; margin-left: 30px">
                <t-button theme="primary" @click="onSearchOrder">查询</t-button>
                <t-button theme="success" @click="onCreatePurchaseOrder">{{ isDomestic ? '新建采购' : '新建销售' }}</t-button>
              </t-space>
            </t-form-item>
          </t-form>
        </t-col>
      </t-row>
      <br />
      <div class="table-container">
        <t-table
          :columns="orderTableColumns"
          :data="orderTableData"
          :loading="orderTableLoading"
          bordered
          hover
          row-key="purchase_order_id"
          stripe
        >
          <template #sku_amount="{ row }">
            {{ formatCurrency(row.sku_amount / 100.0) }}
          </template>
          <template #pay_amount="{ row }">
            {{ formatCurrency(row.pay_amount / 100.0) }}
          </template>
          <template #pay_state="{ row }">
            {{ row.pay_state === 1 ? '已支付: \n' + formatCurrency(row.pay_amount / 100.0) : '待支付' }}
          </template>
          <template #pack_volume_m3="{ row }">
            {{ formatVolumeM3(orderPackVolumeM3(row)) }}
          </template>
          <template #op="{ row }">
            <t-button
              v-if="row.purchase_step !== '完成'"
              size="small"
              theme="primary"
              variant="text"
              @click="popupEditDialog(row)"
            >
              {{ getNextPurchaseAction(row.purchase_step, orderType) }}
            </t-button>
            <t-button
              v-if="row.purchase_step !== '草稿'"
              size="small"
              theme="default"
              variant="text"
              @click="popupPrintPurchaseOrderDialog(row)"
            >
              打印
            </t-button>
            <t-button size="small" theme="default" variant="text" @click="onCopyOrderText(row)">复制文本</t-button>
            <t-button
              v-if="row.purchase_step !== '草稿' && row.pay_state === 0"
              size="small"
              theme="success"
              variant="text"
              @click="popupPayOrderDialog(row)"
            >
              支付
            </t-button>
            <t-popconfirm
              v-if="row.purchase_step !== '草稿' && row.purchase_step !== '完成'"
              content="是否确认将该订单修改到上一步状态？"
              theme="danger"
              @confirm="goPreStep(row)"
            >
              <t-button size="small" theme="danger" variant="text">上一步</t-button>
            </t-popconfirm>
          </template>
        </t-table>
        <t-pagination
          v-model="paginationCurrentPage"
          v-model:pageSize="paginationPageSize"
          :page-size-options="paginationPageSizeOptions"
          :total="paginationTotalCount"
          class="pagination"
          @change="onPaginationChange"
        />
      </div>
    </t-card>
    <select-purchase-sku-dialog ref="selectPurchaseSkuDialog" :order-type="orderType" @onOrderChange="onSearchOrder()" />
    <input-shipping-dialog v-if="isDomestic" ref="inputShippingDialog" :order-type="orderType" @onOrderChange="onSearchOrder()" />
    <check-in-ware-house-dialog v-if="isDomestic" ref="checkInWareHouseDialog" :order-type="orderType" @onOrderChange="onSearchOrder()" />
    <print-purchase-order-dialog ref="printPurchaseOrderDialog" />
    <pay-dialog ref="payDialog" @onOrderChange="onSearchOrder()" />
  </div>
</template>

<script lang="ts">
import SelectPurchaseSkuDialog from './components/purchase/selectPurchaseSkuDialog.vue';
import InputShippingDialog from './components/purchase/inputShippingDialog.vue';
import CheckInWareHouseDialog from './components/purchase/checkInWareHouseDialog.vue';
import PrintPurchaseOrderDialog from './components/purchase/printPurchaseOrderDialog.vue';
import PayDialog from './components/purchase/payDialog.vue';

export default {
  name: 'PurchaseOrderList',
  components: {
    SelectPurchaseSkuDialog,
    InputShippingDialog,
    CheckInWareHouseDialog,
    PrintPurchaseOrderDialog,
    PayDialog,
  },
};
</script>
<script lang="ts" setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { searchPurchaseOrder, savePurchaseOrder, submitPurchaseOrderAndNextStep } from '@/apis/supplierApis';
import { Textarea, MessagePlugin } from 'tdesign-vue-next';
import {
  ORDER_TYPE_DOMESTIC,
  ORDER_TYPE_OVERSEAS,
  getNextPurchaseAction,
  getPurchaseOrderPreState,
} from '@/utils/supplierUtil';
import { skuMap, loadSkuInfo, calcPackVolumeM3, formatVolumeM3 } from '@/utils/skuUtil';

const route = useRoute();
const orderType = computed(() => (route.meta.orderType as number) || ORDER_TYPE_DOMESTIC);
const isDomestic = computed(() => orderType.value === ORDER_TYPE_DOMESTIC);

const cnyFormatter = new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' });
const usdFormatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
const formatCurrency = (value: number) => {
  return isDomestic.value ? cnyFormatter.format(value) : usdFormatter.format(value);
};

const baseColumns = computed(() => {
  const cols = [
    {
      width: 40,
      colKey: 'purchase_order_id',
      title: isDomestic.value ? '采购单' : '销售单',
      align: 'center',
    },
  ];
  if (isDomestic.value) {
    cols.push({
      width: 60,
      colKey: 'supplier_name',
      title: '供应商',
      align: 'center',
    });
  }
  cols.push(
    {
      width: 60,
      colKey: 'purchase_date',
      title: isDomestic.value ? '采购日期' : '销售日期',
      align: 'center',
    },
    {
      width: 60,
      colKey: 'purchase_step',
      title: isDomestic.value ? '采购进度' : '销售进度',
      align: 'center',
    },
  );
  return cols;
});

const domesticExtraColumns = [
  {
    width: 40,
    colKey: 'shipping_company',
    title: '海运公司',
    align: 'center',
  },
  {
    width: 60,
    colKey: 'expect_arrive_warehouse_date',
    title: '预计到货日期',
    align: 'center',
  },
];

const orderTableColumns = computed(() => {
  const remarkEditCol = {
    width: 120,
    colKey: 'remark',
    title: '备注',
    align: 'center',
    edit: {
      component: Textarea,
      props: {
        autofocus: true,
      },
      validateTrigger: 'change',
      abortEditOnEvent: ['onEnter', 'onBlur'],
      onEdited: async (context) => {
        const data = { ...context.newRowData, order_type: orderType.value };
        await savePurchaseOrder(data);
        await onSearchOrder();
      },
      rules: [{ required: true, message: '不能为空' }],
      defaultEditable: false,
    },
  };
  const tailColumns = [
    { width: 80, colKey: 'sku_amount', title: 'sku总价', align: 'center' },
    { width: 80, colKey: 'pack_volume_m3', title: '打包体积(m³)', align: 'center' },
    { width: 80, colKey: 'pay_state', title: '支付状态', align: 'center' },
    remarkEditCol,
    { width: 100, colKey: 'op', title: '操作', align: 'center' },
  ];
  if (isDomestic.value) {
    return [...baseColumns.value, ...domesticExtraColumns, ...tailColumns];
  }
  return [...baseColumns.value, ...tailColumns];
});

const orderTableData = ref([]);
const orderTableLoading = ref(false);
const paginationCurrentPage = ref(1);
const paginationTotalCount = ref(0);
const paginationPageSize = ref(10);
const paginationPageSizeOptions = [10, 20, 50, 100];
const queryParam = ref({
  supplier_name: '',
  purchase_state: '',
  maritime_port: '',
});
const selectPurchaseSkuDialog = ref(null);
const inputShippingDialog = ref(null);
const checkInWareHouseDialog = ref(null);
const printPurchaseOrderDialog = ref(null);
const payDialog = ref(null);

onMounted(() => {
  // 加载 sku 主数据，用于按订单计算打包体积（snapshot 不冗余 sku_pack_*）
  loadSkuInfo();
  onSearchOrder();
});

const orderPackVolumeM3 = (order: any) => {
  if (!order?.purchase_skus || order.purchase_skus.length === 0) return 0;
  let total = 0;
  order.purchase_skus.forEach((item: any) => {
    const sku = skuMap.value.get(item.sku);
    total += calcPackVolumeM3(
      item.quantity,
      item.sku_unit_quantity,
      sku?.sku_pack_length,
      sku?.sku_pack_width,
      sku?.sku_pack_height,
    );
  });
  return total;
};

watch(orderType, () => {
  orderTableData.value = [];
  paginationCurrentPage.value = 1;
  paginationTotalCount.value = 0;
  onSearchOrder();
});

const onPaginationChange = ({ current, pageSize }) => {
  paginationCurrentPage.value = current;
  paginationPageSize.value = pageSize;
  onSearchOrder();
};
const onSearchOrder = async () => {
  const req = {
    current_page: paginationCurrentPage.value,
    page_size: paginationPageSize.value,
    order_type: orderType.value,
  };
  orderTableLoading.value = true;
  try {
    const res = await searchPurchaseOrder(req);
    paginationTotalCount.value = res.total;
    orderTableData.value = res.list;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询订单异常: ${e}`);
  }
  orderTableLoading.value = false;
};
const onCreatePurchaseOrder = () => {
  selectPurchaseSkuDialog.value.popupDialog(null);
};
const syncSkuToErp = async (order) => {
  orderTableLoading.value = true;
  try {
    await submitPurchaseOrderAndNextStep({ ...order, order_type: orderType.value });
    await onSearchOrder();
  } catch (e) {
    console.log(`同步ERP异常:${e}`);
    await MessagePlugin.error(`同步ERP异常:${e}`);
  }
};
const popupEditDialog = async (order) => {
  console.log(`当前状态： ${order.purchase_step}, 订单类型: ${orderType.value}`);
  if (orderType.value === ORDER_TYPE_OVERSEAS) {
    if (order.purchase_step === '草稿' || order.purchase_step === '境外拣货') {
      selectPurchaseSkuDialog.value.popupDialog(order);
    } else if (order.purchase_step === '已出库') {
      await syncSkuToErp(order);
    }
  } else {
    if (order.purchase_step === '草稿' || order.purchase_step === '供应商捡货中') {
      selectPurchaseSkuDialog.value.popupDialog(order);
    } else if (order.purchase_step === '待发货') {
      inputShippingDialog.value.popupDialog(order);
    } else if (order.purchase_step === '海运中') {
      checkInWareHouseDialog.value.popupDialog(order);
    } else if (order.purchase_step === '已入库') {
      await syncSkuToErp(order);
    }
  }
};
const popupPrintPurchaseOrderDialog = (order) => {
  printPurchaseOrderDialog.value.popupDialog(order);
};

const buildOrderCopyText = (order: any): string => {
  const orderIdLabel = isDomestic.value ? '采购单号' : '销售单号';
  const dateLabel = isDomestic.value ? '采购日期' : '销售日期';
  const lines: string[] = [];
  lines.push(`${orderIdLabel}：EC-${order.purchase_order_id ?? ''}`);
  if (isDomestic.value) {
    lines.push(`供应商：${order.supplier_name ?? ''}`);
  }
  lines.push(`${dateLabel}：${order.purchase_date ?? ''}`);
  if (isDomestic.value) {
    if (order.shipping_company) {
      lines.push(`海运公司：${order.shipping_company}`);
    }
    if (order.maritime_port) {
      lines.push(`国内港口：${order.maritime_port}`);
    }
    if (order.expect_arrive_warehouse_date) {
      lines.push(`预计到货日期：${order.expect_arrive_warehouse_date}`);
    }
  }
  if (order.remark) {
    lines.push(`备注：${order.remark}`);
  }
  lines.push('SKU清单：');
  const skus: any[] = Array.isArray(order.purchase_skus) ? order.purchase_skus : [];
  if (skus.length === 0) {
    lines.push('  （无）');
  } else {
    skus.forEach((item: any, idx: number) => {
      const name = item?.sku_name ?? '';
      const sku = item?.sku ?? '';
      const qty = item?.quantity ?? 0;
      lines.push(`${idx + 1}：${name} (${sku}): ${qty}`);
    });
  }
  lines.push('----');
  return lines.join('\n');
};

const copyTextToClipboard = async (text: string): Promise<boolean> => {
  // 优先使用现代 Clipboard API（需 HTTPS / localhost），失败时回退到 textarea + execCommand
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch (e) {
    console.warn('navigator.clipboard.writeText failed, fallback to execCommand', e);
  }
  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    ta.style.top = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    return ok;
  } catch (e) {
    console.error('execCommand copy failed', e);
    return false;
  }
};

const onCopyOrderText = async (order: any) => {
  const text = buildOrderCopyText(order);
  const ok = await copyTextToClipboard(text);
  if (ok) {
    await MessagePlugin.success('已复制采购单文本到剪贴板');
  } else {
    await MessagePlugin.error('复制失败，请手动复制');
    console.log(text);
  }
};

const popupPayOrderDialog = (order) => {
  payDialog.value.popupDialog(order);
};
const goPreStep = async (order) => {
  const state = getPurchaseOrderPreState(order.purchase_step, orderType.value);
  if (state === null) {
    return;
  }
  order.purchase_step = state;
  await savePurchaseOrder({ ...order, order_type: orderType.value });
  await onSearchOrder();
};
</script>

<style lang="less" scoped></style>
