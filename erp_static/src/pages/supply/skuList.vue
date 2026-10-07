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
                <t-button theme="default" :loading="exportLoading" @click="onExportSku">导出</t-button>
                <t-button theme="default" :loading="importParsing" @click="onChooseImportFile">导入</t-button>
                <input
                  ref="importFileInputRef"
                  class="import-file-input"
                  type="file"
                  accept=".xlsx"
                  @change="onImportFileChange"
                />
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
    <t-dialog
      v-model:visible="importDialogVisible"
      header="导入商品SKU预览"
      :cancel-btn="null"
      :close-btn="importPhase !== 'running'"
      :close-on-esc-keydown="false"
      :close-on-overlay-click="false"
      :confirm-btn="null"
      show-overlay
      width="92%"
    >
      <div class="import-summary">{{ importCountryHint }}</div>
      <div class="import-summary">
        本次导入：新增 {{ importPreview.created.length }} 条，覆盖 {{ importPreview.overwritten.length }} 条，无变化
        {{ importPreview.unchangedCount }} 条。
      </div>
      <div v-if="importPreview.errors.length" class="import-warning">
        有 {{ importPreview.errors.length }} 行校验失败，确认导入后将跳过这些行。
      </div>
      <div v-if="importPhase !== 'idle'" class="import-summary">
        已处理 {{ importFinishedCount }} / {{ importActionCount }}
      </div>
      <t-tabs :value="importPreviewTab" @change="onImportPreviewTabChange">
        <t-tab-panel value="created" :label="`新增 (${importPreview.created.length})`">
          <t-table
            :columns="importCreatedColumns"
            :data="importPreview.created"
            row-key="rowIndex"
            bordered
            hover
            size="small"
            max-height="420"
          >
            <template #import_status="{ row }">
              <span :class="importStatusClass(row.importStatus)">{{ importStatusLabel(row) }}</span>
            </template>
            <template #sync_status="{ row }">
              <span :class="importStatusClass(row.syncStatus)">{{ syncStatusLabel(row) }}</span>
            </template>
          </t-table>
        </t-tab-panel>
        <t-tab-panel value="overwritten" :label="`覆盖 (${importPreview.overwritten.length})`">
          <t-table
            :columns="importOverwriteColumns"
            :data="importPreview.overwritten"
            row-key="rowIndex"
            bordered
            hover
            size="small"
            max-height="420"
          >
            <template #sku_group="{ row }">
              <span :class="{ 'import-field-changed': isImportFieldChanged(row, 'sku_group') }">
                {{ importFieldText(row, 'sku_group') }}
              </span>
            </template>
            <template #sku_name="{ row }">
              <span :class="{ 'import-field-changed': isImportFieldChanged(row, 'sku_name') }">
                {{ importFieldText(row, 'sku_name') }}
              </span>
            </template>
            <template #sku_unit_name="{ row }">
              <span :class="{ 'import-field-changed': isImportFieldChanged(row, 'sku_unit_name') }">
                {{ importFieldText(row, 'sku_unit_name') }}
              </span>
            </template>
            <template #sku_unit_quantity="{ row }">
              <span :class="{ 'import-field-changed': isImportFieldChanged(row, 'sku_unit_quantity') }">
                {{ importFieldText(row, 'sku_unit_quantity') }}
              </span>
            </template>
            <template #sku_pack_length="{ row }">
              <span :class="{ 'import-field-changed': isImportFieldChanged(row, 'sku_pack_length') }">
                {{ importFieldText(row, 'sku_pack_length') }}
              </span>
            </template>
            <template #sku_pack_width="{ row }">
              <span :class="{ 'import-field-changed': isImportFieldChanged(row, 'sku_pack_width') }">
                {{ importFieldText(row, 'sku_pack_width') }}
              </span>
            </template>
            <template #sku_pack_height="{ row }">
              <span :class="{ 'import-field-changed': isImportFieldChanged(row, 'sku_pack_height') }">
                {{ importFieldText(row, 'sku_pack_height') }}
              </span>
            </template>
            <template #import_status="{ row }">
              <span :class="importStatusClass(row.importStatus)">{{ importStatusLabel(row) }}</span>
            </template>
            <template #sync_status="{ row }">
              <span :class="importStatusClass(row.syncStatus)">{{ syncStatusLabel(row) }}</span>
            </template>
          </t-table>
        </t-tab-panel>
        <t-tab-panel value="errors" :label="`校验失败 (${importPreview.errors.length})`">
          <t-table
            :columns="importErrorColumns"
            :data="importPreview.errors"
            row-key="rowIndex"
            bordered
            hover
            size="small"
            max-height="420"
          />
        </t-tab-panel>
      </t-tabs>
      <div class="import-hint">确认后才会写入当前国家。新增 SKU 若当前国 ERP 没有该编码，会标同步失败且不入库。</div>
      <t-row class="import-actions">
        <t-col :span="8"></t-col>
        <t-col :span="4">
          <t-space style="float: right">
            <t-button v-if="importPhase === 'idle'" theme="default" @click="importDialogVisible = false">取消</t-button>
            <t-button
              v-if="importPhase === 'idle'"
              theme="primary"
              :disabled="!canConfirmImport"
              @click="onConfirmImport"
            >
              确认导入
            </t-button>
            <t-button v-if="importPhase === 'running'" theme="primary" loading>导入中</t-button>
            <t-button v-if="importPhase === 'done'" theme="primary" @click="importDialogVisible = false">关闭</t-button>
          </t-space>
        </t-col>
      </t-row>
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
import {
  saveSku,
  searchSku,
  syncAllSku,
  addSku,
  deleteSku,
  checkSkuInErp,
  importSkuManualFields,
  syncSku,
} from '@/apis/supplierApis';
import { getLoginUserInfo } from '@/apis/sysApis';
import { getProjectLabel } from '@/constants/project';
import {
  skuGroupNameOptions,
  loadSkuInfo,
  reloadSkuInfo,
  calcPackVolumeM3PerUnit,
  formatVolumeM3,
  calcAvgSellQuantityPkg,
  calcInventoryPkg,
  calcShippingStockQuantityPkg,
  calcShippingSupportDays,
} from '@/utils/skuUtil';
import {
  SKU_IMPORT_INTERVAL_MS,
  buildSkuImportPreview,
  exportSkuExcel,
  getSkuImportFieldDiff,
  parseSkuExcelSourceCountry,
  skuImportStatusText,
  toSkuManualFieldsPayload,
} from '@/utils/skuExcel';
import type {
  ISkuImportPreview,
  ISkuImportOverwriteItem,
  SkuImportOpStatus,
  SkuManualFieldKey,
} from '@/utils/skuExcel';

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

