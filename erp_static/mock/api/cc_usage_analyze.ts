import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/aop_web/cc_usage_analyze/query_logic_view',
    method: 'post',
  },
  {
    url: '/aop_web/cc_usage_analyze/query_biz_unit_view',
    method: 'post',
  },
  {
    url: '/aop_web/cc_usage_analyze/query_cc_usage_report_detail',
    method: 'post',
  },
  {
    url: '/aop_web/cc_usage_analyze/query_conf_key_relate_info',
    method: 'post',
  },
  {
    url: '/aop_web/cc_usage_analyze/update_logic_view',
    method: 'post',
  },
  {
    url: '/aop_web/cc_usage_analyze/update_biz_unit_view',
    method: 'post',
  },
  {
    url: '/aop_web/cc_usage_analyze/update_conf_key_relate_info',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];
