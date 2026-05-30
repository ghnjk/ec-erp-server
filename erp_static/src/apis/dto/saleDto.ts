/**
 * SKU销售价格
 */
export interface ISkuSalePrice {
  sku: string;
  unit_price: number;
  create_time?: string;
  modify_time?: string;
}

/**
 * 销售SKU项
 */
export interface ISaleSkuItem {
  sku: string;
  sku_group?: string;
  sku_name?: string;
  erp_sku_image_url?: string;
  unit_price: number;
  quantity: number;
  total_amount?: number;
}

/**
 * 销售订单
 */
export interface ISaleOrder {
  order_id?: number;
  order_date: string;
  sale_sku_list: ISaleSkuItem[];
  total_amount?: number;
  status?: string;
  is_delete?: number;
  create_time?: string;
  modify_time?: string;
}

/**
 * 保存SKU销售价格请求参数
 */
export interface ISaveSkuSalePriceReq {
  sku: string;
  unit_price: number;
}

/**
 * 搜索SKU销售价格请求参数
 */
export interface ISearchSkuSalePriceReq {
  sku?: string;
  current_page?: number;
  page_size?: number;
}

/**
 * 创建销售订单请求参数
 */
export interface ICreateSaleOrderReq {
  order_date: string;
  sale_sku_list: ISaleSkuItem[];
}

/**
 * 更新销售订单请求参数
 */
export interface IUpdateSaleOrderReq {
  order_id: number;
  order_date?: string;
  sale_sku_list?: ISaleSkuItem[];
  status?: string;
}

/**
 * 删除销售订单请求参数
 */
export interface IDeleteSaleOrderReq {
  order_id: number;
}

/**
 * 提交销售订单请求参数
 */
export interface ISubmitSaleOrderReq {
  order_id: number;
}

/**
 * 搜索销售订单请求参数
 */
export interface ISearchSaleOrderReq {
  status?: string;
  begin_date?: string;
  end_date?: string;
  current_page?: number;
  page_size?: number;
}

/**
 * SKU销售价格分页结果
 */
export interface ISkuSalePricePageVO {
  total: number;
  list?: ISkuSalePrice[];  // 实际返回的字段（标准）
  records?: ISkuSalePrice[];  // 旧版本兼容字段
}

/**
 * 销售订单分页结果
 */
export interface ISaleOrderPageVO {
  total: number;
  list?: ISaleOrder[];  // 实际返回的字段（标准）
  records?: ISaleOrder[];  // 旧版本兼容字段
}

/**
 * 创建订单响应
 */
export interface ICreateSaleOrderRes {
  order_id: number;
}

