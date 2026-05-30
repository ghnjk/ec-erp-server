import request from '@/utils/request';
import { PageDto } from '@/apis/dto/common';

/**
 * 查询op server依赖逻辑视图
 * @param req
 */
export const queryLogicView = (req) => {
  return request.post<any, PageDto>('/aop_web/cc_usage_analyze/query_logic_view', req);
};
/**
 * 查询业务单元物理依赖视图
 * @param req
 */
export const queryBizUnitView = (req) => {
  return request.post<any, PageDto>('/aop_web/cc_usage_analyze/query_biz_unit_view', req);
};
/**
 * 查询调用记录明细
 * @param req
 */
export const queryCcUsageReportDetail = (req) => {
  return request.post<any, PageDto>('/aop_web/cc_usage_analyze/query_cc_usage_report_detail', req);
};
/**
 * 查询confkey关联的信息
 * @param req
 */
export const queryConfKeyRelateInfo = (req) => {
  return request.post<any, PageDto>('/aop_web/cc_usage_analyze/query_conf_key_relate_info', req);
};
/**
 * 更新逻辑视图记录
 * @param req
 */
export const updateLogicView = (req) => {
  return request.post<any, any>('/aop_web/cc_usage_analyze/update_logic_view', req);
};
/**
 * 修改业务单元视图
 * @param req
 */
export const updateBizUnitView = (req) => {
  return request.post<any, any>('/aop_web/cc_usage_analyze/update_biz_unit_view', req);
};
/**
 * 跟心confke关联信息
 * @param req
 */
export const updateConfKeyRelateInfo = (req) => {
  return request.post<any, any>('/aop_web/cc_usage_analyze/update_conf_key_relate_info', req);
};
