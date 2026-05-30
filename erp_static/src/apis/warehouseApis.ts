import request from '@/utils/request';
import { PageVO } from '@/apis/dto/common';

/**
 * 查询待打印订单统计信息
 */
export const getWaitPrintOrderShipProviderList = () => {
  return request.post<any, any>('/erp_api/warehouse/get_wait_print_order_ship_provider_list', {});
};
/**
 * 查询待打印订单信息
 */
export const searchWaitPrintOrder = (req: any) => {
  return request.post<any, PageVO>('/erp_api/warehouse/search_wait_print_order', req);
};
/**
 * 预提交需要打印的订单信息
 * @param req
 */
export const preSubmitPrintOrder = (req: any) => {
  return request.post<any, any>('/erp_api/warehouse/pre_submit_print_order', req);
};

/**
 * 启动打印订单任务
 * @param req
 */
export const startRunPrintOrderTask = (req: any) => {
  return request.post<any, any>('/erp_api/warehouse/start_run_print_order_task', req);
};

/**
 * 提交sku拣货备注信息
 * @param req
 */
export const submitManualMarkSkuPickingNote = (req: any) => {
  return request.post<any, any>('/erp_api/warehouse/submit_manual_mark_sku_picking_note', req);
};
/**
 * 查询sku拣货备注信息
 * @param req
 */
export const searchManualMarkSkuPickingNote = (req: any) => {
  return request.post<any, any>('/erp_api/warehouse/search_manual_mark_sku_picking_note', req);
};
/**
 * 查询打印任务信息
 * @param req
 */
export const queryPrintOrderTask = (req: any) => {
  return request.post<any, any>('/erp_api/warehouse/query_print_order_task', req);
};
