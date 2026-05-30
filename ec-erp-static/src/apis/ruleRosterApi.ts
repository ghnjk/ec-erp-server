import request from '@/utils/request';

/**
 * 查询值班人员名字
 */
export const queryDutyRosterName = () => {
  return request.post<any, string>('/aop_web/rule_roster/duty_roster_name');
};
