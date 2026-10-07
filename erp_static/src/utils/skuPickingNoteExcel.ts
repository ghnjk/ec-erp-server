/* eslint-disable camelcase */
import { read, utils, writeFile } from 'xlsx';

export const PICKING_NOTE_SHEET_NAME = '拣货备注';
export const PICKING_NOTE_IMPORT_BATCH_SIZE = 200;
const MIN_PICKING_UNIT = 0.01;
const NUMBER_SCALE = 10000;

export const PICKING_NOTE_COLUMNS = [
  'sku',
  '1拣货单位=多少sku?',
  '拣货单位名',
  '拣货SKU名',
  '是否支持PKG打包',
  '1 PKG=多少SKU',
  'PKG打包单位名',
] as const;

export type PickingNoteColumn = (typeof PICKING_NOTE_COLUMNS)[number];

export interface IPickingNoteImportRow {
  sku: string;
  picking_unit: number;
  picking_unit_name: string;
  picking_sku_name: string;
  support_pkg_picking: boolean;
  pkg_picking_unit: number;
  pkg_picking_unit_name: string;
}

export interface IPickingNoteCreatedItem extends IPickingNoteImportRow {
  rowIndex: number;
}

export interface IPickingNoteImportError {
  rowIndex: number;
  sku: string;
  message: string;
}

export type PickingNoteFieldKey =
  | 'picking_unit'
  | 'picking_unit_name'
  | 'picking_sku_name'
  | 'support_pkg_picking'
  | 'pkg_picking_unit'
  | 'pkg_picking_unit_name';

export interface IPickingNoteFieldDiff {
  key: PickingNoteFieldKey;
  label: string;
  oldValue: string;
  newValue: string;
  changed: boolean;
}

export interface IPickingNoteOverwriteItem {
  rowIndex: number;
  sku: string;
  diffs: IPickingNoteFieldDiff[];
  row: IPickingNoteImportRow;
}

export interface IPickingNoteImportPreview {
  created: IPickingNoteCreatedItem[];
  overwritten: IPickingNoteOverwriteItem[];
  unchangedCount: number;
  errors: IPickingNoteImportError[];
}

interface IPickingNoteSource {
  sku?: string | null;
  picking_unit?: number | string | null;
  picking_unit_name?: string | null;
  picking_sku_name?: string | null;
  support_pkg_picking?: boolean | number | string | null;
  pkg_picking_unit?: number | string | null;
  pkg_picking_unit_name?: string | null;
}

interface IParsedCandidate {
  rowIndex: number;
  sku: string;
  messages: string[];
  row: IPickingNoteImportRow | null;
}

const COMPARE_FIELDS: Array<{ key: PickingNoteFieldKey; label: string }> = [
  { key: 'picking_unit', label: '1拣货单位=多少sku?' },
  { key: 'picking_unit_name', label: '拣货单位名' },
  { key: 'picking_sku_name', label: '拣货SKU名' },
  { key: 'support_pkg_picking', label: '是否支持PKG打包' },
  { key: 'pkg_picking_unit', label: '1 PKG=多少SKU' },
  { key: 'pkg_picking_unit_name', label: 'PKG打包单位名' },
];

function roundPickingNumber(value: number): number {
  return Math.round(value * NUMBER_SCALE) / NUMBER_SCALE;
}

function formatNumber(value: number): string {
  if (!Number.isFinite(value)) {
    return '';
  }
  return String(roundPickingNumber(value));
}

function formatBool(value: boolean): string {
  return value ? '是' : '否';
}

function normalizeHeader(value: unknown): string {
  return String(value ?? '')
    .replace(/^\uFEFF/, '')
    .trim();
}

