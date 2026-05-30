import request from '@/utils/request';
import { EventOrderPageVO } from '@/apis/dto/common';

/**
 * 查询告警信息
 * @param req
 */
export const queryEventOrders = (req: any) => {
  return request.post<any, EventOrderPageVO>('/aop_web/workbench/event_order_list', req);
};
