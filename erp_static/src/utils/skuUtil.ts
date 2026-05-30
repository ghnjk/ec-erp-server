import { ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { searchSku } from '@/apis/supplierApis';

/**
 * 计算单个采购包装单位的打包体积（m³）。
 * 入参单位均为 cm（与 t_sku_info.Fsku_pack_* 一致），未填写按 0 处理。
 */
export function calcPackVolumeM3PerUnit(
  packLength: number | null | undefined,
  packWidth: number | null | undefined,
  packHeight: number | null | undefined,
): number {
  const l = Number(packLength) || 0;
  const w = Number(packWidth) || 0;
  const h = Number(packHeight) || 0;
  if (l <= 0 || w <= 0 || h <= 0) return 0;
  // cm³ -> m³
  return (l * w * h) / 1_000_000;
}

/**
 * 计算采购明细某行的总打包体积（m³）。
 *   总体积 = (quantity / sku_unit_quantity) * 单包装体积
 * quantity 为 SKU 数（个），sku_unit_quantity 为每个采购单位包含的 SKU 数。
 */
export function calcPackVolumeM3(
  quantity: number | null | undefined,
  skuUnitQuantity: number | null | undefined,
  packLength: number | null | undefined,
  packWidth: number | null | undefined,
  packHeight: number | null | undefined,
): number {
  const qty = Number(quantity) || 0;
  const unitQty = Number(skuUnitQuantity) || 0;
  if (qty <= 0 || unitQty <= 0) return 0;
  const perUnit = calcPackVolumeM3PerUnit(packLength, packWidth, packHeight);
  if (perUnit <= 0) return 0;
  return qty * perUnit;
}

/**
 * 体积 m³ 的统一格式化（保留 4 位小数；未填写显示 "--"）。
 */
export function formatVolumeM3(volumeM3: number | null | undefined): string {
  const v = Number(volumeM3) || 0;
  if (v <= 0) return '--';
  return v.toFixed(3);
}

// 所有sku信息
const allSkuList = ref([]);
// 所有skuGroup的options
export const skuGroupNameOptions = ref([]);
// 按group分组的sku <groupName, skuList>
export const skuGroupMap = ref(new Map<string, any[]>());
// sku map <sku, skuInfo>
export const skuMap = ref(new Map<string, any>());
// 数据是否已加载
export const skuInfoLoaded = ref(false);
// 正在加载的Promise（防止重复加载）
let loadingPromise: Promise<void> | null = null;

export async function loadSkuInfo() {
  // 如果正在加载，返回加载中的Promise
  if (loadingPromise) {
    return loadingPromise;
  }

  // 如果已加载，直接返回
  if (skuInfoLoaded.value) {
    return Promise.resolve();
  }

  loadingPromise = (async () => {
    allSkuList.value = [];
    skuGroupNameOptions.value = [];
    skuGroupMap.value = new Map<string, any[]>();
    skuMap.value = new Map<string, any[]>();
    skuInfoLoaded.value = false;
  const req = {
    current_page: 1,
    page_size: 10000,
  };
  try {
    const res = await searchSku(req);
    allSkuList.value = res.list;
    new Set(res.list.map((item) => item.sku_group)).forEach((item) => {
      skuGroupNameOptions.value.push({
        label: item,
        value: item,
      });
    });
    res.list.forEach((item) => {
      skuMap.value.set(item.sku, item);
      const groupName = item.sku_group;
      if (skuGroupMap.value.has(groupName)) {
        skuGroupMap.value.get(groupName).push(item);
      } else {
        skuGroupMap.value.set(groupName, [item]);
      }
    });
    
    // 标记为已加载
    skuInfoLoaded.value = true;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询sku异常: ${e}`);
  } finally {
    loadingPromise = null;
  }
  })();

  return loadingPromise;
}
