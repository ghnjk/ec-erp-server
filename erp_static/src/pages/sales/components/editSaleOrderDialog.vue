<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :cancel-btn="null"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      :header="isReadonly ? '查看销售订单' : isCreateMode ? '新建销售订单' : '编辑销售订单'"
      show-overlay
      width="85%"
    >
      <t-row>
        <t-col :span="10">
          <t-form layout="inline">
            <t-form-item label="订单日期:" name="orderDate" required>
              <t-date-picker
                v-model="orderDate"
                :disabled="isReadonly"
                allow-input
                clearable
                format="YYYY-MM-DD"
                placeholder="选择订单日期"
                style="width: 200px"
              />
            </t-form-item>
          </t-form>
        </t-col>
      </t-row>
      <t-row v-if="!isReadonly">
        <t-col :span="8">
          <t-form layout="inline">
            <t-form-item label="SKU分组:" name="skuGroupName">
              <t-select
                v-model="skuGroupName"
                :options="skuGroupNameOptions"
                filterable
                placeholder="-请选择SKU分组-"
                style="width: 200px"
              />
            </t-form-item>
            <t-form-item label="SKU:" name="selectedSku">
              <t-select
                v-model="selectedSku"
                :options="currentSkuOptions"
                filterable
                placeholder="-请选择SKU-"
                style="width: 250px"
              />
            </t-form-item>
          </t-form>
        </t-col>
        <t-col :span="3">
          <t-button theme="default" @click="onAddSku">添加SKU</t-button>
        </t-col>
        <t-col :span="7">
          <h3 style="text-align: right">总金额：{{ currencyFormatter.format(totalAmount) }}</h3>
        </t-col>
      </t-row>
      <t-row v-else>
        <t-col :span="12"></t-col>
        <t-col :span="12">
          <h3 style="text-align: right">总金额：{{ currencyFormatter.format(totalAmount) }}</h3>
        </t-col>
      </t-row>
      <br />
      <div class="table-container">
        <t-table
          :bordered="true"
          :columns="saleSkuTableColumns"
          :data="saleSkuTableData"
          lazy-load
          resizable
          row-key="idx"
          table-layout="fixed"
        >
          <template #sku="{ row }">
            <t-space>
              <t-image :src="row.erp_sku_image_url" :style="{ width: '30px', height: '30px' }" />
              {{ row.sku }}
            </t-space>
          </template>
          <template #picking_info="{ row }">
            {{ row.picking_display_text }}
          </template>
          <template #total_amount="{ row }">
            {{ currencyFormatter.format(row.total_amount) }}
          </template>
          <template #operation="{ row }">
            <t-button v-if="!isReadonly" size="small" theme="danger" variant="text" @click="onDeleteSku(row)">
              删除
            </t-button>
          </template>
        </t-table>
        <br />
        <t-row>
          <t-col :span="9"></t-col>
          <t-col :span="3">
            <t-space>
              <t-button style="float: right" theme="default" @click="visible = false">
                {{ isReadonly ? '关闭' : '取消' }}
              </t-button>
              <t-button v-if="!isReadonly" style="float: right" theme="primary" @click="onSaveSaleOrder">
                保存
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
  name: 'EditSaleOrderDialog',
};
</script>
<script lang="ts" setup>
import { ref, computed, defineExpose, defineEmits, watch } from 'vue';
import { InputNumber, MessagePlugin, DialogPlugin } from 'tdesign-vue-next';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { skuGroupNameOptions, skuGroupMap, skuMap, loadSkuInfo } from '@/utils/skuUtil';
import { loadAllSkuSalePrice, getSkuSalePrice, batchUpdateSkuSalePrice } from '@/utils/saleUtil';
import { calculatePickingInfo } from '@/utils/skuPickingNoteUtil';
import { createSaleOrder, updateSaleOrder } from '@/apis/saleApis';
import type { ISaleOrder, ISaleSkuItem } from '@/apis/dto/saleDto';

// 扩展 dayjs 时区插件
dayjs.extend(utc);
dayjs.extend(timezone);

const currencyFormatter = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY',
});

const visible = ref(false);
const isCreateMode = ref(true);
const isReadonly = ref(false);
const saleOrder = ref<ISaleOrder | null>(null);
const orderDate = ref('');
const skuGroupName = ref('');
const selectedSku = ref('');
const saleSkuTableData = ref<any[]>([]);
const totalAmount = ref(0.0);
const emit = defineEmits(['onOrderChange']);

