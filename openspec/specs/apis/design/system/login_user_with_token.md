# 通过 Token 登录

## 接口信息

- **接口路径**: `/erp_api/system/login_user_with_token`
- **请求方法**: POST
- **接口描述**: 通过 Base64 编码的 token 登录，或在已登录态下回查当前用户信息
- **权限要求**: 无（登录前调用）
- **Handler**: [ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `login_user_with_token`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 否 | Base64 编码后的 URL query 字符串 `user_name=xxx&password=xxx`。空字符串或未传时回查当前 session 用户信息 |

### Token 格式说明

token 构造步骤：

1. 拼接 query string：`user_name=<账号>&password=<明文密码>`
2. 对结果进行 Base64 编码

示例：`user_name=jk&password=123456` → `dXNlcl9uYW1lPWprJnBhc3N3b3JkPTEyMzQ1Ng==`

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 用户信息对象 |
| ∟ userName | string | 用户名 |
| ∟ groupName | string | 用户组名称（当前固定为 `""`） |
| ∟ roles | array | 当前 project 下的角色列表 |
| &nbsp;&nbsp;∟ name | string | 角色名称 |
| &nbsp;&nbsp;∟ level | int | 角色等级 |
| &nbsp;&nbsp;∟ memo | string | 角色说明（Unicode 编码） |
| &nbsp;&nbsp;∟ project_id | string | 所属项目 |
| ∟ admin | int | 是否管理员（0/1） |
| ∟ project_id | string | 当前项目 ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户未登录（token 为空且 session 无用户） |
| 1002 | token 解析失败 / 用户不存在 / 密码错误 |

## 请求示例

```json
{
  "timestamp": "TRACE_1709991728857",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/system/login_user_with_token",
  "traceId": "TRACE_1709991728857",
  "body": {
    "token": "dXNlcl9uYW1lPWprJnBhc3N3b3JkPTEyMzQ1Ng=="
  }
}
```

或不传 token 仅查会话状态：

```json
{
  "body": { "token": "" }
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "admin": 1,
    "groupName": "",
    "project_id": "philipine",
    "roles": [
      {
        "level": 1,
        "memo": "u4f9bu5e94u94feu7ba1u7406",
        "name": "supply",
        "project_id": "philipine"
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
  "result": 1002,
  "resultMsg": "用户不存在或者密码异常",
  "traceId": 1709991728857
}
```

## 业务逻辑说明

1. 若 `token` 为空或不传，调用 `_get_login_user_info()` 返回当前 session 用户信息
2. 若 `token` 非空：
   - `codec_util.base64_decode(token)` 解码
   - `parse_url_query_string` 解析为 dict 并提取 `user_name`、`password`
   - SHA256 加密 password
   - 调用 `backend.get_user(user_name)` 比对
   - 通过则写 session（`user_name`、`project_id`），返回用户信息

## 关联

- 数据表：[t_user_info](../../../data-model/design/t_user_info.md)
- 模块 spec：[system_module_spec.md](../../../system_module_spec.md)
- 业务文档：[docs/erp_api/system/login_user_with_token.md](../../../../../docs/erp_api/system/login_user_with_token.md)
- 兄弟接口：[login_user](./login_user.md)、[get_login_user_info](./get_login_user_info.md)

## 注意事项

- token 中 `password` 是明文，传输前需保证 HTTPS 通道
- 通常用于：第三方系统跳转单点登录
- 登录成功后会建立 Flask Session

## Change-Log

### 初始版本 - Token 登录接口创建

**变更类型**：新增接口

**变更原因**：支持外部系统跳转登录与已登录态回查。

**变更内容**：
- 新增 `POST /erp_api/system/login_user_with_token`
- 支持空 token 用于会话回查

**前端影响**：登录跳转流程使用此接口。

**回滚方式**：不允许回滚。

**关联代码改动**：
- handler：[ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `login_user_with_token`
- 数据表：[t_user_info](../../../data-model/design/t_user_info.md)
