/* eslint-disable camelcase */
import { read, utils, writeFile } from 'xlsx';
import {
  calcAvgSellQuantityPkg,
  calcInventoryPkg,
  calcPackVolumeM3PerUnit,
  calcShippingStockQuantityPkg,
  calcShippingSupportDays,
  formatAvgSellQuantity,
  formatVolumeM3,
} from '@/utils/skuUtil';

export const SKU_EXCEL_SHEET_NAME = '商品SKU';
export const SKU_EXCEL_FILE_SUFFIX = '_商品sku.xlsx';
export const SKU_IMPORT_INTERVAL_MS = 300;

export const SKU_EXPORT_COLUMNS = [
  'sku分组',
  '商品名',
  '商品SKU',
  'BigSeller商品名',
  '采购单位',
  '单位的SKU数',
  '打包长(cm)',
  '打包宽(cm)',
  '打包高(cm)',
  '打包体积(m³)',
  '库存-SKU',
  '库存-采购单位',
  '平均日销-SKU',
  '平均日销-采购单位',
  '库存支撑天数',
  '海运中-SKU',
  '海运中-采购单位',
  '海运中-支撑天数',
] as const;

export const SKU_IMPORT_COLUMNS = [
  '商品SKU',
  'sku分组',
  '商品名',
  '采购单位',
  '单位的SKU数',
  '打包长(cm)',
  '打包宽(cm)',
  '打包高(cm)',
] as const;

export type SkuManualFieldKey =
  | 'sku_group'
  | 'sku_name'
  | 'sku_unit_name'
  | 'sku_unit_quantity'
  | 'sku_pack_length'
  | 'sku_pack_width'
  | 'sku_pack_height';

export type SkuImportOpStatus = 'pending' | 'running' | 'success' | 'fail' | 'skipped';

export interface ISkuImportManualFields {
  sku: string;
  sku_group: string;
  sku_name: string;
  sku_unit_name: string;
  sku_unit_quantity: number;
  sku_pack_length: number;
  sku_pack_width: number;
  sku_pack_height: number;
}

export interface ISkuImportStatus {
  importStatus: SkuImportOpStatus;
  importMessage: string;
  syncStatus: SkuImportOpStatus;
  syncMessage: string;
}

export interface ISkuImportCreatedItem extends ISkuImportManualFields, ISkuImportStatus {
  rowIndex: number;
}

export interface ISkuImportFieldDiff {
  key: SkuManualFieldKey;
  label: string;
  oldValue: string;
  newValue: string;
  changed: boolean;
}

export interface ISkuImportOverwriteItem extends ISkuImportStatus {
  rowIndex: number;
  sku: string;
  diffs: ISkuImportFieldDiff[];
  row: ISkuImportManualFields;
}

export interface ISkuImportError {
  rowIndex: number;
  sku: string;
  message: string;
}

export interface ISkuImportPreview {
  created: ISkuImportCreatedItem[];
  overwritten: ISkuImportOverwriteItem[];
  unchangedCount: number;
  errors: ISkuImportError[];
}

interface IParsedCandidate {
  rowIndex: number;
  sku: string;
  messages: string[];
  row: ISkuImportManualFields | null;
}

const COMPARE_FIELDS: Array<{ key: SkuManualFieldKey; label: string }> = [
  { key: 'sku_group', label: 'sku分组' },
  { key: 'sku_name', label: '商品名' },
  { key: 'sku_unit_name', label: '采购单位' },
  { key: 'sku_unit_quantity', label: '单位的SKU数' },
  { key: 'sku_pack_length', label: '打包长(cm)' },
  { key: 'sku_pack_width', label: '打包宽(cm)' },
  { key: 'sku_pack_height', label: '打包高(cm)' },
];

function pendingStatus(): ISkuImportStatus {
  return {
    importStatus: 'pending',
    importMessage: '',
    syncStatus: 'pending',
    syncMessage: '',
  };
}

function normalizeHeader(value: unknown): string {
  return String(value ?? '')
    .replace(/^\uFEFF/, '')
    .trim();
}

function toFiniteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === '') {
    return null;
  }
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null;
  }
  if (typeof value === 'string') {
    const text = value.trim();
    if (text === '') {
      return null;
    }
    const parsed = Number(text);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function toNonNegativeInt(value: unknown, emptyAsZero: boolean): number | null {
  if (value === null || value === undefined || String(value).trim() === '') {
    return emptyAsZero ? 0 : null;
  }
  const parsed = toFiniteNumber(value);
  if (parsed === null || !Number.isInteger(parsed) || parsed < 0) {
    return null;
  }
  return parsed;
}

function readCell(row: unknown[], columnIndex: Map<string, number>, column: string): unknown {
  const index = columnIndex.get(column);
  if (index === undefined) {
    return '';
  }
  return row[index];
}

function isBlankRow(row: unknown[], columnIndex: Map<string, number>): boolean {
  return SKU_IMPORT_COLUMNS.every((column) => String(readCell(row, columnIndex, column) ?? '').trim() === '');
}

function validateCandidate(rowIndex: number, cells: unknown[], columnIndex: Map<string, number>): IParsedCandidate {
  const sku = String(readCell(cells, columnIndex, '商品SKU') ?? '').trim();
  const skuGroup = String(readCell(cells, columnIndex, 'sku分组') ?? '').trim();
  const skuName = String(readCell(cells, columnIndex, '商品名') ?? '').trim();
  const skuUnitName = String(readCell(cells, columnIndex, '采购单位') ?? '').trim();
  const unitQuantityRaw = readCell(cells, columnIndex, '单位的SKU数');
  const unitQuantity = toNonNegativeInt(unitQuantityRaw, false);
  const packLength = toNonNegativeInt(readCell(cells, columnIndex, '打包长(cm)'), true);
  const packWidth = toNonNegativeInt(readCell(cells, columnIndex, '打包宽(cm)'), true);
  const packHeight = toNonNegativeInt(readCell(cells, columnIndex, '打包高(cm)'), true);
  const messages: string[] = [];

  if (!sku) {
    messages.push('商品SKU不能为空');
  }
  if (!columnIndex.has('sku分组') || !skuGroup) {
    messages.push('sku分组不能为空');
  }
  if (!columnIndex.has('商品名') || !skuName) {
    messages.push('商品名不能为空');
  }
  if (!columnIndex.has('采购单位') || !skuUnitName) {
    messages.push('采购单位不能为空');
  }
  if (!columnIndex.has('单位的SKU数') || unitQuantity === null || unitQuantity <= 0) {
    messages.push('单位的SKU数必须是正整数');
  }
  if (packLength === null) {
    messages.push('打包长(cm)必须是非负整数');
  }
  if (packWidth === null) {
    messages.push('打包宽(cm)必须是非负整数');
  }
  if (packHeight === null) {
    messages.push('打包高(cm)必须是非负整数');
  }

  if (
    messages.length > 0 ||
    unitQuantity === null ||
    packLength === null ||
    packWidth === null ||
    packHeight === null
  ) {
    return {
      rowIndex,
      sku,
      messages,
      row: null,
    };
  }

  return {
    rowIndex,
    sku,
    messages,
    row: {
      sku,
      sku_group: skuGroup,
      sku_name: skuName,
      sku_unit_name: skuUnitName,
      sku_unit_quantity: unitQuantity,
      sku_pack_length: packLength,
      sku_pack_width: packWidth,
      sku_pack_height: packHeight,
    },
  };
}

function parseSheetRows(fileBuffer: ArrayBuffer): IParsedCandidate[] | ISkuImportError[] {
  const workbook = read(fileBuffer, { type: 'array' });
  const sheetName = workbook.SheetNames[0];
  if (!sheetName) {
    return [{ rowIndex: 1, sku: '', message: '文件没有工作表' }];
  }
  const matrix = utils.sheet_to_json<unknown[]>(workbook.Sheets[sheetName], {
    header: 1,
    defval: '',
    raw: true,
  });
  const header = (matrix[0] || []).map((cell) => normalizeHeader(cell));
  const columnIndex = new Map<string, number>();
  header.forEach((name, index) => {
    if (name && !columnIndex.has(name)) {
      columnIndex.set(name, index);
    }
  });
  if (!columnIndex.has('商品SKU')) {
    return [{ rowIndex: 1, sku: '', message: '缺少列：商品SKU' }];
  }

  const candidates: IParsedCandidate[] = [];
  matrix.forEach((cells, index) => {
    if (index === 0 || isBlankRow(cells || [], columnIndex)) {
      return;
    }
    candidates.push(validateCandidate(index + 1, cells || [], columnIndex));
  });
  if (candidates.length === 0) {
    return [{ rowIndex: 1, sku: '', message: '文件中没有可导入的数据' }];
  }
  return candidates;
}

function isErrorList(rows: IParsedCandidate[] | ISkuImportError[]): rows is ISkuImportError[] {
  return rows.length === 0 || !('messages' in rows[0]);
}

function formatFieldValue(key: SkuManualFieldKey, row: ISkuImportManualFields): string {
  const value = row[key];
  return value === null || value === undefined ? '' : String(value);
}

function isFieldChanged(
  key: SkuManualFieldKey,
  current: ISkuImportManualFields,
  incoming: ISkuImportManualFields,
): boolean {
  return formatFieldValue(key, current) !== formatFieldValue(key, incoming);
}

function buildDiffs(current: ISkuImportManualFields, incoming: ISkuImportManualFields): ISkuImportFieldDiff[] {
  return COMPARE_FIELDS.map((field) => ({
    key: field.key,
    label: field.label,
    oldValue: formatFieldValue(field.key, current),
    newValue: formatFieldValue(field.key, incoming),
    changed: isFieldChanged(field.key, current, incoming),
  }));
}

function normalizeExisting(note: any): ISkuImportManualFields {
  return {
    sku: String(note?.sku ?? '').trim(),
    sku_group: String(note?.sku_group ?? '').trim(),
    sku_name: String(note?.sku_name ?? '').trim(),
    sku_unit_name: String(note?.sku_unit_name ?? '').trim(),
    sku_unit_quantity: Number(note?.sku_unit_quantity) || 0,
    sku_pack_length: Number(note?.sku_pack_length) || 0,
    sku_pack_width: Number(note?.sku_pack_width) || 0,
    sku_pack_height: Number(note?.sku_pack_height) || 0,
  };
}

export function buildSkuImportPreview(fileBuffer: ArrayBuffer, existingSkus: any[]): ISkuImportPreview {
  const parsed = parseSheetRows(fileBuffer);
  if (isErrorList(parsed)) {
    return {
      created: [],
      overwritten: [],
      unchangedCount: 0,
      errors: parsed,
    };
  }

  const firstRowIndex = new Map<string, number>();
  parsed.forEach((candidate) => {
    if (!candidate.sku || firstRowIndex.has(candidate.sku)) {
      return;
    }
    firstRowIndex.set(candidate.sku, candidate.rowIndex);
  });

  const existingMap = new Map<string, ISkuImportManualFields>();
  existingSkus.forEach((item) => {
    const normalized = normalizeExisting(item);
    if (normalized.sku) {
      existingMap.set(normalized.sku, normalized);
    }
  });

  const created: ISkuImportCreatedItem[] = [];
  const overwritten: ISkuImportOverwriteItem[] = [];
  const errors: ISkuImportError[] = [];
  let unchangedCount = 0;

  parsed.forEach((candidate) => {
    const messages = candidate.messages.slice();
    const firstIndex = firstRowIndex.get(candidate.sku);
    if (candidate.sku && firstIndex !== undefined && candidate.rowIndex !== firstIndex) {
      messages.push('SKU重复');
    }
    if (messages.length > 0 || !candidate.row) {
      errors.push({
        rowIndex: candidate.rowIndex,
        sku: candidate.sku,
        message: messages.join('；'),
      });
      return;
    }

    const current = existingMap.get(candidate.sku);
    if (!current) {
      created.push({
        rowIndex: candidate.rowIndex,
        ...candidate.row,
        ...pendingStatus(),
      });
      return;
    }
    const diffs = buildDiffs(current, candidate.row);
    if (diffs.some((diff) => diff.changed)) {
      overwritten.push({
        rowIndex: candidate.rowIndex,
        sku: candidate.sku,
        diffs,
        row: candidate.row,
        ...pendingStatus(),
      });
      return;
    }
    unchangedCount += 1;
  });

  return {
    created,
    overwritten,
    unchangedCount,
    errors,
  };
}

export function getSkuImportFieldDiff(
  item: ISkuImportOverwriteItem,
  key: SkuManualFieldKey,
): ISkuImportFieldDiff | undefined {
  return item.diffs.find((diff) => diff.key === key);
}

export function parseSkuExcelSourceCountry(fileName: string): string {
  const normalized = fileName.trim();
  if (!normalized.toLowerCase().endsWith(SKU_EXCEL_FILE_SUFFIX)) {
    return '';
  }
  return normalized.slice(0, normalized.length - SKU_EXCEL_FILE_SUFFIX.length);
}

export function skuImportStatusText(status: SkuImportOpStatus, message: string, successText: string, failText: string) {
  if (status === 'pending') {
    return '待处理';
  }
  if (status === 'running') {
    return '处理中';
  }
  if (status === 'success') {
    return successText;
  }
  if (status === 'skipped') {
    return message || '未执行';
  }
  return message ? `${failText}：${message}` : failText;
}

function exportCell(row: any, column: (typeof SKU_EXPORT_COLUMNS)[number]): string | number {
  if (column === 'sku分组') return row.sku_group || '';
  if (column === '商品名') return row.sku_name || '';
  if (column === '商品SKU') return row.sku || '';
  if (column === 'BigSeller商品名') return row.erp_sku_name || '';
  if (column === '采购单位') return row.sku_unit_name || '';
  if (column === '单位的SKU数') return Number(row.sku_unit_quantity) || 0;
  if (column === '打包长(cm)') return Number(row.sku_pack_length) || 0;
  if (column === '打包宽(cm)') return Number(row.sku_pack_width) || 0;
  if (column === '打包高(cm)') return Number(row.sku_pack_height) || 0;
  if (column === '打包体积(m³)') {
    return formatVolumeM3(calcPackVolumeM3PerUnit(row.sku_pack_length, row.sku_pack_width, row.sku_pack_height));
  }
  if (column === '库存-SKU') return Number(row.inventory) || 0;
  if (column === '库存-采购单位') return calcInventoryPkg(row);
  if (column === '平均日销-SKU') return formatAvgSellQuantity(row.avg_sell_quantity);
  if (column === '平均日销-采购单位') return calcAvgSellQuantityPkg(row);
  if (column === '库存支撑天数') return Number(row.inventory_support_days) || 0;
  if (column === '海运中-SKU') return Number(row.shipping_stock_quantity) || 0;
  if (column === '海运中-采购单位') return calcShippingStockQuantityPkg(row);
  return calcShippingSupportDays(row);
}

export function exportSkuExcel(skus: any[], fileName: string) {
  const header = [...SKU_EXPORT_COLUMNS];
  const body = skus.map((sku) => header.map((column) => exportCell(sku, column)));
  const sheet = utils.aoa_to_sheet([header, ...body]);
  const skuColumnIndex = header.indexOf('商品SKU');
  const sheetRef = sheet['!ref'];
  if (sheetRef && skuColumnIndex >= 0) {
    const range = utils.decode_range(sheetRef);
    for (let rowIndex = 1; rowIndex <= range.e.r; rowIndex += 1) {
      const address = utils.encode_cell({ r: rowIndex, c: skuColumnIndex });
      const cell = sheet[address];
      if (cell) {
        cell.t = 's';
        cell.v = String(cell.v ?? '');
        cell.z = '@';
      }
    }
  }
  const workbook = utils.book_new();
  utils.book_append_sheet(workbook, sheet, SKU_EXCEL_SHEET_NAME);
  const downloadName = fileName.toLowerCase().endsWith('.xlsx') ? fileName : `${fileName}.xlsx`;
  writeFile(workbook, downloadName);
}

export function toSkuManualFieldsPayload(row: ISkuImportManualFields) {
  return {
    sku: row.sku,
    sku_group: row.sku_group,
    sku_name: row.sku_name,
    sku_unit_name: row.sku_unit_name,
    sku_unit_quantity: row.sku_unit_quantity,
    sku_pack_length: row.sku_pack_length,
    sku_pack_width: row.sku_pack_width,
    sku_pack_height: row.sku_pack_height,
  };
}
