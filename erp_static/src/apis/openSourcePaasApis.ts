import request from '@/utils/request';
import { PageDto } from '@/apis/dto/common';
import { AddUserResult, DeployNewServerResult, HostIpInfo } from '@/apis/dto/OpenSourcePaasDto';

/**
 * 查询集群信息
 * @param req
 */
export const queryServerList = (req) => {
  return request.post<any, PageDto>('/aop_web/open_source_paas/infoManage/getClusterInfo', req);
};

/**
 * 查询用户信息
 * @param req
 */
export const queryUserInfoList = (req) => {
  return request.post<any, PageDto>('/aop_web/open_source_paas/infoManage/getUserInfo', req);
};

/**
 * 根据部署环境查询IP列表
 * @param req
 */
export const queryHostIp = (req) => {
  return request.post<any, HostIpInfo[]>('/aop_web/open_source_paas/infoManage/queryHostIp', req);
};

/**
 * 部署新SFTP服务
 * @param req
 */
export const deployNewSFTPServerWithUser = (req) => {
  return request.post<any, DeployNewServerResult>('/aop_web/open_source_paas/sftp/deployNewSFTPServerWithUser', req);
};

/**
 * 添加安全组规则ip白名单
 * @param req
 */
export const addIpWhites = (req) => {
  return request.post<any, any>('/aop_web/open_source_paas/ipWhite/addSFTPWhiteList', req);
};

/**
 * 添加SFTP新用户
 * @param req
 */
export const addSFTPUser = (req) => {
  return request.post<any, AddUserResult>('/aop_web/open_source_paas/sftp/addSFTPUser', req);
};
