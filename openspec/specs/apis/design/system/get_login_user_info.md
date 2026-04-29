# 获取登录用户信息

## 接口信息

- **接口路径**: `/erp_api/system/get_login_user_info`
- **请求方法**: POST
- **接口描述**: 获取当前已登录用户的详细信息
- **权限要求**: 无（仅需登录态）
- **Handler**: [ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `get_login_user_info`

## 请求参数

无（依赖 session）

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 用户信息对象 |
| ∟ userName | string | 用户名 |
| ∟ groupName | string | 用户组（固定 `""`） |
| ∟ roles | array | 当前 project 下的角色列表（已按 project_id 过滤） |
| &nbsp;&nbsp;∟ name | string | 角色名称 |
| &nbsp;&nbsp;∟ level | int | 角色等级 |
| &nbsp;&nbsp;∟ memo | string | 角色说明（Unicode 编码） |
| &nbsp;&nbsp;∟ project_id | string | 所属项目 |
| ∟ admin | int | 是否管理员（0/1） |
| ∟ project_id | string | 当前 session 中的项目 ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户未登录（session 无 `user_name`） |

## 请求示例

```json
{
  "timestamp": "TRACE_1709991728857",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/system/get_login_user_info",
  "traceId": "TRACE_1709991728857",
  "body": {}
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "admin": 1,
    "groupName": "",
    "project_id": "malaysia",
    "roles": [
      {
        "level": 1,
        "memo": "u4f9bu5e94u94feu7ba1u7406",
        "name": "supply",
        "project_id": "malaysia"
      }
    ],
    "userName": "jk"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857
}
```

### 错误响应

```json
{
  "result": 1001,
  "resultMsg": "not login.",
  "traceId": 1709991728857
}
```

## 业务逻辑说明

1. 从 session 取 `user_name`，未登录返回 1001
2. 调用 `backend.get_user` 取用户记录
3. 取 session 中 `project_id`
4. 过滤 `roles`，仅保留当前 project 下的角色
5. 返回用户信息

## 关联

- 数据表：[t_user_info](../../../data-model/design/t_user_info.md)
- 模块 spec：[system_module_spec.md](../../../system_module_spec.md)
- 业务文档：[docs/erp_api/system/get_login_user_info.md](../../../../../docs/erp_api/system/get_login_user_info.md)

## 注意事项

- 此接口完全依赖 session，必须先调用 `login_user` 或 `login_user_with_token`
- 前端通常用于：判断登录状态、判断当前权限、刷新页面后获取用户信息

## Change-Log

### 初始版本 - 获取登录用户信息接口

**变更类型**：新增接口

**变更原因**：前端需要回查登录态与权限。

**变更内容**：
- 新增 `POST /erp_api/system/get_login_user_info`
- 完全依赖 session

**前端影响**：登录态轮询/刷新页面调用。

**回滚方式**：不允许回滚。

**关联代码改动**：
- handler：[ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `get_login_user_info`
- 数据表：[t_user_info](../../../data-model/design/t_user_info.md)
