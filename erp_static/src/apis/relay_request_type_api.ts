import request from '@/utils/request';
import {PageVO} from '@/apis/dto/common';

/**
 * 字典
 * @param req
 */
export const dictOpName = (req: any) => {
  return request.post<any, any[]>('/aop_web/request_type/dict_op_name', req);
};

/**
 * 查询请求类型列表
 * @param req
 */
export const getRequestTypeList = (req: any) => {
  return request.post<any, any[]>('/aop_web/request_type/request_type_list', req);
};

/**
 * 新增请求类型
 * @param req
 */
export const addRequestType = (req: any) => {
  return request.post('/aop_web/request_type/request_type_add', req);
};

/**
 * 修改请求类型
 * @param req
 */
export const updateRequestType = (req: any) => {
  return request.post('/aop_web/request_type/request_type_update', req);
};

/**
 * 新增请求类型
 * @param req
 */
export const deleteRequestType = (req: any) => {
  return request.post('/aop_web/request_type/request_type_delete', req);
};
