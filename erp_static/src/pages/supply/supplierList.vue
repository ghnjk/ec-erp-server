<template>
  <div>
    <t-card>
      <t-row>
        <t-col :span="12">
          <t-space size="small" style="margin-bottom: 16px">
            <t-button theme="success" @click="popupAddSupplierDialog">添加供应商</t-button>
          </t-space>
        </t-col>
      </t-row>
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
          <template #operation="{ row }">
            <t-popconfirm content="确认删除该供应商?" @confirm="onDeleteSupplier(row)">
              <t-button size="small" theme="danger" variant="text">删除</t-button>
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
    <t-dialog
      v-if="addSupplierDialog.visible"
      v-model:visible="addSupplierDialog.visible"
      :cancel-btn="null"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      header="添加供应商"
      show-overlay
      width="40%"
    >
      <t-form>
        <t-form-item label="供应商名:" name="supplier_name">
          <t-input v-model="addSupplierDialog.supplier_name" placeholder="请输入供应商名" />
        </t-form-item>
        <t-form-item label="微信号:" name="wechat_account">
          <t-input v-model="addSupplierDialog.wechat_account" placeholder="请输入微信号" />
        </t-form-item>
        <t-form-item label="详细信息:" name="detail">
          <t-textarea
            v-model="addSupplierDialog.detail"
            :autosize="{ minRows: 3, maxRows: 5 }"
            placeholder="请输入详细信息"
          />
        </t-form-item>
      </t-form>
      <br />
      <t-row>
        <t-col :span="9"></t-col>
        <t-col :span="3">
          <t-space>
            <t-button style="float: right" theme="primary" @click="onAddSupplier">提交</t-button>
          </t-space>
        </t-col>
      </t-row>
    </t-dialog>
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
import { searchSupplier, addSupplier, deleteSupplier } from '@/apis/supplierApis';

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
  {
    width: 100,
    colKey: 'operation',
    title: '操作',
    align: 'center',
  },
];
const supplierTableData = ref([]);
const supplierTableLoading = ref(false);
const paginationCurrentPage = ref(1);
const paginationTotalCount = ref(0);
const paginationPageSize = ref(10);
const paginationPageSizeOptions = [10, 20, 50, 100];
const addSupplierDialog = ref({
  visible: false,
  supplier_name: '',
  wechat_account: '',
  detail: '',
});

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

const popupAddSupplierDialog = () => {
  addSupplierDialog.value = {
    visible: true,
    supplier_name: '',
    wechat_account: '',
    detail: '',
  };
};

const onAddSupplier = async () => {
  const supplierName = addSupplierDialog.value.supplier_name.trim();
  if (!supplierName) {
    await MessagePlugin.warning('供应商名不能为空');
    return;
  }
  try {
    await addSupplier({
      supplier_name: supplierName,
      wechat_account: addSupplierDialog.value.wechat_account,
      detail: addSupplierDialog.value.detail,
    });
    await MessagePlugin.success('添加供应商成功');
    addSupplierDialog.value.visible = false;
    await onSearchSupplier();
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`添加供应商异常: ${e}`);
  }
};

const onDeleteSupplier = async (row) => {
  try {
    await deleteSupplier({ supplier_id: row.supplier_id });
    await MessagePlugin.success('删除供应商成功');
    await onSearchSupplier();
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`删除供应商异常: ${e}`);
  }
};
</script>

<style lang="less" scoped></style>
