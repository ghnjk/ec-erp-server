import request from '@/utils/request';
import type {
  ISaveSkuSalePriceReq,
  ISearchSkuSalePriceReq,
  ISkuSalePricePageVO,
  ICreateSaleOrderReq,
  ICreateSaleOrderRes,
  IUpdateSaleOrderReq,
  IDeleteSaleOrderReq,
  ISubmitSaleOrderReq,
  ISearchSaleOrderReq,
  ISaleOrderPageVO,
} from '@/apis/dto/saleDto';

/**
 * 保存SKU销售价格
 * @param req 保存请求参数
 */
export const saveSkuSalePrice = (req: ISaveSkuSalePriceReq) => {
  return request.post<ISaveSkuSalePriceReq, any>('/erp_api/sale/save_sku_sale_price', req);
};

/**
 * 搜索SKU销售价格
 * @param req 搜索请求参数
 */
export const searchSkuSalePrice = (req: ISearchSkuSalePriceReq) => {
  return request.post<ISearchSkuSalePriceReq, ISkuSalePricePageVO>('/erp_api/sale/search_sku_sale_price', req);
};

/**
 * 创建销售订单
 * @param req 创建订单请求参数
 */
export const createSaleOrder = (req: ICreateSaleOrderReq) => {
  return request.post<ICreateSaleOrderReq, ICreateSaleOrderRes>('/erp_api/sale/create_sale_order', req);
};

/**
 * 更新销售订单
 * @param req 更新订单请求参数
 */
export const updateSaleOrder = (req: IUpdateSaleOrderReq) => {
  return request.post<IUpdateSaleOrderReq, any>('/erp_api/sale/update_sale_order', req);
};

/**
 * 删除销售订单
 * @param req 删除订单请求参数
 */
export const deleteSaleOrder = (req: IDeleteSaleOrderReq) => {
  return request.post<IDeleteSaleOrderReq, any>('/erp_api/sale/delete_sale_order', req);
};

/**
 * 确认提交销售订单
 * @param req 提交订单请求参数
 */
export const submitSaleOrder = (req: ISubmitSaleOrderReq) => {
  return request.post<ISubmitSaleOrderReq, any>('/erp_api/sale/submit_sale_order', req);
};

/**
 * 搜索销售订单
 * @param req 搜索订单请求参数
 */
export const searchSaleOrder = (req: ISearchSaleOrderReq) => {
  return request.post<ISearchSaleOrderReq, ISaleOrderPageVO>('/erp_api/sale/search_sale_order', req);
};

