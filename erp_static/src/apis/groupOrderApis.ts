import request from '@/utils/request';

/**
 * 查询告警信息
 * @param req
 */
export const getList = (req: any) => {
  return request.post<any, any>('/aop_web/group_order/list', req);
};

export const createOrder = (req: any) => {
  return request.post<any, number>('/aop_web/group_order/create', req);
};

export const updateOrder = (req: any) => {
  return request.post<any, number>('/aop_web/group_order/update', req);
};

export const updateStatus = (req: any) => {
  return request.post<any, number>('/aop_web/group_order/update_status', req);
};

export const deleteById = (req: any) => {
  return request.post<any, number>('/aop_web/group_order/delete_by_id', req);
};
