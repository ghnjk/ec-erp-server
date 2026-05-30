import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/aop_web/workbench/work_order_list',
    method: 'post',
  },
  {
    url: '/aop_web/workbench/event_order_list',
    method: 'post',
  },
  {
    url: '/aop_web/group_order/list',
    method: 'post',
  },
  {
    url: '/aop_web/group_order/create',
    method: 'post',
  },
  {
    url: '/aop_web/group_order/update',
    method: 'post',
  },
  {
    url: '/aop_web/group_order/update_status',
    method: 'post',
  },
  {
    url: '/aop_web/group_order/delete_by_id',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];
