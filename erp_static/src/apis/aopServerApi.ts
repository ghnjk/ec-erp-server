import request from '@/utils/request';
import { PageDto } from '@/apis/dto/common';

/**
 * 查询集群列表
 * @param req
 */
export const queryCluster = (req) => {
  return request.post<any, PageDto>('/aop_web/aop_server/cluster_manage/query', req);
};

/**
 * 查询所有集群列表
 * @param req
 */
export const queryAllClusters = () => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/query_all_clusters', {});
};

/**
 * 查询集群资源值
 * @param req
 */
export const queryResourceValue = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_sys_resource_manage/query_resource_value', req);
};

/**
 * 创建系统资源
 * @param req
 */
export const createResource = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_sys_resource_manage/create', req);
};

/**
 * 创建系统资源
 * @param req
 */
export const updateResource = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_sys_resource_manage/update', req);
};

/**
 * 删除系统资源
 * @param req
 */
export const deleteResource = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_sys_resource_manage/delete', req);
};
/**
 * 查询集群资源
 * @param req
 */
export const querySysResource = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_sys_resource_manage/query', req);
};

/**
 * 查询tag key
 * @param req
 */
export const queryTagKey = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/query_tag_key', req);
};

/**
 * 查询所有资源类型
 * @param req
 */
export const queryTagValue = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/query_tag_value', req);
};

/**
 * 创建集群
 * @param req 创建请求
 */
export const createCuster = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/create', req);
};

/**
 * 更新集群
 * @param req
 */
export const updateCluster = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/update', req);
};

/**
 * 查询集群架构
 * @param req
 */
export const queryArchitecture = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/query_architecture', req);
};

/**
 * 查询集群流量
 * @param req
 */
export const queryFlowInstanceInfo = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_flow_manage/query_instance_info', req);
};

/**
 * 更新入口流量
 * @param req
 */
export const updateInFlow = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_flow_manage/update_in_flow', req);
};

/**
 * 查询框架模块元数据
 */
export const queryModuleMetaData = () => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/query_module_meta_data', {});
};

/**
 * 新增CMDB模块
 * @param req
 */
export const addCmdbServer = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/add_cmdb_server', req);
};

/**
 * 查询框架模块下业务列表
 * @param req
 */
export const queryFrameServerBus = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/query_frame_server_bus', req);
};

/**
 * 新增OP部署模块
 * @param req
 */
export const addDeployServer = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/add_deploy_server', req);
};

/**
 * 新增容器部署环境
 * @param req
 */
export const addDeployEnv = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/add_deploy_env', req);
};

/**
 * 创建富容器模块添加业务单元的ops任务单
 * @param req
 */
export const addRCUnit = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/add_rc_unit', req);
};

/**
 * 启动自定义变更任务自动执行
 * @param req
 */
export const startAutoOpsTask = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/start_auto_ops_task', req);
};

/**
 * 创建监控模块
 * @param req
 */
export const addMonitModule = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/add_monit_module', req);
};

/**
 * 创建OP任务
 * @param req
 */
export const createOpTask = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/create_op_task', req);
};

/**
 * 修改系统配置
 * @param req
 */
export const modifySysConfig = (req) => {
  return request.post<any, any>('/aop_web/aop_server/frame_module_expand/modify_sys_config', req);
};

/**
 * 查询集群节点列表
 * @param req
 */
export const queryClusterNodeInfos = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/queryClusterNodeInfos', req);
};
/**
 *  从 SDK 中获取最新的集群消息
 * @param req
 */
export const queryClusterInfoBySDK = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/queryClusterInfoBySDK', req);
};
/**
 *  冻结TKE 创建变更工单
 * @param req
 */
export const createFlowOpsTask = (req) => {
  return request.post<any, any>('/aop_web/aop_server/cluster_manage/createFlowOpsTask', req);
};
