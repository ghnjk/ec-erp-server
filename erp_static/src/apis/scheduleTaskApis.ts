import request from '@/utils/request';

/**
 * 值班提醒定时任务
 * @param req
 */

/**
 * 值班提醒列表
 * @param req
 */
export const getList = (req: any) => {
  return request.post<any, any>('aop_web/remind_job/list', req);
};

/**
 * 添加
 * @param req
 */
export const saveOrUpdate = (req: any) => {
  return request.post<any, any>('aop_web/remind_job/saveOrUpdate', req);
};

/**
 * 删除
 * @param req
 */
export const deleteBatch = (req: any) => {
  return request.post<any, any>('aop_web/remind_job/deleteBatch', req);
};

/**
 * 暂停
 * @param req
 */
export const pauseNow = (req: any) => {
  return request.post<any, any>('aop_web/remind_job/pause', req);
};
/**
 * 恢复
 * @param req
 */
export const resumeNow = (req: any) => {
  return request.post<any, any>('aop_web/remind_job/resume', req);
};
/**
 * 立即执行
 * @param req
 */
export const runNow = (req: any) => {
  return request.post<any, any>('aop_web/remind_job/run', req);
};

/**
 * 查询日志
 * @param req
 */
export const logList = (req: any) => {
  return request.post<any, any>('aop_web/remind_job/log/list', req);
};
