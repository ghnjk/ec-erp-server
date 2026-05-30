/**
 * 分页结果DTO
 */
export type PageDto<T = any> = {
  data: Array<T>;
  totalCount: number;
};

/**
 * 运维工单接口分页返回参数
 */
export type PageVO<T = any> = {
  list: Array<T>;
  total: number;
  page: number;
  size: number;
};

/**
 * 事件工单接口分页参数
 */
export type EventOrderPageVO<T = any> = {
  data: Array<T>;
  total: number;
  page: number;
  size: number;
};
