import { ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { searchSupplier } from '@/apis/supplierApis';

export const ORDER_TYPE_DOMESTIC = 1; // 境内进货采购单
export const ORDER_TYPE_OVERSEAS = 2; // 境外线下采购单

// 所有供应商信息
export const allSuppliers = ref([]);
// 供应商options
export const supplierIdOptions = ref([]);

export async function loadSupplierInfo() {
  allSuppliers.value = [];
  supplierIdOptions.value = [];
  const req = {
    current_page: 1,
    page_size: 10000,
  };
  try {
    const res = await searchSupplier(req);
    allSuppliers.value = res.list;
    res.list.forEach((item) => {
      supplierIdOptions.value.push({
        label: item.supplier_name,
        value: item.supplier_id,
      });
    });
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询供应商异常: ${e}`);
  }
}

/**
 *     类型1(境内进货)采购流程图：
 *     草稿 -- 选择采购物品，提交采购单 -->
 *     供应商捡货中 -- 厂家提供采购清单，采购单确认 -->
 *     待发货 -- 厂家发货，填写海运公司，填写港口，填写海运费， 预计到达日期 -->
 *     海运中 -- 抵达海外仓库，点货入库 -->
 *     已入库 -- 同步erp -->
 *     完成
 *
 *     类型2(境外线下)采购流程图：
 *     草稿 -- 选择采购物品，提交采购单 -->
 *     境外拣货 -- 确认出货 -->
 *     已出库 -- 同步ERP出库 -->
 *     完成
 */
export function getNextPurchaseAction(currentStep, orderType = ORDER_TYPE_DOMESTIC) {
  if (orderType === ORDER_TYPE_OVERSEAS) {
    if (currentStep === null || currentStep === undefined || currentStep === '草稿') {
      return '销售';
    }
    if (currentStep === '境外拣货') {
      return '确认出货';
    }
    if (currentStep === '已出库') {
      return '同步ERP';
    }
    return '下一步';
  } else {
    if (currentStep === null || currentStep === undefined || currentStep === '草稿') {
      return '选购';
    }
    if (currentStep === '供应商捡货中') {
      return '采购单确认';
    }
    if (currentStep === '待发货') {
      return '发货';
    }
    if (currentStep === '海运中') {
      return '点货入库';
    }
    if (currentStep === '已入库') {
      return '同步erp';
    }
    return '下一步';
  }
}

export function getPurchaseOrderPreState(currentStep, orderType = ORDER_TYPE_DOMESTIC) {
  if (currentStep === null || currentStep === undefined || currentStep === '草稿') {
    return null;
  }
  if (orderType === ORDER_TYPE_OVERSEAS) {
    if (currentStep === '境外拣货') {
      return '草稿';
    }
    if (currentStep === '已出库') {
      return '境外拣货';
    }
    return null;
  }
  if (currentStep === '供应商捡货中') {
    return '草稿';
  }
  if (currentStep === '待发货') {
    return '供应商捡货中';
  }
  if (currentStep === '海运中') {
    return '待发货';
  }
  if (currentStep === '已入库') {
    return '海运中';
  }
  return null;
}

/**
 * 判断当前步骤是否为终态
 */
export function isPurchaseOrderCompleted(currentStep) {
  return currentStep === '完成';
}

/**
 * 判断当前步骤是否为草稿
 */
export function isPurchaseOrderDraft(currentStep) {
  return currentStep === null || currentStep === undefined || currentStep === '草稿';
}

/**
 * 判断当前步骤是否需要同步ERP（即最后一个操作步骤）
 */
export function isPurchaseOrderSyncErpStep(currentStep, orderType = ORDER_TYPE_DOMESTIC) {
  if (orderType === ORDER_TYPE_OVERSEAS) {
    return currentStep === '已出库';
  }
  return currentStep === '已入库';
}
