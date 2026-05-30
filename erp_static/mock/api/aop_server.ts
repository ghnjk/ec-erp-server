import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/aop_web/aop_server/cluster_manage/query',
    method: 'post',
  },
  {
    url: '/aop_web/aop_server/cluster_manage/query_architecture',
    method: 'post',
  },
  {
    url: '/aop_web/aop_server/cluster_manage/queryClusterNodeInfos',
    method: 'post',
  },
  {
    url: '/aop_web/aop_server/cluster_manage/query_tag_key',
    method: 'post',
  },
  {
    url: '/aop_web/aop_server/cluster_sys_resource_manage/query_resource_value',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];
