<template>
  <div>
    <t-card>
      <t-row>
        <t-col :span="12">
          <t-form layout="inline">
            <t-form-item label="订单状态:" name="status">
              <t-select
                v-model="queryParam.status"
                :options="statusOptions"
                clearable
                placeholder="请选择状态"
                style="width: 150px"
              />
            </t-form-item>
            <t-form-item label="开始日期:" name="begin_date">
              <t-date-picker
                v-model="queryParam.begin_date"
                allow-input
                clearable
                format="YYYY-MM-DD"
                placeholder="开始日期"
                style="width: 150px"
              />
            </t-form-item>
            <t-form-item label="结束日期:" name="end_date">
              <t-date-picker
                v-model="queryParam.end_date"
                allow-input
                clearable
                format="YYYY-MM-DD"
                placeholder="结束日期"
                style="width: 150px"
              />
            </t-form-item>
            <t-form-item>
              <t-space size="small" style="align-items: center; margin-left: 30px">
                <t-button theme="primary" @click="onSearchOrder">查询</t-button>
                <t-button theme="success" @click="onCreateSaleOrder">新建订单</t-button>
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
          row-key="order_id"
          stripe
        >
          <template #sku_order_summary="{ row }">
            <div style="white-space: pre-wrap">{{ row.sku_order_summary }}</div>
          </template>
          <template #total_amount="{ row }">
            {{ currencyFormatter.format(row.total_amount) }}
          </template>
          <template #status="{ row }">
            <t-tag v-if="row.status === '待同步'" theme="warning">{{ row.status }}</t-tag>
            <t-tag v-else-if="row.status === '已同步'" theme="success">{{ row.status }}</t-tag>
            <t-tag v-else>{{ row.status }}</t-tag>
          </template>
          <template #op="{ row }">
            <t-button
              v-if="row.status === '待同步'"
              size="small"
              theme="primary"
              variant="text"
              @click="onEditOrder(row)"
            >
              编辑
            </t-button>
            <t-button
              v-if="row.status === '已同步'"
              size="small"
              theme="primary"
              variant="text"
              @click="onViewOrder(row)"
            >
              查看
            </t-button>
            <t-popconfirm
              v-if="row.status === '待同步'"
              content="确认提交该订单吗？提交后，会将相应的库存从erp中扣除。"
              theme="success"
              @confirm="onSubmitOrder(row)"
            >
              <t-button size="small" theme="success" variant="text">同步erp</t-button>
            </t-popconfirm>
            <t-popconfirm content="确认删除该订单吗？删除后不可恢复" theme="danger" @confirm="onDeleteOrder(row)">
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
    <edit-sale-order-dialog ref="editSaleOrderDialog" @onOrderChange="onSearchOrder()" />
  </div>
</template>

<script lang="ts">
import EditSaleOrderDialog from './components/editSaleOrderDialog.vue';

export default {
  name: 'SaleOrderList',
  components: {
    EditSaleOrderDialog,
  },
};
</script>
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { searchSaleOrder, deleteSaleOrder, submitSaleOrder } from '@/apis/saleApis';
import { loadAllSkuPickingNote, generateOrderSummary } from '@/utils/skuPickingNoteUtil';
import { loadSkuInfo } from '@/utils/skuUtil';
import { loadAllSkuSalePrice } from '@/utils/saleUtil';
import type { ISaleOrder } from '@/apis/dto/saleDto';

const currencyFormatter = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY',
});

// 查询参数
const queryParam = ref({
  status: '',
  begin_date: '',
  end_date: '',
});

// 状态选项
const statusOptions = [
  { label: '待同步', value: '待同步' },
  { label: '已同步', value: '已同步' },
];

// 表格列配置
const orderTableColumns = [
  {
    width: 80,
    colKey: 'order_id',
    title: '订单ID',
    align: 'center',
  },
  {
    width: 150,
    colKey: 'order_date',
    title: '订单日期',
    align: 'center',
  },
  {
    width: 250,
    colKey: 'sku_order_summary',
    title: '订单摘要',
    align: 'left',
  },
  {
    width: 120,
    colKey: 'total_amount',
    title: '总金额',
    align: 'center',
  },
  {
    width: 100,
    colKey: 'status',
    title: '状态',
    align: 'center',
  },
  {
    width: 150,
    colKey: 'modify_time',
    title: '修改时间',
    align: 'center',
  },
  {
    width: 180,
    colKey: 'op',
    title: '操作',
    align: 'center',
    fixed: 'right',
  },
];

// 表格数据
const orderTableData = ref<any[]>([]);
const orderTableLoading = ref(false);

// 分页
const paginationCurrentPage = ref(1);
const paginationPageSize = ref(20);
const paginationPageSizeOptions = [10, 20, 50, 100];
const paginationTotalCount = ref(0);

// 对话框引用
const editSaleOrderDialog = ref();

// 查询订单
const onSearchOrder = async () => {
  orderTableLoading.value = true;
  try {
    const req = {
      status: queryParam.value.status || undefined,
      begin_date: queryParam.value.begin_date || undefined,
      end_date: queryParam.value.end_date || undefined,
      current_page: paginationCurrentPage.value,
      page_size: paginationPageSize.value,
    };

    const res = await searchSaleOrder(req);
    
    // 处理数据，生成订单摘要
    // 注意：标准返回字段是 list，兼容旧版本的 records 字段
    const orderList = res.list || res.records || [];
    orderTableData.value = orderList.map((order: ISaleOrder) => ({
      ...order,
      sku_order_summary: generateOrderSummary(order.sale_sku_list),
    }));
    
    paginationTotalCount.value = res.total || 0;
  } catch (e) {
    console.error('查询销售订单失败:', e);
    MessagePlugin.error(`查询销售订单异常: ${e}`);
  } finally {
    orderTableLoading.value = false;
  }
};

// 分页变化
const onPaginationChange = () => {
  onSearchOrder();
};

// 新建订单
const onCreateSaleOrder = () => {
  editSaleOrderDialog.value.popupDialog(null, false);
};

// 编辑订单
const onEditOrder = (row: any) => {
  editSaleOrderDialog.value.popupDialog(row, false);
};

// 查看订单（只读模式）
const onViewOrder = (row: any) => {
  editSaleOrderDialog.value.popupDialog(row, true);
};

// 提交订单
const onSubmitOrder = async (row: any) => {
  try {
    await submitSaleOrder({ order_id: row.order_id });
    MessagePlugin.success('提交订单成功');
    await onSearchOrder();
  } catch (e) {
    console.error('提交订单失败:', e);
    MessagePlugin.error(`提交订单异常: ${e}`);
  }
};

// 删除订单
const onDeleteOrder = async (row: any) => {
  try {
    await deleteSaleOrder({ order_id: row.order_id });
    MessagePlugin.success('删除订单成功');
    await onSearchOrder();
  } catch (e) {
    console.error('删除订单失败:', e);
    MessagePlugin.error(`删除订单异常: ${e}`);
  }
};

// 组件挂载时
onMounted(async () => {
  // 并行预加载基础数据（不阻塞UI，提前准备好数据供dialog使用）
  Promise.all([
    loadSkuInfo(),
    loadAllSkuSalePrice(),
    loadAllSkuPickingNote(),
  ]).catch((e) => {
    console.error('预加载基础数据失败:', e);
  });
  
  // 查询订单列表
  await onSearchOrder();
});
</script>

<style scoped lang="less">
.table-container {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>