// 当前SKU分组下的SKU选项
const currentSkuOptions = computed(() => {
  if (!skuGroupName.value) {
    return [];
  }
  const skuList = skuGroupMap.value.get(skuGroupName.value);
  if (!skuList) {
    return [];
  }
  return skuList.map((item) => ({
    label: `${item.sku} - ${item.sku_name}`,
    value: item.sku,
  }));
});

// 表格列配置（动态根据只读模式调整）
const saleSkuTableColumns = computed(() => {
  const columns: any[] = [
    {
      width: 100,
      colKey: 'sku_group',
      title: 'SKU分组',
      align: 'center',
    },
    {
      width: 120,
      colKey: 'sku_name',
      title: '商品名',
      align: 'center',
    },
    {
      width: 150,
      colKey: 'sku',
      title: '商品SKU',
      align: 'center',
    },
    {
      width: 100,
      colKey: 'quantity',
      title: '数量',
      align: 'center',
      edit: isReadonly.value
        ? undefined
        : {
            component: InputNumber,
            props: {
              autofocus: true,
              min: 1,
            },
            validateTrigger: 'change',
            abortEditOnEvent: ['onEnter', 'onBlur'],
            onEdited: (context: any) => {
              saleSkuTableData.value.splice(context.rowIndex, 1, context.newRowData);
              updateRowPickingInfo(context.rowIndex);
              calcTotalAmount();
            },
            rules: [
              {
                required: true,
                message: '不能为空',
              },
            ],
            defaultEditable: true,
          },
    },
    {
      width: 150,
      colKey: 'picking_info',
      title: '拣货信息',
      align: 'center',
    },
    {
      width: 100,
      colKey: 'unit_price',
      title: '单价',
      align: 'center',
      edit: isReadonly.value
        ? undefined
        : {
            component: InputNumber,
            props: {
              autofocus: true,
              min: 0.01,
              step: 0.01,
            },
            validateTrigger: 'change',
            abortEditOnEvent: ['onEnter', 'onBlur'],
            onEdited: (context: any) => {
              saleSkuTableData.value.splice(context.rowIndex, 1, context.newRowData);
              calcTotalAmount();
            },
            rules: [
              {
                required: true,
                message: '不能为空',
              },
            ],
            defaultEditable: false,
          },
    },
    {
      width: 120,
      colKey: 'total_amount',
      title: '总价',
      align: 'center',
    },
  ];

  // 只有非只读模式才显示操作列
  if (!isReadonly.value) {
    columns.push({
      width: 80,
      colKey: 'operation',
      title: '操作',
      align: 'center',
    });
  }

  return columns;
});

// 更新某行的拣货信息
const updateRowPickingInfo = (rowIndex: number) => {
  const row = saleSkuTableData.value[rowIndex];
  const pickingInfo = calculatePickingInfo(row.sku, row.quantity);
  row.picking_display_text = pickingInfo.display_text;
  row.total_amount = row.unit_price * row.quantity;
};

// 添加SKU
const onAddSku = () => {
  if (!selectedSku.value) {
    MessagePlugin.warning('请先选择SKU');
    return;
  }

  // 检查是否已添加
  const exists = saleSkuTableData.value.find((item) => item.sku === selectedSku.value);
  if (exists) {
    MessagePlugin.warning('该SKU已添加');
    return;
  }

  const skuInfo = skuMap.value.get(selectedSku.value);
  if (!skuInfo) {
    MessagePlugin.error('SKU信息不存在');
    return;
  }

  // 获取销售价格
  const salePrice = getSkuSalePrice(selectedSku.value);

  const newRow = {
    idx: saleSkuTableData.value.length + 1,
    sku: skuInfo.sku,
    sku_group: skuInfo.sku_group,
    sku_name: skuInfo.sku_name,
    erp_sku_image_url: skuInfo.erp_sku_image_url,
    quantity: 1,
    unit_price: salePrice || 0,
    total_amount: salePrice || 0,
    picking_display_text: '',
  };

  saleSkuTableData.value.push(newRow);
  updateRowPickingInfo(saleSkuTableData.value.length - 1);
  calcTotalAmount();
  selectedSku.value = '';
};

