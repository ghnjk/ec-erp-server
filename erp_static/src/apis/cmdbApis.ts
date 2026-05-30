import request from '@/utils/request';
export interface StaffInfo {
  centerName: string;
  mainGroupName: string;
  mainGroupID: string;
  leaderName: string;
  staffEngName: string;
  staffName: string;
}
/**
 * 查询包产大类
 */
export const queryBusiType = () => {
  return request.post<any, any>('/aop_web/cmdb/query_busi_type', {});
};

/**
 * 查询cmdb业务
 */
export const queryBusiSystem = () => {
  return request.post<any, any>('/aop_web/cmdb/query_busi_system', {});
};

/**
 * 查询员工信息
 */
export const queryStaffInfo = () => {
  return request.post<any, StaffInfo[]>('/aop_web/cmdb/query_fit_staff', {});
};

/**
 * 查询员工信息
 */
export const queryBusiTree = () => {
  return request.post<any, any>('/aop_web/cmdb/query_busi_tree', {});
};

/**
 * 查询员工架构
 */
export const queryFitDepartment = () => {
  return request.post<any, any>('/aop_web/cmdb/query_fit_department', {});
};

/**
 * 查询设备
 */
export const queryMachine = (req) => {
  return request.post<any, any>('/aop_web/cmdb/query_machine', req);
};
