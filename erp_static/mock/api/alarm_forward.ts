import MockUtil from '../mock_util';
import { MockMethod } from 'vite-plugin-mock';

const apiList = [
  {
    url: '/aop_web/alarm_forward/get_alarm_info_echart_data',
    method: 'post',
  },
  {
    url: '/aop_web/alarm_forward/query_alarm_info',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [
  ...mocks,
] as MockMethod[];
