import axios from 'axios';
import { MessagePlugin } from 'tdesign-vue-next';
import proxy from '../config/proxy';

const env = import.meta.env.MODE || 'development';

const host = env === 'mock' ? '/' : proxy[env].host; // 如果是mock模式 就不配置host 会走本地Mock拦截

/**
 * 生成traceId
 * @param len
 */
function genTraceId(len) {
  len = len || 32;
  const $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';
  const maxPos = $chars.length;
  let pwd = '';
  for (let i = 0; i < len; i++) pwd += $chars.charAt(Math.floor(Math.random() * maxPos));

  return pwd;
}

export interface IReturnResult<T = any> {
  result: number;
  resultMsg: string;
  traceId: string;
  data: T;
}

const CODE = {
  LOGIN_TIMEOUT: 1000,
  REQUEST_SUCCESS: 0,
  REQUEST_FOBID: 1001,
};

const instance = axios.create({
  baseURL: host,
  timeout: 1000,
  headers: { 'X-Requested-With': 'XMLHttpRequest' }, // 让后台判定为axios请求
  withCredentials: true,
});

const omsRequestConf = (config) => {
  if (config.method === 'post') {
    config.data = {
      timestamp: Date.now(),
      serviceName: 'ec_erp_static',
      apiUrl: config.url,
      traceId: genTraceId(32),
      body: config.data,
    };
  }
  return config;
};

// 拦截post请求，前面加上oms头
instance.interceptors.request.use(omsRequestConf);

instance.defaults.timeout = 300000;

instance.interceptors.response.use(
  (response) => {
    if (response.status === 200) {
      const { data } = response;
      if (data.result === CODE.REQUEST_SUCCESS) {
        return data.data;
      }

      MessagePlugin.error(`接口请求报错: ${data.resultMsg}`);
      return Promise.reject(data);
    }
    return Promise.reject(response);
  },
  (error) => {
    if (error.response?.status >= 500) {
      MessagePlugin.error('服务器异常');
    } else if (error.response?.status === 401 || error.response?.status === 403) {
      MessagePlugin.warning(`接口权限过期, 请刷新浏览器重新登录`);
    } else {
      MessagePlugin.closeAll();
      MessagePlugin.error(`接口请求异常: ${error.message}`);
    }

    const { config } = error;

    if (!config || !config.retry) return Promise.reject(error);

    config.retryCount = config.retryCount || 0;

    if (config.retryCount >= config.retry) return Promise.reject(error);

    config.retryCount += 1;

    const backoff = new Promise((resolve) => {
      setTimeout(() => {
        resolve(null);
      }, config.retryDelay || 1);
    });

    return backoff.then(() => instance(config));
  },
);

export default instance;
