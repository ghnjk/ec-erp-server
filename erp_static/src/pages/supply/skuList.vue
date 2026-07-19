<template>
  <div>
    <t-card>
      <t-row>
        <t-col :span="12">
          <t-form layout="inline">
            <t-form-item label="sku分组:" name="skuGroup">
              <t-select
                v-model="queryParam.skuGroup"
                :options="skuGroupNameOptions"
                clearable
                filterable
                placeholder="-请选择商品分组-"
                style="width: 150px; display: inline-block"
              />
            </t-form-item>
            <t-form-item label="商品名:" name="skuName">
              <t-input v-model="queryParam.skuName" placeholder="商品名" />
            </t-form-item>
            <t-form-item label="商品SKU:" name="sku">
              <t-input v-model="queryParam.sku" placeholder="商品SKU" />
            </t-form-item>
            <t-form-item label="支撑天数:" name="supportDays">
              <t-input-number v-model="queryParam.supportDays" theme="column"></t-input-number>
            </t-form-item>
            <t-form-item>
              <t-space size="small" style="align-items: center; margin-left: 30px">
                <t-button theme="primary" @click="onSearchSku">查询</t-button>
              </t-space>
              <t-space size="small" style="align-items: center; margin-left: 30px">
                <t-button theme="success" @click="popupAddSkuDialog">添加SKU</t-button>
              </t-space>
              <t-space size="small" style="align-items: center; margin-left: 30px">
                <t-button theme="default" variant="outline" @click="popupColumnSettingDialog">列设置</t-button>
              </t-space>
              <t-space size="small" style="align-items: center; margin-left: 30px">
                <t-button theme="default" variant="text" @click="onSyncAllSku">同步所有库存</t-button>
              </t-space>
            </t-form-item>
          </t-form>
        </t-col>
      </t-row>
      <br />
      <div class="table-container">
        <t-table
          :columns="skuTableColumns"
          :data="skuTableData"
          :fixed-rows="[0, 0]"
          :loading="skuTableLoading"
          :max-height="1000"
          :show-sort-column-bg-color="true"
          :sort="sortTable"
          bordered
          hover
          row-key="sku"
          stripe
          @sort-change="sortTableChange"
        >
          <template #avg_sell_quantity="{ row }">
            {{ row.avg_sell_quantity.toFixed(2) }}
          </template>
          <template #erp_sku_image_url="{ row }">
            <t-image :src="row.erp_sku_image_url" :style="{ width: '60px', height: '60px' }" />
          </template>
          <template #inventory_pkg="{ row }">
            {{ calcInventoryPkg(row) }}
          </template>
          <template #avg_sell_quantity_pkg="{ row }">
            {{ calcAvgSellQuantityPkg(row) }}
          </template>
          <template #shipping_stock_quantity_pkg="{ row }">
            {{ calcShippingStockQuantityPkg(row) }}
          </template>
          <template #shipping_stock_support_days="{ row }">
            {{ calcShippingSupportDays(row) }}
          </template>
          <template #pack_volume_m3="{ row }">
            {{ formatVolumeM3(rowPackVolumeM3(row)) }}
          </template>
          <template #operation="{ row }">
            <t-button size="small" theme="danger" variant="text" @click="popupDeleteSkuDialog(row)">删除</t-button>
          </template>
        </t-table>
        <t-pagination
          v-model="paginationCurrentPage"
          v-model:page-size="paginationPageSize"
          :page-size-options="paginationPageSizeOptions"
          :total="paginationTotalCount"
          class="pagination"
          @change="onPaginationChange"
        />
      </div>
    </t-card>
    <t-dialog
      v-if="addSkuDialog.visible"
      v-model:visible="addSkuDialog.visible"
      :cancel-btn="null"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      header="添加SKU"
      show-overlay
      width="60%"
    >
      <t-alert message="需要提前在bigseller添加好sku" />
      <br />
      <t-form>
        <t-form-item label="sku:" name="supplier_name">
          <t-textarea
            v-model="addSkuDialog.skus"
            :autosize="{ minRows: 3, maxRows: 5 }"
            name="description"
            placeholder="需要添加的sku。多个换行"
          />
        </t-form-item>
      </t-form>
      <br />
      <t-row>
        <t-col :span="9"></t-col>
        <t-col :span="3">
          <t-space>
            <t-button style="float: right" theme="primary" @click="onAddSku">批量添加</t-button>
          </t-space>
        </t-col>
      </t-row>
    </t-dialog>
    <t-dialog
      v-if="columnSettingDialog.visible"
      v-model:visible="columnSettingDialog.visible"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      header="自定义显示列"
      show-overlay
      width="50%"
      @confirm="onConfirmColumnSetting"
    >
      <t-space style="margin-bottom: 12px">
        <t-button size="small" variant="text" @click="onSelectAllCols">全选</t-button>
        <t-button size="small" variant="text" @click="onClearAllCols">清空</t-button>
        <t-button size="small" variant="text" @click="onResetCols">恢复默认</t-button>
      </t-space>
      <t-checkbox-group v-model="columnSettingDialog.selectedKeys" style="display: flex; flex-wrap: wrap; gap: 12px">
        <t-checkbox v-for="col in allColumnDefs" :key="col.colKey" :value="col.colKey" :disabled="col.required">
          {{ col.title }}
          <span v-if="col.required" style="color: var(--td-text-color-placeholder)">（必显）</span>
        </t-checkbox>
      </t-checkbox-group>
    </t-dialog>
    <t-dialog
      v-if="deleteSkuDialog.visible"
      v-model:visible="deleteSkuDialog.visible"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="{
        content: '确认删除',
        theme: 'danger',
        disabled: !isDeleteSkuConfirmed,
        loading: deleteSkuDialog.loading,
      }"
      header="删除SKU"
      show-overlay
      width="520px"
      @confirm="onDeleteSku"
    >
      <div class="delete-sku-info">
        <t-image
          :src="deleteSkuDialog.skuInfo?.erp_sku_image_url"
          :style="{ width: '96px', height: '96px' }"
          fit="cover"
        />
        <div class="delete-sku-detail">
          <div><span>SKU：</span>{{ deleteSkuDialog.skuInfo?.sku }}</div>
          <div><span>商品名：</span>{{ deleteSkuDialog.skuInfo?.sku_name || '--' }}</div>
          <div><span>SKU分组：</span>{{ deleteSkuDialog.skuInfo?.sku_group || '--' }}</div>
          <div><span>BigSeller商品名：</span>{{ deleteSkuDialog.skuInfo?.erp_sku_name || '--' }}</div>
        </div>
      </div>
      <t-alert theme="error" message="删除后该 SKU 后，不可恢复。请谨慎操作。" />
      <div class="delete-sku-confirm-form">
        <div class="delete-sku-confirm-label">
          请输入 <code>{{ deleteSkuDialog.skuInfo?.sku }}</code> 以确认删除
        </div>
        <t-input v-model="deleteSkuDialog.confirmSku" placeholder="请输入完整SKU" />
      </div>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'SkuList',
};
</script>
<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { MessagePlugin, InputNumber, Input, TableProps } from 'tdesign-vue-next';
import { saveSku, searchSku, syncAllSku, addSku, deleteSku } from '@/apis/supplierApis';
import { skuGroupNameOptions, loadSkuInfo, calcPackVolumeM3PerUnit, formatVolumeM3 } from '@/utils/skuUtil';

