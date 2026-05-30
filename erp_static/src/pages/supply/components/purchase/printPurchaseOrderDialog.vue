<template>
  <div>
    <t-dialog
      v-if="visible"
      v-model:visible="visible"
      :cancel-btn="null"
      :confirm-btn="null"
      header="打印采购单"
      show-overlay
      width="80%"
      @confirm="printDialog"
    >
      <div id="printDiv" ref="printDiv">
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
            <template #sku="{ row }">
              <t-space>
                <t-image :src="row.erp_sku_image_url" :style="{ width: '30px', height: '30px' }" />
                {{ row.sku }}
              </t-space>
            </template>
            <template #pack_volume_m3="{ row }">
              {{ formatVolumeM3(rowPackVolumeM3(row)) }}
            </template>
          </t-table>
          <div style="margin-top: 8px; text-align: right; font-weight: 600">
            合计打包体积：{{ formatVolumeM3(totalPackVolumeM3) }} m³
          </div>
        </div>
      </div>
      <br />
      <hr />
      <br />
      <t-button style="float: right; margin-left: 10px" theme="success" @click="saveAsPic">保存图片</t-button>
      <t-button v-print="printSetting" style="float: right" theme="primary">打印</t-button>
    </t-dialog>
  </div>
</template>

<script lang="tsx">
export default {
  name: 'PrintPurchaseOrderDialog•',
};
</script>
<script lang="tsx" setup>
import { ref, computed, defineExpose, defineEmits } from 'vue';
import { TableProps, DialogProps } from 'tdesign-vue-next';
import print from 'vue3-print-nb';
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';
import { skuMap, loadSkuInfo, calcPackVolumeM3, formatVolumeM3 } from '@/utils/skuUtil';

const vPrint = print;
const printSetting = ref({
  id: 'printDiv',
});
const printDiv = ref(null);

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
    colKey: 'sku_unit_name',
    title: '单位',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'pack_volume_m3',
    title: '打包体积(m³)',
    align: 'center',
  },
];

const rowPackVolumeM3 = (row: any) =>
  calcPackVolumeM3(row.quantity, row.sku_unit_quantity, row.sku_pack_length, row.sku_pack_width, row.sku_pack_height);

const totalPackVolumeM3 = computed(() => {
  let total = 0;
  skuTableData.value.forEach((item: any) => {
    total += rowPackVolumeM3(item);
  });
  return total;
});

const saveAsPic = () => {
  html2canvas(printDiv.value).then((canvas) => {
    canvas.toBlob((blob) => {
      saveAs(blob, `采购单-${purchaseOrder.value.purchase_date}.png`);
    });
  });
};

const popupDialog = async (pOrder: any) => {
  await loadSkuInfo();
  console.log(pOrder);
  purchaseOrder.value = pOrder;
  skuTableData.value = [];
  purchaseOrder.value.purchase_skus.forEach((item) => {
    const sku = skuMap.value.get(item.sku);
    skuTableData.value.push({
      idx: skuTableData.value.length + 1,
      sku_group: item.sku_group,
      sku_name: item.sku_name,
      sku: item.sku,
      erp_sku_image_url: sku?.erp_sku_image_url,
      quantity: item.quantity,
      sku_unit_name: sku?.sku_unit_name,
      sku_unit_quantity: sku?.sku_unit_quantity,
      // 体积来自 sku 主数据（snapshot 不冗余，符合后端 add-sku-pack-volume 设计 D4）
      sku_pack_length: sku?.sku_pack_length,
      sku_pack_width: sku?.sku_pack_width,
      sku_pack_height: sku?.sku_pack_height,
      avg_sell_quantity: sku?.avg_sell_quantity,
      shipping_stock_quantity: sku?.shipping_stock_quantity,
    });
  });
  visible.value = true;
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
const printDialog = () => {};
defineExpose({ popupDialog });
</script>
<style scoped></style>
