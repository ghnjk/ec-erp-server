import request from '@/utils/request';
import { PageVO } from '@/apis/dto/common';

/**
 * 查询供应商信息
 * @param req
 */
export const searchSupplier = (req: any) => {
  return request.post<any, PageVO>('/erp_api/supplier/search_supplier', req);
};
/**
 * 检索商品SKU
 * @param req
 */
export const searchSku = (req: any) => {
  return request.post<any, PageVO>('/erp_api/supplier/search_sku', req);
};
export const saveSku = (req: any) => {
  return request.post<any, PageVO>('/erp_api/supplier/save_sku', req);
};
export const addSku = (req: any) => {
  return request.post<any, any>('/erp_api/supplier/add_sku', req);
};
export const syncAllSku = () => {
  return request.post<any, any>('/erp_api/supplier/sync_all_sku', {});
};
/**
 * 检索商品SKU采购价
 * @param req
 */
export const searchSkuPurchasePrice = (req: any) => {
  return request.post<any, PageVO>('/erp_api/supplier/search_sku_purchase_price', req);
};

/**
 * 检索采购单
 * @param req
 */
export const searchPurchaseOrder = (req: any) => {
  return request.post<any, PageVO>('/erp_api/supplier/search_purchase_order', req);
};
/**
 * 保存采购单
 * @param req
 */
export const savePurchaseOrder = (req: any) => {
  return request.post<any, any>('/erp_api/supplier/save_purchase_order', req);
};
/**
 * 提交采购单并扭转到下一环节
 * @param req
 */
export const submitPurchaseOrderAndNextStep = (req: any) => {
  return request.post<any, any>('/erp_api/supplier/submit_purchase_order_and_next_step', req);
};
/**
 * 查询sku的供应价格
 */
export const querySkuPurchasePrice = (req: any) => {
  return request.post<any, any>('/erp_api/supplier/query_sku_purchase_price', req);
};