// 列设置 localStorage key（v2：新增必显「操作」列）
const COL_VISIBILITY_STORAGE_KEY = 'sku_list_visible_cols_v2';

const queryParam = ref({
  skuGroup: '',
  skuName: '',
  sku: '',
  supportDays: '',
});
const sortTable = ref<TableProps['sort']>({
  sortBy: 'avg_sell_quantity',
  descending: true,
});
// 通用：可编辑单元格定义
const buildEditableCell = (component: any, defaultEditable = false) => ({
  component,
  props: { autofocus: true },
  validateTrigger: 'change',
  abortEditOnEvent: ['onEnter', 'onBlur'],
  onEdited: async (context: any) => {
    await onSaveSku(context.newRowData);
    await onSearchSku();
  },
  rules: [{ required: true, message: '不能为空' }],
  defaultEditable,
});

// 全部列定义。required=true 的列（如商品图片 / SKU）始终展示且不可在"列设置"中关闭。
const allColumnDefs: Array<any> = [
  { width: 60, colKey: 'erp_sku_image_url', fixed: 'left', title: '商品图片', align: 'center', required: true },
  {
    width: 120,
    colKey: 'sku_group',
    fixed: 'left',
    title: 'sku分组',
    align: 'center',
    edit: buildEditableCell(Input),
  },
  {
    width: 120,
    colKey: 'sku_name',
    fixed: 'left',
    title: '商品名',
    align: 'center',
    edit: buildEditableCell(Input),
  },
  { width: 120, colKey: 'sku', title: '商品SKU', align: 'center', required: true },
  { width: 120, colKey: 'erp_sku_name', title: 'BigSeller商品名', align: 'center' },
  {
    width: 120,
    colKey: 'sku_unit_name',
    title: '采购单位',
    align: 'center',
    edit: buildEditableCell(Input),
  },
  {
    width: 120,
    colKey: 'sku_unit_quantity',
    title: '单位的SKU数',
    align: 'center',
    sortType: 'all',
    sorter: true,
    edit: buildEditableCell(InputNumber),
  },
  {
    width: 120,
    colKey: 'sku_pack_length',
    title: '打包长(cm)',
    align: 'center',
    sortType: 'all',
    sorter: true,
    edit: buildEditableCell(InputNumber),
  },
  {
    width: 120,
    colKey: 'sku_pack_width',
    title: '打包宽(cm)',
    align: 'center',
    sortType: 'all',
    sorter: true,
    edit: buildEditableCell(InputNumber),
  },
  {
    width: 120,
    colKey: 'sku_pack_height',
    title: '打包高(cm)',
    align: 'center',
    sortType: 'all',
    sorter: true,
    edit: buildEditableCell(InputNumber),
  },
  { width: 120, colKey: 'pack_volume_m3', title: '打包体积(m³)', align: 'center' },
  { width: 120, colKey: 'inventory', sortType: 'all', sorter: true, title: '库存-SKU', align: 'center' },
  { width: 120, colKey: 'inventory_pkg', sortType: 'all', sorter: true, title: '库存-采购单位', align: 'center' },
  { width: 120, colKey: 'avg_sell_quantity', title: '平均日销-SKU', align: 'center', sortType: 'all', sorter: true },
  {
    width: 120,
    colKey: 'avg_sell_quantity_pkg',
    title: '平均日销-采购单位',
    align: 'center',
    sortType: 'all',
    sorter: true,
  },
  {
    width: 120,
    colKey: 'inventory_support_days',
    title: '库存支撑天数',
    align: 'center',
    sortType: 'all',
    sorter: true,
  },
  {
    width: 120,
    colKey: 'shipping_stock_quantity',
    title: '海运中-SKU',
    align: 'center',
    sortType: 'all',
    sorter: true,
  },
  {
    width: 120,
    colKey: 'shipping_stock_quantity_pkg',
    title: '海运中-采购单位',
    align: 'center',
    sortType: 'all',
    sorter: true,
  },
  {
    width: 120,
    colKey: 'shipping_stock_support_days',
    title: '海运中-支撑天数',
    align: 'center',
    sortType: 'all',
    sorter: true,
  },
  { width: 80, colKey: 'operation', fixed: 'right', title: '操作', align: 'center', required: true },
];

