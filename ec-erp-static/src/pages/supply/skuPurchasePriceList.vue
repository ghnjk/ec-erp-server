<template>
  <div>
    <t-card>
      <div class="table-container">
        <t-table
          :columns="skuTableColumns"
          :data="skuTableData"
          :loading="skuTableLoading"
          bordered
          hover
          row-key="sku"
          stripe
        >
          <template #erp_sku_image_url="{ row }">
            <t-image :src="row.erp_sku_image_url" :style="{ width: '60px', height: '60px' }" />
          </template>
          <template #purchase_price="{ row }">
            {{ row.purchase_price / 100.0 }}
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
  </div>
</template>

<script lang="ts">
export default {
  name: 'SkuPurchasePriceList',
};
</script>
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { searchSkuPurchasePrice } from '@/apis/supplierApis';

const skuTableColumns = [
  {
    width: 120,
    colKey: 'supplier_name',
    title: '供应商',
    align: 'center',
  },
  {
    width: 60,
    colKey: 'erp_sku_image_url',
    title: '商品图片',
    align: 'center',
  },
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
    colKey: 'purchase_price',
    title: '采购价(RMB)',
    align: 'center',
  },
];
const skuTableData = ref([]);
const skuTableLoading = ref(false);
const paginationCurrentPage = ref(1);
const paginationTotalCount = ref(0);
const paginationPageSize = ref(10);
const paginationPageSizeOptions = [10, 20, 50, 100];

onMounted(() => {
  onSearchSku();
});

const onPaginationChange = ({ current, pageSize }) => {
  paginationCurrentPage.value = current;
  paginationPageSize.value = pageSize;
  onSearchSku();
};
const onSearchSku = async () => {
  const req = {
    current_page: paginationCurrentPage.value,
    page_size: paginationPageSize.value,
  };
  skuTableLoading.value = true;
  try {
    const res = await searchSkuPurchasePrice(req);
    paginationTotalCount.value = res.total;
    skuTableData.value = res.list;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询sku异常: ${e}`);
  }
  skuTableLoading.value = false;
};
</script>

<style lang="less" scoped></style>
