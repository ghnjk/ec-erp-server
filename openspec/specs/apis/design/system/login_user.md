# 用户登录

## 接口信息

- **接口路径**: `/erp_api/system/login_user`
- **请求方法**: POST
- **接口描述**: 通过用户名和密码进行登录
- **权限要求**: 无（登录前调用）
- **Handler**: [ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `login_user`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| account | string | 是 | 用户账号（注意 body 字段名为 `account`，**不是** `user_name`） |
| password | string | 是 | 用户密码（明文，服务端 SHA256 后比对） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0 表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID（透传请求 timestamp） |
| data | object | 用户信息对象 |
| ∟ userName | string | 用户名 |
| ∟ groupName | string | 用户组名称（当前固定为 `""`） |
| ∟ roles | array | 用户角色列表（按当前 project_id 过滤） |
| &nbsp;&nbsp;∟ name | string | 角色名称（supply / warehouse / sale） |
| &nbsp;&nbsp;∟ level | int | 角色等级 |
| &nbsp;&nbsp;∟ memo | string | 角色说明（Unicode 编码） |
| &nbsp;&nbsp;∟ project_id | string | 所属项目 ID |
| ∟ admin | int | 是否管理员，1=是，0=否 |
| ∟ project_id | string | 当前 session 中的项目 ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1002 | 用户不存在或密码错误 |

## 请求示例

```json
{
  "timestamp": "TRACE_1709991728857",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/system/login_user",
  "traceId": "TRACE_1709991728857",
  "body": {
    "account": "jk",
    "password": "123456"
  }
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
      },
      {
        "level": 1,
        "memo": "u4ed3u5e93u7ba1u7406",
        "name": "warehouse",
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

1. 接收用户名（`account`）和明文密码
2. 对密码进行 SHA256 加密 (`codec_util.calc_sha256`)
3. 从数据库查询用户信息 (`backend.get_user`)
4. 验证用户是否存在、是否被逻辑删除、密码是否匹配
5. 校验通过后，在 session 中保存 `user_name` 与 `project_id`（来自 `default_project_id`）
6. 调用内部 `_get_login_user_info()` 返回用户详细信息

## 关联

- 数据表：[t_user_info](../../../data-model/design/t_user_info.md)
- 模块 spec：[system_module_spec.md](../../../system_module_spec.md)
- 业务文档：[docs/erp_api/system/login_user.md](../../../../../docs/erp_api/system/login_user.md)

## 注意事项

- 请求体字段名为 **`account`**，不是 `user_name`
- 前端传入 `password` 为明文，后端进行 SHA256 加密后比对
- 登录成功后建立 Flask Session
- 返回的 `roles` 列表按当前 project_id 过滤
- 角色 `memo` 字段为 Unicode 编码，前端需解码显示

## Change-Log

### 初始版本 - 用户登录接口创建

**变更类型**：新增接口

**变更原因**：建立用户认证基础。

**变更内容**：
- 新增 `POST /erp_api/system/login_user`
- 请求参数：`account`、`password`
- 写入 session：`user_name`、`project_id`

**前端影响**：必须实现登录页面。

**回滚方式**：不允许回滚（核心认证接口）。

**关联代码改动**：
- handler：[ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `login_user`
- 数据表：[t_user_info](../../../data-model/design/t_user_info.md)
- 前端：`ec-erp-static/src/pages/user/loginIndex.vue`
