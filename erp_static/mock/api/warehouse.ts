import { MockMethod } from 'vite-plugin-mock';
import MockUtil from '../mock_util';

const apiList = [
  {
    url: '/erp_api/warehouse/get_wait_print_order_ship_provider_list',
    method: 'post',
  },
  {
    url: '/erp_api/warehouse/search_wait_print_order',
    method: 'post',
  },
  {
    url: '/erp_api/warehouse/pre_submit_print_order',
    method: 'post',
  },
  {
    url: '/erp_api/warehouse/start_run_print_order_task',
    method: 'post',
  },
  {
    url: '/erp_api/warehouse/submit_manual_mark_sku_picking_note',
    method: 'post',
  },
  {
    url: '/erp_api/warehouse/query_print_order_task',
    method: 'post',
  },
  {
    url: '/erp_api/warehouse/search_manual_mark_sku_picking_note',
    method: 'post',
  },
];
const mocks = MockUtil.buildMockCases(apiList);

export default [...mocks] as MockMethod[];
