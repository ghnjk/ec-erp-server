import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/erp_api/system/get_login_user_info',
    method: 'post',
  },
  {
    url: '/erp_api/system/get_backend_erp_status',
    method: 'post',
  },
  {
    url: '/erp_api/system/up_seller_manual_login',
    method: 'post',
  },
  {
    url: '/erp_api/system/login_user_with_token',
    method: 'post',
  },
  {
    url: '/erp_api/system/dict',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];
