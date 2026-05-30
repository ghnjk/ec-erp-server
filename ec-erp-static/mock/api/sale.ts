import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/erp_api/sale/save_sku_sale_price',
    method: 'post',
  },
  {
    url: '/erp_api/sale/search_sku_sale_price',
    method: 'post',
  },
  {
    url: '/erp_api/sale/create_sale_order',
    method: 'post',
  },
  {
    url: '/erp_api/sale/update_sale_order',
    method: 'post',
  },
  {
    url: '/erp_api/sale/delete_sale_order',
    method: 'post',
  },
  {
    url: '/erp_api/sale/submit_sale_order',
    method: 'post',
  },
  {
    url: '/erp_api/sale/search_sale_order',
    method: 'post',
  },
];

const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];

