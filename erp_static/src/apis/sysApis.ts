/* eslint-disable camelcase */
import request from '@/utils/request';

/**
 * 获取用户登录信息
 */
export const getLoginUserInfo = () => {
  return request.post('/erp_api/system/get_login_user_info');
};

export interface BackendErpStatus {
  erp_type: 'big_seller' | 'up_seller' | string;
  email: string;
  warehouse_id: string;
  is_login: boolean;
  auto_login: boolean;
  message: string;
}

/**
 * 获取后端 ERP 登录状态
 */
export const getBackendErpStatus = () => {
  return request.post<any, BackendErpStatus>('/erp_api/system/get_backend_erp_status', {});
};

export type UpSellerManualLoginStatus = 'logged_in' | 'need_email_code' | 'failed' | string;

export interface UpSellerManualLoginResult {
  login_status: UpSellerManualLoginStatus;
  logs: string;
  exit_code: number;
  message: string;
}

/**
 * UpSeller 人工登录（两阶段：无参发码 / 带 email_code 完成登录）
 */
export const upSellerManualLogin = (payload: { email_code?: string } = {}) => {
  return request.post<any, UpSellerManualLoginResult>('/erp_api/system/up_seller_manual_login', payload);
};

/**
 * 用户登录
 */
export const login = (loginInfo) => {
  return request.post('/erp_api/system/login_user', loginInfo);
};

export const loginWithToken = (token) => {
  return request.post('/erp_api/system/login_user_with_token', {
    token,
  });
};

/**
 * 字典
 */
export const dictApi = (req: any) => {
  return request.post('/erp_api/system/dict', req);
};