// 默认显示的列（保持本次改动前的列集合 + 新增 3 个体积字段中的"打包体积(m³)" 汇总列；
// 长/宽/高 默认不展示，避免列过多，用户可在"列设置"中开启）
const DEFAULT_VISIBLE_COL_KEYS: string[] = [
  'erp_sku_image_url',
  'sku_group',
  'sku_name',
  'sku',
  'erp_sku_name',
  'sku_unit_name',
  'sku_unit_quantity',
  'pack_volume_m3',
  'inventory',
  'inventory_pkg',
  'avg_sell_quantity',
  'avg_sell_quantity_pkg',
  'inventory_support_days',
  'shipping_stock_quantity',
  'shipping_stock_quantity_pkg',
  'shipping_stock_support_days',
  'operation',
];

const REQUIRED_COL_KEYS: string[] = allColumnDefs.filter((c) => c.required).map((c) => c.colKey);

const withRequiredColKeys = (keys: string[]): string[] => {
  const set = new Set<string>(keys);
  REQUIRED_COL_KEYS.forEach((k) => set.add(k));
  // 保持 allColumnDefs 顺序，避免操作列跑到中间
  return allColumnDefs.map((c) => c.colKey).filter((k) => set.has(k));
};

const loadVisibleColKeys = (): string[] => {
  try {
    const raw = localStorage.getItem(COL_VISIBILITY_STORAGE_KEY);
    if (!raw) return withRequiredColKeys(DEFAULT_VISIBLE_COL_KEYS);
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return withRequiredColKeys(DEFAULT_VISIBLE_COL_KEYS);
    return withRequiredColKeys(parsed);
  } catch (e) {
    console.warn('loadVisibleColKeys failed', e);
    return withRequiredColKeys(DEFAULT_VISIBLE_COL_KEYS);
  }
};

