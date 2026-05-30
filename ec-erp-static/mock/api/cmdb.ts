import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/aop_web/cmdb/query_busi_type',
    method: 'post',
  },
  {
    url: '/aop_web/cmdb/query_fit_department',
    method: 'post',
  },
  {
    url: '/aop_web/cmdb/query_fit_staff',
    method: 'post',
  },
  {
    url: '/aop_web/cmdb/query_busi_tree',
    method: 'post',
  },
  {
    url: '/aop_web/cmdb/query_machine',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];
