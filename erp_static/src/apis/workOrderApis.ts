import request from '@/utils/request';
import { PageVO } from '@/apis/dto/common';

/**
 * 查询告警信息
 * @param req
 */
export const queryWorkOrders = (req: any) => {
  return request.post<any, PageVO>('/aop_web/workbench/work_order_list', req);
};