const visibleColKeys = ref<string[]>(loadVisibleColKeys());

const skuTableColumns = computed(() => {
  const keep = new Set(withRequiredColKeys(visibleColKeys.value));
  return allColumnDefs.filter((c) => keep.has(c.colKey));
});

const rowPackVolumeM3 = (row: any) =>
  calcPackVolumeM3PerUnit(row.sku_pack_length, row.sku_pack_width, row.sku_pack_height);

const skuTableData = ref<any[]>([]);
const skuTableLoading = ref(false);
const paginationCurrentPage = ref(1);
const paginationTotalCount = ref(0);
const paginationPageSize = ref(10);
const paginationPageSizeOptions = [10, 20, 50, 100];
const addSkuDialog = ref({
  visible: false,
  skus: '',
});

const deleteSkuDialog = ref({
  visible: false,
  loading: false,
  confirmSku: '',
  skuInfo: null as any,
});

const isDeleteSkuConfirmed = computed(
  () =>
    Boolean(deleteSkuDialog.value.skuInfo?.sku) &&
    deleteSkuDialog.value.confirmSku === deleteSkuDialog.value.skuInfo.sku,
);

const columnSettingDialog = ref({
  visible: false,
  selectedKeys: [] as string[],
});

const popupColumnSettingDialog = () => {
  columnSettingDialog.value.selectedKeys = withRequiredColKeys(visibleColKeys.value);
  columnSettingDialog.value.visible = true;
};

const onSelectAllCols = () => {
  columnSettingDialog.value.selectedKeys = allColumnDefs.map((c) => c.colKey);
};

const onClearAllCols = () => {
  // 必显列保留
  columnSettingDialog.value.selectedKeys = withRequiredColKeys([]);
};

const onResetCols = () => {
  columnSettingDialog.value.selectedKeys = withRequiredColKeys(DEFAULT_VISIBLE_COL_KEYS);
};

const onConfirmColumnSetting = () => {
  visibleColKeys.value = withRequiredColKeys(columnSettingDialog.value.selectedKeys);
  try {
    localStorage.setItem(COL_VISIBILITY_STORAGE_KEY, JSON.stringify(visibleColKeys.value));
  } catch (e) {
    console.warn('save visible cols failed', e);
  }
  columnSettingDialog.value.visible = false;
};

