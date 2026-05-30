<template>
  <div>
    <t-card>
      <br />
      <t-row>
        <t-col :span="12">
          <t-form layout="inline">
            <t-form-item label="物流方式">
              <t-radio-group v-model="shipProvider" name="shipping" variant="default-filled" @change="onShippingChange">
                <t-space direction="vertical">
                  <t-radio v-for="item in shippingOptions" :value="item.value">
                    {{ item.label }}
                  </t-radio>
                </t-space>
              </t-radio-group>
            </t-form-item>
            <t-form-item>
              <t-space size="small" style="align-items: center; margin-left: 30px">
                <t-button theme="default" @click="onSearchOrder">刷 新</t-button>
                <t-button theme="primary" @click="onPrintOrder">打 印</t-button>
              </t-space>
            </t-form-item>
          </t-form>
        </t-col>
      </t-row>
      <br />
      <div class="table-container">
        <t-pagination
          v-model="paginationCurrentPage"
          v-model:pageSize="paginationPageSize"
          :page-size-options="paginationPageSizeOptions"
          :total="paginationTotalCount"
          class="pagination"
          @change="onPaginationChange"
        />
        <t-table
          :columns="orderTableColumns"
          :data="orderTableData"
          :loading="orderTableLoading"
          :select-on-row-click="true"
          :selected-row-keys="orderTableSelectedRowKeys"
          bordered
          hover
          row-key="id"
          stripe
          @select-change="rehandleSelectChange"
        >
          <template #multilingualViewStatus="{ row }">
            {{ row.printLabelMark > 0 ? '[已打印]' + row.multilingualViewStatus : row.multilingualViewStatus }}
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
    <order-print-confirm-dialog ref="orderPrintConfirmDialog"></order-print-confirm-dialog>
  </div>
</template>

<script lang="ts">
import OrderPrintConfirmDialog from './components/orderPrintConfirmDialog.vue';

export default {
  name: 'PrintOrder',
  components: {
    OrderPrintConfirmDialog,
  },
};
</script>
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { MessagePlugin, TableProps } from 'tdesign-vue-next';
import { useRoute } from 'vue-router';
import { loginWithToken } from '@/apis/sysApis';
import { getWaitPrintOrderShipProviderList, searchWaitPrintOrder } from '@/apis/warehouseApis';

const userName = ref('未登录');
const shipProvider = ref(null);
const orderTableColumns = [
  {
    width: 50,
    colKey: 'row-select',
    type: 'multiple',
    // 允许单选(Radio)取消行选中
    checkProps: { allowUncheck: true },
    align: 'center',
  },
  {
    width: 120,
    colKey: 'id',
    title: 'id',
    align: 'center',
  },
  {
    width: 60,
    colKey: 'platformOrderId',
    title: '订单号',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'packageNo',
    title: '包裹号',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'shippingCarrierName',
    title: '物流',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'trackingNo',
    title: '运单号',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'multilingualViewStatus',
    title: '状态',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'amount',
    title: '金额',
    align: 'center',
  },
  {
    width: 120,
    colKey: 'platform',
    title: '平台',
    align: 'center',
  },
];
const orderTableData = ref([]);
const orderTableLoading = ref(false);
const orderTableSelectedRowKeys = ref<TableProps['selectedRowKeys']>([]);
const paginationCurrentPage = ref(1);
const paginationTotalCount = ref(0);
const paginationPageSize = ref(300);
const paginationPageSizeOptions = [10, 20, 50, 100, 200, 300, 500, 1000, 5000];

const shippingOptions = ref([]);
const orderPrintConfirmDialog = ref(null);
onMounted(async () => {
  const { query } = useRoute();
  const { token } = query;
  try {
    const userInfo: any = await loginWithToken(token);
    userName.value = userInfo.userName;
    await loadWaitPrintOrderStatics();
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`登陆异常: ${e}`);
  }
});

const loadWaitPrintOrderStatics = async () => {
  try {
    const res = await getWaitPrintOrderShipProviderList();
    const shipProviderList = res.ship_provider_list;
    console.log('shipProviderList', shipProviderList);
    shippingOptions.value = [];
    shipProviderList.forEach((item) => {
      shippingOptions.value.push({
        label: `${item.name}(${item.count})`,
        value: item.id,
      });
    });
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询订单统计信息异常: ${e}`);
  }
};
const onShippingChange = (value, ctx) => {
  shipProvider.value = value;
  onSearchOrder();
};
const rehandleSelectChange = (value, { selectedRowData }) => {
  orderTableSelectedRowKeys.value = value;
};
const onPaginationChange = ({ current, pageSize }) => {
  paginationCurrentPage.value = current;
  paginationPageSize.value = pageSize;
  onSearchOrder();
};
const onSearchOrder = async () => {
  orderTableLoading.value = true;
  await loadWaitPrintOrderStatics();
  if (shipProvider.value === null) {
    orderTableLoading.value = false;
    return;
  }
  try {
    const req = {
      shipping_provider_id: shipProvider.value,
      current_page: paginationCurrentPage.value,
      page_size: paginationPageSize.value,
    };
    orderTableSelectedRowKeys.value = [];
    const res = await searchWaitPrintOrder(req);
    paginationTotalCount.value = res.total;
    orderTableData.value = res.list;
    console.log('waitOrder', paginationTotalCount.value, orderTableData.value);
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询订单信息异常: ${e}`);
  }
  orderTableLoading.value = false;
};
const onPrintOrder = async () => {
  const selectOrderIds = new Set();
  orderTableSelectedRowKeys.value.forEach((item) => {
    selectOrderIds.add(item);
  });
  console.log('selected: ', selectOrderIds);
  if (selectOrderIds.size <= 0) {
    MessagePlugin.info('请先选中需要打印的订单.');
    return;
  }
  const orderList = [];
  orderTableData.value.forEach((item) => {
    if (selectOrderIds.has(item.id)) {
      orderList.push(item);
    }
  });
  if (orderList.length != selectOrderIds.size) {
    MessagePlugin.error('选中的订单信息缺失。.');
    return;
  }

  orderPrintConfirmDialog.value.popupDialog(paginationTotalCount.value, orderList);
};
</script>
<style scoped>
.page-header {
  margin: 15px;
}
</style>