const exportLoading = ref(false);
const importParsing = ref(false);
const importDialogVisible = ref(false);
const importPhase = ref<'idle' | 'running' | 'done'>('idle');
const importPreviewTab = ref('created');
const importSourceCountry = ref('');
const currentCountryName = ref('');
const importFileInputRef = ref<HTMLInputElement | null>(null);
const emptyImportPreview = (): ISkuImportPreview => ({
  created: [],
  overwritten: [],
  unchangedCount: 0,
  errors: [],
});
const importPreview = ref<ISkuImportPreview>(emptyImportPreview());
const importCreatedColumns = [
  { colKey: 'rowIndex', title: '行号', width: 70 },
  { colKey: 'sku', title: '商品SKU', width: 160 },
  { colKey: 'sku_group', title: 'sku分组', width: 120 },
  { colKey: 'sku_name', title: '商品名', width: 140 },
  { colKey: 'sku_unit_name', title: '采购单位', width: 100 },
  { colKey: 'sku_unit_quantity', title: '单位的SKU数', width: 120 },
  { colKey: 'sku_pack_length', title: '打包长(cm)', width: 110 },
  { colKey: 'sku_pack_width', title: '打包宽(cm)', width: 110 },
  { colKey: 'sku_pack_height', title: '打包高(cm)', width: 110 },
  { colKey: 'import_status', title: '导入状态', width: 160 },
  { colKey: 'sync_status', title: '同步状态', width: 180 },
];
const importOverwriteColumns = [
  { colKey: 'rowIndex', title: '行号', width: 70 },
  { colKey: 'sku', title: '商品SKU', width: 160 },
  { colKey: 'sku_group', title: 'sku分组', width: 160 },
  { colKey: 'sku_name', title: '商品名', width: 160 },
  { colKey: 'sku_unit_name', title: '采购单位', width: 140 },
  { colKey: 'sku_unit_quantity', title: '单位的SKU数', width: 140 },
  { colKey: 'sku_pack_length', title: '打包长(cm)', width: 130 },
  { colKey: 'sku_pack_width', title: '打包宽(cm)', width: 130 },
  { colKey: 'sku_pack_height', title: '打包高(cm)', width: 130 },
  { colKey: 'import_status', title: '导入状态', width: 160 },
  { colKey: 'sync_status', title: '同步状态', width: 180 },
];
const importErrorColumns = [
  { colKey: 'rowIndex', title: '行号', width: 80 },
  { colKey: 'sku', title: '商品SKU', width: 180 },
  { colKey: 'message', title: '原因' },
];
const canConfirmImport = computed(
  () => importPreview.value.created.length + importPreview.value.overwritten.length > 0,
);
const importActionCount = computed(() => importPreview.value.created.length + importPreview.value.overwritten.length);
const isImportRowSettled = (row: { importStatus: SkuImportOpStatus; syncStatus: SkuImportOpStatus }) => {
  const importDone = row.importStatus === 'success' || row.importStatus === 'fail' || row.importStatus === 'skipped';
  const syncDone = row.syncStatus === 'success' || row.syncStatus === 'fail' || row.syncStatus === 'skipped';
  return importDone && syncDone;
};
const importFinishedCount = computed(() => {
  const rows = [...importPreview.value.created, ...importPreview.value.overwritten];
  return rows.filter((row) => isImportRowSettled(row)).length;
});
const importCountryHint = computed(() => {
  const current = currentCountryName.value || '当前国家';
  const source = importSourceCountry.value;
  if (source && source !== current) {
    return `文件来自 ${source}，将写入 ${current}`;
  }
  return `将写入 ${current}`;
});
const fetchAllSkus = async (currentPage = 1, collected: any[] = []): Promise<any[]> => {
  const pageSize = 1000;
  const res = await searchSku({
    current_page: currentPage,
    page_size: pageSize,
  });
  const list = res.list || [];
  const total = res.total || 0;
  const merged = collected.concat(list);
  if (list.length === 0 || merged.length >= total) {
    return merged;
  }
  return fetchAllSkus(currentPage + 1, merged);
};
const readFileAsArrayBuffer = (file: File) => {
  return new Promise<ArrayBuffer>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result as ArrayBuffer);
    };
    reader.onerror = () => {
      reject(reader.error || new Error('读取文件失败'));
    };
    reader.readAsArrayBuffer(file);
  });
};
const resolveCountryName = async () => {
  const userInfo = await getLoginUserInfo();
  const projectId = (userInfo as any)?.project_id || '';
  return getProjectLabel(projectId) || projectId || '未知国家';
};
const apiErrorMessage = (error: unknown) => {
  if (error && typeof error === 'object' && 'resultMsg' in error) {
    const message = String((error as { resultMsg?: string }).resultMsg || '').trim();
    if (message) {
      return message;
    }
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return '请求失败';
};
const sleep = (ms: number) =>
  new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
const importStatusClass = (status: SkuImportOpStatus) => {
  if (status === 'success') return 'import-status-success';
  if (status === 'fail') return 'import-status-fail';
  if (status === 'skipped') return 'import-status-skipped';
  return '';
};
const importStatusLabel = (row: { importStatus: SkuImportOpStatus; importMessage: string }) => {
  if (row.importStatus === 'pending') return '待导入';
  if (row.importStatus === 'running') return '导入中';
  return skuImportStatusText(row.importStatus, row.importMessage, '导入成功', '导入失败');
};
const syncStatusLabel = (row: { syncStatus: SkuImportOpStatus; syncMessage: string }) => {
  if (row.syncStatus === 'pending') return '待同步';
  if (row.syncStatus === 'running') return '同步中';
  return skuImportStatusText(row.syncStatus, row.syncMessage, '同步成功', '同步失败');
};
const onImportPreviewTabChange = (value: string) => {
  importPreviewTab.value = value;
};
const importFieldText = (row: ISkuImportOverwriteItem, key: SkuManualFieldKey) => {
  const diff = getSkuImportFieldDiff(row, key);
  if (!diff) return '';
  return `${diff.oldValue} → ${diff.newValue}`;
};
const isImportFieldChanged = (row: ISkuImportOverwriteItem, key: SkuManualFieldKey) => {
  const diff = getSkuImportFieldDiff(row, key);
  return Boolean(diff && diff.changed);
};
const onExportSku = async () => {
  exportLoading.value = true;
  try {
    const [skus, countryName] = await Promise.all([fetchAllSkus(), resolveCountryName()]);
    exportSkuExcel(skus, `${countryName}_商品sku.xlsx`);
    MessagePlugin.success(`已导出 ${skus.length} 条商品SKU`);
  } catch (e) {
    console.error(e);
    MessagePlugin.error(`导出商品SKU失败: ${e}`);
  } finally {
    exportLoading.value = false;
  }
};
const onChooseImportFile = () => {
  importFileInputRef.value?.click();
};
const onImportFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files && input.files.length > 0 ? input.files[0] : null;
  input.value = '';
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.xlsx')) {
    MessagePlugin.error('请选择 xlsx 文件');
    return;
  }
  importParsing.value = true;
  try {
    const [fileBuffer, skus, countryName] = await Promise.all([
      readFileAsArrayBuffer(file),
      fetchAllSkus(),
      resolveCountryName(),
    ]);
    currentCountryName.value = countryName;
    importSourceCountry.value = parseSkuExcelSourceCountry(file.name);
    importPreview.value = buildSkuImportPreview(fileBuffer, skus);
    importPhase.value = 'idle';
    if (importPreview.value.created.length > 0) {
      importPreviewTab.value = 'created';
    } else if (importPreview.value.overwritten.length > 0) {
      importPreviewTab.value = 'overwritten';
    } else {
      importPreviewTab.value = 'errors';
    }
    importDialogVisible.value = true;
  } catch (e) {
    console.error(e);
    MessagePlugin.error(`解析商品SKU文件失败: ${e}`);
  } finally {
    importParsing.value = false;
  }
};
const onConfirmImport = async () => {
  if (!canConfirmImport.value || importPhase.value !== 'idle') return;
  const actions = [
    ...importPreview.value.created.map((item) => ({ kind: 'created' as const, item })),
    ...importPreview.value.overwritten.map((item) => ({ kind: 'overwrite' as const, item })),
  ].sort((left, right) => left.item.rowIndex - right.item.rowIndex);
  importPhase.value = 'running';
  const importOne = async (action: (typeof actions)[number]) => {
    const fields = action.kind === 'created' ? action.item : action.item.row;
    if (action.kind === 'created') {
      action.item.syncStatus = 'running';
      try {
        await checkSkuInErp({ sku: fields.sku });
        action.item.syncStatus = 'pending';
        action.item.syncMessage = '';
      } catch (error) {
        action.item.syncStatus = 'fail';
        action.item.syncMessage = apiErrorMessage(error);
        action.item.importStatus = 'skipped';
        action.item.importMessage = '未导入';
        return;
      }
    }
    action.item.importStatus = 'running';
    try {
      await importSkuManualFields(toSkuManualFieldsPayload(fields));
      action.item.importStatus = 'success';
      action.item.importMessage = '';
    } catch (error) {
      action.item.importStatus = 'fail';
      action.item.importMessage = apiErrorMessage(error);
      action.item.syncStatus = 'skipped';
      action.item.syncMessage = '未同步';
      return;
    }
    action.item.syncStatus = 'running';
    try {
      await syncSku({ sku: fields.sku });
      action.item.syncStatus = 'success';
      action.item.syncMessage = '';
    } catch (error) {
      action.item.syncStatus = 'fail';
      action.item.syncMessage = apiErrorMessage(error);
    }
  };
  try {
    for (let index = 0; index < actions.length; index += 1) {
      if (index > 0) {
        // 串行间隔，避免连续打 ERP
        // eslint-disable-next-line no-await-in-loop
        await sleep(SKU_IMPORT_INTERVAL_MS);
      }
      // 必须逐条执行，才能在对话框里实时标出导入和同步结果
      // eslint-disable-next-line no-await-in-loop
      await importOne(actions[index]);
    }
    await onSearchSku();
    await reloadSkuInfo();
  } finally {
    importPhase.value = 'done';
  }
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

.import-file-input {
  display: none;
}

.import-summary {
  margin-bottom: 12px;
  line-height: 22px;
}

.import-warning {
  margin-bottom: 12px;
  color: var(--td-warning-color);
}

.import-hint {
  margin-top: 12px;
  color: var(--td-text-color-secondary);
}

.import-actions {
  margin-top: 16px;
}

.import-field-changed {
  color: var(--td-error-color);
  font-weight: 600;
}

.import-status-success {
  color: var(--td-success-color);
}

.import-status-fail {
  color: var(--td-error-color);
}

.import-status-skipped {
  color: var(--td-warning-color);
}
</style>