// 删除SKU
const onDeleteSku = (row: any) => {
  const index = saleSkuTableData.value.findIndex((item) => item.idx === row.idx);
  if (index !== -1) {
    saleSkuTableData.value.splice(index, 1);
    // 重新设置idx
    saleSkuTableData.value.forEach((item, i) => {
      item.idx = i + 1;
    });
    calcTotalAmount();
  }
};

// 计算总金额
const calcTotalAmount = () => {
  totalAmount.value = 0;
  saleSkuTableData.value.forEach((item) => {
    item.total_amount = item.quantity * item.unit_price;
    totalAmount.value += item.total_amount;
  });
};

// 打开对话框
const popupDialog = async (order: ISaleOrder | null, readonly = false) => {
  // 设置只读模式
  isReadonly.value = readonly;
  
  // 加载基础数据
  await loadSkuInfo();
  await loadAllSkuSalePrice();

  if (order) {
    // 编辑/查看模式
    isCreateMode.value = false;
    saleOrder.value = order;
    orderDate.value = order.order_date;
    saleSkuTableData.value = [];

    order.sale_sku_list.forEach((item, index) => {
      const skuInfo = skuMap.value.get(item.sku);
      const pickingInfo = calculatePickingInfo(item.sku, item.quantity);
      
      saleSkuTableData.value.push({
        idx: index + 1,
        sku: item.sku,
        sku_group: item.sku_group || skuInfo?.sku_group || '',
        sku_name: item.sku_name || skuInfo?.sku_name || '',
        erp_sku_image_url: item.erp_sku_image_url || skuInfo?.erp_sku_image_url || '',
        quantity: item.quantity,
        unit_price: item.unit_price,
        total_amount: item.total_amount || item.unit_price * item.quantity,
        picking_display_text: pickingInfo.display_text,
      });
    });
  } else {
    // 新建模式
    isCreateMode.value = true;
    saleOrder.value = null;
    // 使用东八区（Asia/Shanghai）时区获取当前日期
    orderDate.value = dayjs().tz('Asia/Shanghai').format('YYYY-MM-DD');
    saleSkuTableData.value = [];
  }

  skuGroupName.value = '';
  selectedSku.value = '';
  calcTotalAmount();
  visible.value = true;
};

// 构建SKU列表
const buildSaleSkuList = (): ISaleSkuItem[] => {
  return saleSkuTableData.value.map((item) => ({
    sku: item.sku,
    sku_group: item.sku_group,
    sku_name: item.sku_name,
    erp_sku_image_url: item.erp_sku_image_url,
    quantity: item.quantity,
    unit_price: item.unit_price,
    total_amount: item.total_amount,
  }));
};

// 保存销售订单
const onSaveSaleOrder = async () => {
  // 校验
  if (!orderDate.value) {
    MessagePlugin.error('请选择订单日期');
    return;
  }

  if (saleSkuTableData.value.length === 0) {
    MessagePlugin.error('请至少添加一个商品');
    return;
  }

  // 检查是否有未填写单价的商品
  const invalidItems = saleSkuTableData.value.filter((item) => !item.unit_price || item.unit_price <= 0);
  if (invalidItems.length > 0) {
    MessagePlugin.error('存在未设置单价的商品，请检查');
    return;
  }

  try {
    // 1. 批量更新SKU销售价格（如有变化）
    await batchUpdateSkuSalePrice(saleSkuTableData.value);

    // 2. 保存或更新订单
    const sale_sku_list = buildSaleSkuList();

    if (isCreateMode.value) {
      const createReq = {
        order_date: orderDate.value,
        sale_sku_list,
      };
      console.log(`创建销售订单:`, createReq);
      await createSaleOrder(createReq);
      MessagePlugin.success('创建销售订单成功');
    } else {
      const updateReq = {
        order_id: saleOrder.value!.order_id!,
        order_date: orderDate.value,
        sale_sku_list,
      };
      console.log(`更新销售订单:`, updateReq);
      await updateSaleOrder(updateReq);
      MessagePlugin.success('更新销售订单成功');
    }

    visible.value = false;
    emit('onOrderChange');
  } catch (e) {
    console.error('保存销售订单失败:', e);
    MessagePlugin.error(`保存销售订单异常: ${e}`);
  }
};

defineExpose({ popupDialog });
</script>

<style scoped lang="less">
.table-container {
  max-height: 600px;
  overflow-y: auto;
}
</style>