onMounted(() => {
  onSearchSku();
  loadSkuInfo();
});
const sortTableChange: TableProps['onSortChange'] = (val) => {
  sortTable.value = val;
  onSearchSku();
};
const onPaginationChange = ({ current, pageSize }: { current: number; pageSize: number }) => {
  paginationCurrentPage.value = current;
  paginationPageSize.value = pageSize;
  onSearchSku();
};
const calcAvgSellQuantityPkg = (row: any) => {
  if (row.sku_unit_quantity === null || row.sku_unit_quantity === undefined || row.sku_unit_quantity <= 0) {
    return row.avg_sell_quantity.toFixed(1);
  }
  const res = row.avg_sell_quantity / row.sku_unit_quantity;
  if (!row.sku_unit_name || !row.sku_unit_name.trim() || row.sku_unit_name.toLowerCase().includes('pcs')) {
    return `${res.toFixed(0)}`;
  }
  return `${res.toFixed(1)} ${row.sku_unit_name.substring(0, 1)}`;
};
const calcInventoryPkg = (row: any) => {
  if (row.sku_unit_quantity === null || row.sku_unit_quantity === undefined || row.sku_unit_quantity <= 0) {
    return row.inventory.toFixed(1);
  }
  const res = row.inventory / row.sku_unit_quantity;
  if (!row.sku_unit_name || !row.sku_unit_name.trim() || row.sku_unit_name.toLowerCase().includes('pcs')) {
    return `${res.toFixed(0)}`;
  }
  return `${res.toFixed(1)} ${row.sku_unit_name.substring(0, 1)}`;
};
const calcShippingStockQuantityPkg = (row: any) => {
  if (row.sku_unit_quantity === null || row.sku_unit_quantity === undefined || row.sku_unit_quantity <= 0) {
    return row.shipping_stock_quantity.toFixed(1);
  }
  const res = row.shipping_stock_quantity / row.sku_unit_quantity;
  if (!row.sku_unit_name || !row.sku_unit_name.trim() || row.sku_unit_name.toLowerCase().includes('pcs')) {
    return `${res.toFixed(0)}`;
  }
  return `${res.toFixed(1)} ${row.sku_unit_name.substring(0, 1)}`;
};
const calcShippingSupportDays = (row: any) => {
  if (row.shipping_stock_quantity === 0) {
    return '0';
  }
  if (row.avg_sell_quantity === 0) {
    return '--';
  }
  const supportDays = row.shipping_stock_quantity / row.avg_sell_quantity;
  return supportDays.toFixed(1);
};
const onSaveSku = async (sku: any) => {
  try {
    await saveSku(sku);
    await MessagePlugin.success('更新sku成功。');
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`更新sku异常: ${e}`);
  }
};
const onAddSku = async () => {
  try {
    const {
      success_count: successCount,
      ignore_count: ignoreCount,
      fail_count: failCount,
      detail,
    } = await addSku({
      skus: addSkuDialog.value.skus,
    });
    console.log('onAddSku response', detail);
    await MessagePlugin.success(`成功添加：${successCount}, 失败：${failCount}， 忽略： ${ignoreCount}`);
    onSearchSku();
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`添加sku异常: ${e}`);
  }
};
const popupAddSkuDialog = () => {
  addSkuDialog.value.visible = true;
};
const popupDeleteSkuDialog = (skuInfo: any) => {
  deleteSkuDialog.value = {
    visible: true,
    loading: false,
    confirmSku: '',
    skuInfo,
  };
};
const onDeleteSku = async () => {
  if (!isDeleteSkuConfirmed.value || deleteSkuDialog.value.loading) return;
  deleteSkuDialog.value.loading = true;
  try {
    await deleteSku({ sku: deleteSkuDialog.value.skuInfo.sku });
    deleteSkuDialog.value.visible = false;
    await MessagePlugin.success('删除SKU成功。');
    await onSearchSku();
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`删除SKU异常: ${e}`);
  } finally {
    deleteSkuDialog.value.loading = false;
  }
};
const onSyncAllSku = async () => {
  skuTableLoading.value = true;
  try {
    const { update_count: updateCount } = await syncAllSku();
    await MessagePlugin.success(`成功同步${updateCount}个sku`);
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询sku异常: ${e}`);
  }
  skuTableLoading.value = false;
};
const onSearchSku = async () => {
  const req = {
    sku_group: queryParam.value.skuGroup,
    sku_name: queryParam.value.skuName,
    sku: queryParam.value.sku,
    inventory_support_days: queryParam.value.supportDays,
    current_page: paginationCurrentPage.value,
    page_size: paginationPageSize.value,
    sort: sortTable.value,
  };
  skuTableLoading.value = true;
  try {
    const res = await searchSku(req);
    paginationTotalCount.value = res.total;
    skuTableData.value = res.list;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询sku异常: ${e}`);
  }
  skuTableLoading.value = false;
};
</script>

<style lang="less" scoped>
.delete-sku-info {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 20px;
}

.delete-sku-detail {
  display: grid;
  gap: 8px;
  min-width: 0;
  line-height: 1.5;

  span {
    color: var(--td-text-color-secondary);
  }
}

.delete-sku-confirm-form {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.delete-sku-confirm-label {
  line-height: 1.5;
  word-break: break-all;
  color: var(--td-text-color-primary);

  code {
    padding: 0 4px;
    color: var(--td-error-color);
    background: var(--td-error-color-1);
    border-radius: 3px;
  }
}
</style>