function normalizeBool(value: unknown): boolean {
  if (value === true || value === 1 || value === '1' || value === '是') {
    return true;
  }
  if (typeof value === 'string' && value.trim().toLowerCase() === 'true') {
    return true;
  }
  return false;
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

export function normalizePickingNoteRow(note: IPickingNoteSource): IPickingNoteImportRow {
  const pickingUnit = toFiniteNumber(note.picking_unit);
  const pkgPickingUnit = toFiniteNumber(note.pkg_picking_unit);
  return {
    sku: String(note.sku ?? '').trim(),
    picking_unit: pickingUnit === null ? 0 : pickingUnit,
    picking_unit_name: String(note.picking_unit_name ?? '').trim(),
    picking_sku_name: String(note.picking_sku_name ?? '').trim(),
    support_pkg_picking: normalizeBool(note.support_pkg_picking),
    pkg_picking_unit: pkgPickingUnit === null ? 0 : pkgPickingUnit,
    pkg_picking_unit_name: String(note.pkg_picking_unit_name ?? '').trim(),
  };
}

export function toPickingNoteSubmitItem(row: IPickingNoteImportRow) {
  return {
    sku: row.sku,
    picking_unit: row.picking_unit,
    picking_unit_name: row.picking_unit_name,
    picking_sku_name: row.picking_sku_name,
    support_pkg_picking: row.support_pkg_picking,
    pkg_picking_unit: row.pkg_picking_unit,
    pkg_picking_unit_name: row.pkg_picking_unit_name,
  };
}

function isSameNumber(left: number, right: number): boolean {
  if (!Number.isFinite(left) || !Number.isFinite(right)) {
    return false;
  }
  return roundPickingNumber(left) === roundPickingNumber(right);
}

function formatFieldValue(key: PickingNoteFieldKey, row: IPickingNoteImportRow): string {
  if (key === 'support_pkg_picking') {
    return formatBool(row.support_pkg_picking);
  }
  if (key === 'picking_unit' || key === 'pkg_picking_unit') {
    return formatNumber(row[key]);
  }
  return row[key];
}

function isFieldChanged(
  key: PickingNoteFieldKey,
  current: IPickingNoteImportRow,
  incoming: IPickingNoteImportRow,
): boolean {
  if (key === 'support_pkg_picking') {
    return current.support_pkg_picking !== incoming.support_pkg_picking;
  }
  if (key === 'picking_unit' || key === 'pkg_picking_unit') {
    return !isSameNumber(current[key], incoming[key]);
  }
  return current[key] !== incoming[key];
}

function buildDiffs(current: IPickingNoteImportRow, incoming: IPickingNoteImportRow): IPickingNoteFieldDiff[] {
  return COMPARE_FIELDS.map((field) => ({
    key: field.key,
    label: field.label,
    oldValue: formatFieldValue(field.key, current),
    newValue: formatFieldValue(field.key, incoming),
    changed: isFieldChanged(field.key, current, incoming),
  }));
}

function emptyPreview(errors: IPickingNoteImportError[]): IPickingNoteImportPreview {
  return {
    created: [],
    overwritten: [],
    unchangedCount: 0,
    errors,
  };
}

function parseSupportPkg(value: unknown): boolean | null {
  if (value === true || value === 1) {
    return true;
  }
  if (value === false || value === 0) {
    return false;
  }
  const text = String(value ?? '').trim();
  if (text === '是') {
    return true;
  }
  if (text === '否' || text === '') {
    return false;
  }
  return null;
}

function readCell(row: unknown[], columnIndex: Map<string, number>, column: PickingNoteColumn): unknown {
  const index = columnIndex.get(column);
  if (index === undefined) {
    return '';
  }
  return row[index];
}

function isBlankRow(row: unknown[], columnIndex: Map<string, number>): boolean {
  return PICKING_NOTE_COLUMNS.every((column) => String(readCell(row, columnIndex, column) ?? '').trim() === '');
}

function validateCandidate(rowIndex: number, cells: unknown[], columnIndex: Map<string, number>): IParsedCandidate {
  const sku = String(readCell(cells, columnIndex, 'sku') ?? '').trim();
  const pickingUnit = toFiniteNumber(readCell(cells, columnIndex, '1拣货单位=多少sku?'));
  const pickingUnitName = String(readCell(cells, columnIndex, '拣货单位名') ?? '').trim();
  const pickingSkuName = String(readCell(cells, columnIndex, '拣货SKU名') ?? '').trim();
  const supportPkg = parseSupportPkg(readCell(cells, columnIndex, '是否支持PKG打包'));
  const pkgRaw = readCell(cells, columnIndex, '1 PKG=多少SKU');
  const pkgUnit = toFiniteNumber(pkgRaw);
  const pkgUnitName = String(readCell(cells, columnIndex, 'PKG打包单位名') ?? '').trim();
  const messages: string[] = [];

  if (!sku) {
    messages.push('SKU不能为空');
  }
  if (pickingUnit === null) {
    messages.push('拣货单位数量必须是数字');
  } else if (pickingUnit < MIN_PICKING_UNIT) {
    messages.push('拣货单位数量不能小于0.01');
  }
  if (!pickingUnitName) {
    messages.push('拣货单位名不能为空');
  }
  if (!pickingSkuName) {
    messages.push('拣货SKU名不能为空');
  }
  if (supportPkg === null) {
    messages.push('是否支持PKG打包只能填写是或否');
  }
  if (supportPkg === true && (pkgUnit === null || pkgUnit < MIN_PICKING_UNIT)) {
    messages.push('PKG打包单位数量不能小于0.01');
  }
  if (supportPkg === false && String(pkgRaw ?? '').trim() !== '' && pkgUnit === null) {
    messages.push('PKG打包单位数量必须是数字');
  }

  if (messages.length > 0 || supportPkg === null || pickingUnit === null) {
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
      picking_unit: pickingUnit,
      picking_unit_name: pickingUnitName,
      picking_sku_name: pickingSkuName,
      support_pkg_picking: supportPkg,
      pkg_picking_unit: pkgUnit === null ? 0 : pkgUnit,
      pkg_picking_unit_name: pkgUnitName,
    },
  };
}

