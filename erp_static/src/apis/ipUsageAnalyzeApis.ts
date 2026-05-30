import request from '@/utils/request';
import { PageDto } from '@/apis/dto/common';
import { CcUsageData } from '@/apis/dto/ipUsageAnalyzeDto';

/**
 * 查询实例ip的主调信息
 * @param req
 */
export const queryIpCallerDetail = (req) => {
  return request.post<any, PageDto>('/aop_web/ip_usage_analyze/query_ip_caller_detail', req);
};

/**
 * 查询sid的主调信息
 * @param req
 */
export const querySidCallerDetail = (req) => {
  return request.post<any, PageDto>('/aop_web/ip_usage_analyze/query_sid_caller_detail', req);
};

/**
 * 查询sid详细信息
 * @param req
 */
export const querySidExtendDetail = (req) => {
  return request.post<any, PageDto>('/aop_web/ip_usage_analyze/query_sid_extend_detail', req);
};

/**
 * 根据sid查询cc主调相关信息
 * @param req
 */
export const queryCcCallerWithSid = (req) => {
  return request.post<any, CcUsageData>('/aop_web/ip_usage_analyze/query_cc_caller_with_sid', req);
};

/**
 * 根据ip查询cc主调相关信息
 * @param req
 */
 export const queryCcCallerWithIp = (req) => {
  return request.post<any, CcUsageData>('/aop_web/ip_usage_analyze/query_cc_caller_with_ip', req);
};
