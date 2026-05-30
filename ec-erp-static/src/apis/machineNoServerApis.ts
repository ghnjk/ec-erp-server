import request from '@/utils/request';
import { PageDto } from '@/apis/dto/common';

/**
 * 查询分配规则
 * @param req
 */
export const queryAllocateRule = (req) => {
  return request.post<any, any>('/aop_web/machine_no/rule/query', req);
};

/**
 * 查询分配规则
 * @param req
 */
export const queryAllocateRuleExtend = (req) => {
  return request.post<any, PageDto<any>>('/aop_web/machine_no/rule/query_extend', req);
};

/**
 * 创建分配规则
 * @param req
 */
export const createAllocateRule = (req) => {
  return request.post<any, any>('/aop_web/machine_no/rule/create_all', req);
};

/**
 * 更新分配规则
 * @param req
 */
export const updateAllocateRule = (req) => {
  return request.post<any, any>('/aop_web/machine_no/rule/update_all', req);
};

/**
 * 查询流程结果
 * @param req
 */
export const queryFlowResult = (req) => {
  return request.post<any, PageDto<any>>('/aop_web/machine_no/flow/query', req);
};

/**
 * 解锁流程
 * @param req
 */
export const unlockFlow = (req) => {
  return request.post<any, PageDto<any>>('/aop_web/machine_no/flow/unlock', req);
};

/**
 * 查询富容器分配结果信息
 * @param req
 */
export const queryRichContainerAllocateResult = (req) => {
  return request.post<any, PageDto<any>>('/aop_web/machine_no/rich_container/query_result', req);
};

/**
 * 查询物理机/微服务分配结果信息
 * @param req
 */
export const queryNormalAllocateResult = (req) => {
  return request.post<any, PageDto<any>>('/aop_web/machine_no/normal/query_result', req);
};

/**
 * 清理机器编号
 * @param req
 */
export const cleanRichContainerMachineNo = (req) => {
  return request.post<any, any>('/aop_web/machine_no/rich_container/clean', req);
};

/**
 * 清理物理机/微服务机器编号
 */
export const cleanNormalMachineNo = (req) => {
  return request.post<any, any>('/aop_web/machine_no/normal/clean', req);
};

/**
 * 手动触发
 * @param req
 */
export const manualTrigger = (req) => {
  return request.post<any, any>('/aop_web/machine_no/flow/manual_trigger', req);
};

/**
 * 放弃
 * @param req
 */
export const giveUp = (req) => {
  return request.post<any, any>('/aop_web/machine_no/flow/give_up', req);
};

/**
 * 查询物理机/微服务分配结果信息
 * @param req
 */
export const queryNoUsage = (req) => {
  return request.post<any, any>('/aop_web/machine_no/record/query_no_usage', req);
};

/**
 * 查询分配占用情况
 * @param req
 */
export const queryRecord = (req) => {
  return request.post<any, PageDto<any>>('/aop_web/machine_no/record/query', req);
};
