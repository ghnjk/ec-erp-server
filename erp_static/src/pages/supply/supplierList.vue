<template>
  <div>
    <t-card>
      <div class="table-container">
        <t-table
          :columns="supplierTableColumns"
          :data="supplierTableData"
          :loading="supplierTableLoading"
          bordered
          hover
          row-key="supplier_id"
          stripe
        >
          <template #wechat_account="{ row }">
            ***
          </template>
          <template #detail="{ row }">
            ***
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
  name: 'SupplierList',
};
</script>
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { searchSupplier } from '@/apis/supplierApis';

const supplierTableColumns = [
  {
    width: 120,
    colKey: 'supplier_id',
    title: '供应商id',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'supplier_name',
    title: '供应商名',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'wechat_account',
    title: '微信号',
    align: 'center',
  },
  {
    width: 300,
    colKey: 'detail',
    title: '详细信息',
  },
];
const supplierTableData = ref([]);
const supplierTableLoading = ref(false);
const paginationCurrentPage = ref(1);
const paginationTotalCount = ref(0);
const paginationPageSize = ref(10);
const paginationPageSizeOptions = [10, 20, 50, 100];

onMounted(() => {
  onSearchSupplier();
});

const onPaginationChange = async ({ current, pageSize }) => {
  paginationCurrentPage.value = current;
  paginationPageSize.value = pageSize;
  await onSearchSupplier();
};

const onSearchSupplier = async () => {
  const req = {
    current_page: paginationCurrentPage.value,
    page_size: paginationPageSize.value,
  };
  supplierTableLoading.value = true;
  try {
    const res = await searchSupplier(req);
    paginationTotalCount.value = res.total;
    supplierTableData.value = res.list;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询商户异常: ${e}`);
  }
  supplierTableLoading.value = false;
};
</script>

<style lang="less" scoped></style>