function parseSheetRows(fileBuffer: ArrayBuffer): IParsedCandidate[] | IPickingNoteImportError[] {
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
  const missingColumns = PICKING_NOTE_COLUMNS.filter((column) => !columnIndex.has(column));
  if (missingColumns.length > 0) {
    return [{ rowIndex: 1, sku: '', message: `缺少列：${missingColumns.join('、')}` }];
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

function isErrorList(rows: IParsedCandidate[] | IPickingNoteImportError[]): rows is IPickingNoteImportError[] {
  return rows.length === 0 || !('messages' in rows[0]);
}

export function buildPickingNoteImportPreview(
  fileBuffer: ArrayBuffer,
  existingNotes: IPickingNoteSource[],
): IPickingNoteImportPreview {
  const parsed = parseSheetRows(fileBuffer);
  if (isErrorList(parsed)) {
    return emptyPreview(parsed);
  }

  const skuRowIndexes = new Map<string, number[]>();
  parsed.forEach((candidate) => {
    if (!candidate.sku) {
      return;
    }
    const indexes = skuRowIndexes.get(candidate.sku) || [];
    indexes.push(candidate.rowIndex);
    skuRowIndexes.set(candidate.sku, indexes);
  });

  const existingMap = new Map<string, IPickingNoteImportRow>();
  existingNotes.forEach((note) => {
    const normalized = normalizePickingNoteRow(note);
    if (normalized.sku) {
      existingMap.set(normalized.sku, normalized);
    }
  });

  const created: IPickingNoteCreatedItem[] = [];
  const overwritten: IPickingNoteOverwriteItem[] = [];
  const errors: IPickingNoteImportError[] = [];
  let unchangedCount = 0;

  parsed.forEach((candidate) => {
    const messages = candidate.messages.slice();
    const duplicatedIndexes = skuRowIndexes.get(candidate.sku) || [];
    if (candidate.sku && duplicatedIndexes.length > 1) {
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

export function getPickingNoteFieldDiff(
  item: IPickingNoteOverwriteItem,
  key: PickingNoteFieldKey,
): IPickingNoteFieldDiff | undefined {
  return item.diffs.find((diff) => diff.key === key);
}

export function exportPickingNoteExcel(notes: IPickingNoteSource[], fileName: string) {
  const header = [...PICKING_NOTE_COLUMNS];
  const body = notes.map((note) => {
    const row = normalizePickingNoteRow(note);
    return [
      row.sku,
      roundPickingNumber(row.picking_unit),
      row.picking_unit_name,
      row.picking_sku_name,
      formatBool(row.support_pkg_picking),
      roundPickingNumber(row.pkg_picking_unit),
      row.pkg_picking_unit_name,
    ];
  });
  const sheet = utils.aoa_to_sheet([header, ...body]);
  const sheetRef = sheet['!ref'];
  if (sheetRef) {
    const range = utils.decode_range(sheetRef);
    for (let rowIndex = 1; rowIndex <= range.e.r; rowIndex += 1) {
      const address = utils.encode_cell({ r: rowIndex, c: 0 });
      const cell = sheet[address];
      if (cell) {
        cell.t = 's';
        cell.v = String(cell.v ?? '');
        cell.z = '@';
      }
    }
  }
  const workbook = utils.book_new();
  utils.book_append_sheet(workbook, sheet, PICKING_NOTE_SHEET_NAME);
  const downloadName = fileName.endsWith('.xlsx') ? fileName : `${fileName}.xlsx`;
  writeFile(workbook, downloadName);
}
