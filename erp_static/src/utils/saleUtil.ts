import { ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { searchSkuSalePrice, saveSkuSalePrice } from '@/apis/saleApis';
import type { ISkuSalePrice } from '@/apis/dto/saleDto';

// SKU销售价格映射表 <sku, price>
export const skuSalePriceMap = ref(new Map<string, number>());
// 数据是否已加载
export const skuSalePriceLoaded = ref(false);
// 正在加载的Promise（防止重复加载）
let loadingPromise: Promise<void> | null = null;

/**
 * 加载所有SKU销售价格信息
 */
export async function loadAllSkuSalePrice() {
  // 如果正在加载，返回加载中的Promise
  if (loadingPromise) {
    return loadingPromise;
  }

  // 如果已加载，直接返回
  if (skuSalePriceLoaded.value) {
    return Promise.resolve();
  }

  loadingPromise = (async () => {
    skuSalePriceMap.value = new Map<string, number>();
    skuSalePriceLoaded.value = false;
    
    const pageSize = 10000;
    let currentPage = 1;
    let hasMore = true;

    try {
    while (hasMore) {
      const req = {
        current_page: currentPage,
        page_size: pageSize,
        sku: '',
      };
      
      const res = await searchSkuSalePrice(req);
      
      // 优先使用 list 字段（实际返回），兼容 records 字段（文档定义）
      const dataList = res.list || res.records || [];
      
      // 建立价格映射
      if (dataList.length > 0) {
        dataList.forEach((item: ISkuSalePrice) => {
          skuSalePriceMap.value.set(item.sku, item.unit_price);
        });
      }
      
      // 判断是否还有下一页
      hasMore = dataList.length === pageSize;
      currentPage++;
    }
    
    console.log(`成功加载 ${skuSalePriceMap.value.size} 条SKU销售价格信息`);
    
    // 标记为已加载
    skuSalePriceLoaded.value = true;
  } catch (e) {
    console.error('加载SKU销售价格失败:', e);
    await MessagePlugin.error(`加载SKU销售价格异常: ${e}`);
  } finally {
    loadingPromise = null;
  }
  })();

  return loadingPromise;
}

/**
 * 获取SKU的销售价格
 * @param sku SKU编码
 * @returns 销售单价，如果没有则返回0
 */
export function getSkuSalePrice(sku: string): number {
  return skuSalePriceMap.value.get(sku) || 0;
}

/**
 * 批量更新SKU销售价格
 * @param saleSkuList 销售SKU列表
 */
export async function batchUpdateSkuSalePrice(saleSkuList: any[]) {
  const updatePromises: Promise<any>[] = [];
  
  for (const item of saleSkuList) {
    const currentPrice = skuSalePriceMap.value.get(item.sku);
    const newPrice = item.unit_price;
    
    // 如果价格不存在或者价格有变化，则需要更新
    if (currentPrice === undefined || currentPrice !== newPrice) {
      updatePromises.push(
        saveSkuSalePrice({
          sku: item.sku,
          unit_price: newPrice,
        })
      );
      
      // 更新本地缓存
      skuSalePriceMap.value.set(item.sku, newPrice);
    }
  }
  
  if (updatePromises.length > 0) {
    await Promise.all(updatePromises);
    console.log(`成功更新 ${updatePromises.length} 条SKU销售价格`);
  }
}

/**
 * 计算订单总金额
 * @param saleSkuList 销售SKU列表
 * @returns 总金额
 */
export function calculateOrderTotalAmount(saleSkuList: any[]): number {
  if (!saleSkuList || saleSkuList.length === 0) {
    return 0;
  }
  
  return saleSkuList.reduce((total, item) => {
    const itemTotal = (item.unit_price || 0) * (item.quantity || 0);
    return total + itemTotal;
  }, 0);
}

