import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/erp_api/supplier/search_supplier',
    method: 'post',
  },
  {
    url: '/erp_api/supplier/search_sku',
    method: 'post',
  },
  {
    url: '/erp_api/supplier/search_sku_purchase_price',
    method: 'post',
  },
  {
    url: '/erp_api/supplier/search_purchase_order',
    method: 'post',
  },
  {
    url: '/erp_api/supplier/query_sku_purchase_price',
    method: 'post',
  },
  {
    url: '/erp_api/supplier/submit_purchase_order_and_next_step',
    method: 'post',
  },
  {
    url: '/erp_api/supplier/save_purchase_order',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];
