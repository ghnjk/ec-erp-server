import { ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { searchManualMarkSkuPickingNote } from '@/apis/warehouseApis';

/**
 * SKU拣货备注信息
 */
export interface ISkuPickingNote {
  project_id: string;
  sku: string;
  picking_unit: number;
  picking_unit_name: string;
  support_pkg_picking: boolean;
  pkg_picking_unit: number;
  pkg_picking_unit_name: string;
  picking_sku_name: string;
  erp_sku_name: string;
  erp_sku_image_url: string;
}

/**
 * 拣货数量信息
 */
export interface IPickingInfo {
  picking_count: number;
  picking_unit: string;
  display_text: string;
}

// SKU拣货备注映射表 <sku, pickingNote>
export const skuPickingNoteMap = ref(new Map<string, ISkuPickingNote>());

/**
 * 加载所有SKU拣货备注信息
 */
export async function loadAllSkuPickingNote() {
  skuPickingNoteMap.value = new Map<string, ISkuPickingNote>();
  
  const pageSize = 10000;
  let currentPage = 1;
  let hasMore = true;

  try {
    while (hasMore) {
      const req = {
        current_page: currentPage,
        page_size: pageSize,
        search_sku: '',
      };
      
      const res = await searchManualMarkSkuPickingNote(req);
      
      // 建立索引映射
      if (res.list && res.list.length > 0) {
        res.list.forEach((item: ISkuPickingNote) => {
          skuPickingNoteMap.value.set(item.sku, item);
        });
      }
      
      // 判断是否还有下一页
      hasMore = res.list && res.list.length === pageSize;
      currentPage++;
    }
    
    console.log(`成功加载 ${skuPickingNoteMap.value.size} 条SKU拣货备注信息`);
  } catch (e) {
    console.error('加载SKU拣货备注失败:', e);
    await MessagePlugin.error(`加载SKU拣货备注异常: ${e}`);
  }
}

/**
 * 根据SKU和数量计算拣货信息
 * @param sku SKU编码
 * @param quantity 数量
 * @returns 拣货信息
 */
export function calculatePickingInfo(sku: string, quantity: number): IPickingInfo {
  const pickingNote = skuPickingNoteMap.value.get(sku);
  
  // 如果没有找到拣货备注，返回默认值
  if (!pickingNote) {
    return {
      picking_count: quantity,
      picking_unit: 'pcs',
      display_text: `${quantity} pcs`,
    };
  }

  // 如果支持整包拣货
  if (pickingNote.support_pkg_picking && pickingNote.pkg_picking_unit > 0) {
    const pkgCount = Math.floor(quantity / pickingNote.pkg_picking_unit);
    const remainCount = quantity % pickingNote.pkg_picking_unit;
    
    if (remainCount === 0) {
      // 正好是整包
      return {
        picking_count: pkgCount,
        picking_unit: pickingNote.pkg_picking_unit_name,
        display_text: `${pkgCount} ${pickingNote.pkg_picking_unit_name}`,
      };
    } else if (pkgCount > 0) {
      // 有整包 + 散装
      return {
        picking_count: pkgCount,
        picking_unit: pickingNote.pkg_picking_unit_name,
        display_text: `${pkgCount} ${pickingNote.pkg_picking_unit_name} + ${remainCount} ${pickingNote.picking_unit_name}`,
      };
    }
  }
  
  // 使用基础拣货单位
  const basePickingCount = quantity / pickingNote.picking_unit;
  return {
    picking_count: basePickingCount,
    picking_unit: pickingNote.picking_unit_name,
    display_text: `${basePickingCount} ${pickingNote.picking_unit_name}`,
  };
}

/**
 * 批量计算多个SKU的拣货信息并按group汇总
 * @param saleSkuList 销售SKU列表
 * @returns 按group分组的拣货摘要
 */
export function generateOrderSummary(saleSkuList: any[]): string {
  if (!saleSkuList || saleSkuList.length === 0) {
    return '-';
  }

  // 按 sku_group 分组统计总数量和总金额
  const groupMap = new Map<string, { totalQuantity: number; totalAmount: number; firstSku: string }>();

  saleSkuList.forEach((item) => {
    const group = item.sku_group || '未分组';
    const quantity = item.quantity || 0;
    const totalAmount = item.total_amount || (item.unit_price || 0) * quantity;

    if (groupMap.has(group)) {
      const existing = groupMap.get(group)!;
      groupMap.set(group, {
        totalQuantity: existing.totalQuantity + quantity,
        totalAmount: existing.totalAmount + totalAmount,
        firstSku: existing.firstSku,
      });
    } else {
      groupMap.set(group, {
        totalQuantity: quantity,
        totalAmount,
        firstSku: item.sku,
      });
    }
  });

  // 生成摘要文本
  const summaries: string[] = [];
  groupMap.forEach((value, group) => {
    // 使用该组的第一个SKU来计算拣货信息格式
    const pickingInfo = calculatePickingInfo(value.firstSku, value.totalQuantity);
    summaries.push(`${group}: ${pickingInfo.display_text} = ${value.totalAmount.toFixed(2)}`);
  });

  return summaries.join('\n');
}

