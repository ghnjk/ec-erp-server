# System 模块规约（系统/登录）

## 模块概述

System 模块提供用户认证、登录、用户信息查询等基础能力，是其他业务模块（supplier / warehouse / sale）的访问入口。

- 文件：[ec_erp_api/apis/system.py](../../ec_erp_api/apis/system.py)
- Blueprint：`system_apis`
- url_prefix：`/erp_api/system`

## 接口清单（4 个）

每个接口的详细字段、示例与 Change-Log 见 [apis/design/system/](./apis/design/system/)。接口规约与变更管理流程见 [apis/spec.md](./apis/spec.md)。

| 路径 | 函数 | 说明 | Design |
| ---- | ---- | ---- | ------ |
| `/erp_api/system/login_user_with_token` | `login_user_with_token` | 通过 Token 登录（支持空 Token 仅查 session） | [login_user_with_token.md](./apis/design/system/login_user_with_token.md) |
| `/erp_api/system/login_user` | `login_user` | 账号密码登录 | [login_user.md](./apis/design/system/login_user.md) |
| `/erp_api/system/get_login_user_info` | `get_login_user_info` | 获取已登录用户信息 | [get_login_user_info.md](./apis/design/system/get_login_user_info.md) |
| `/erp_api/system/get_backend_erp_status` | `get_backend_erp_status` | 获取后端 seller ERP 登录状态与基础配置 | [get_backend_erp_status.md](./apis/design/system/get_backend_erp_status.md) |

## 接口定义

### 1. `/erp_api/system/login_user_with_token`

- **HTTP**：POST
- **装饰器**：`@api_post_request()`
- **参数**（来自 `body`）：
  - `token` (string, **可选**)：Base64 编码的 URL query 字符串，解码后必须包含 `user_name` 与 `password`。空字符串或未传时退化为查询当前 session 用户。
- **业务逻辑**：
  1. 若 `token` 非空：`base64_decode → parse_url_query_string` 提取 `user_name`/`password`
  2. `password` 经 `calc_sha256` 后与 `t_user_info.Fpassword` 比对
  3. 通过：写入 `session["user_name"]` 与 `session["project_id"]`（取自 `default_project_id`）
  4. 调用 `_get_login_user_info()` 返回用户信息
- **错误码**：
  - `1001` 未登录或异常
  - `1002` 账号或密码错误

### 2. `/erp_api/system/login_user`

- **HTTP**：POST
- **装饰器**：`@api_post_request()`
- **参数**：
  - `account` (string, **必填**)：用户名（注意 body 字段名为 `account`，**不是** `user_name`）
  - `password` (string, **必填**)：明文密码（服务端 SHA256 后比对）
- **业务逻辑**：与 `login_user_with_token` 校验流程一致；成功后写 session 并返回用户信息。
- **错误码**：`1002` 账号密码错误

### 3. `/erp_api/system/get_login_user_info`

- **HTTP**：POST
- **装饰器**：`@api_post_request()`
- **参数**：无业务参数（依赖 session）
- **业务逻辑**：调用 `_get_login_user_info()`，session 中无 `user_name` 则返回 1001。
- **响应数据示例**：

```json
{
  "user_name": "alice",
  "default_project_id": "philipine",
  "is_admin": 0,
  "roles": [
    { "project_id": "philipine", "role_list": [{"name": "supply"}, {"name": "warehouse"}] }
  ]
}
```

### 4. `/erp_api/system/get_backend_erp_status`

- **HTTP**：POST
- **装饰器**：`@api_post_request()`
- **参数**：无业务参数（依赖 session 与后端配置）
- **业务逻辑**：session 中无 `user_name` 时返回 1001；登录后调用 `seller_util.query_seller_status()` 查询 seller ERP 状态。BigSeller 路径允许自动登录，UpSeller 路径只检查 cookie。
- **响应数据示例**：

```json
{
  "erp_type": "up_seller",
  "email": "seller@example.com",
  "warehouse_id": "19482246679281859",
  "is_login": true,
  "auto_login": false,
  "message": "up_seller cookie login ok"
}
```

## 认证与会话约定

- 登录后 Flask Session 保存 `user_name` 与 `project_id`（缺省 `dev`）
- 用户密码使用 `calc_sha256` 加密后存入 `t_user_info.Fpassword`
- Session 加密 Key 来自 `application.json:session_secret_key`
- 前端通过 `account` + `password` 调用 `login_user`，或通过 Base64 token 调用 `login_user_with_token`

## 用户角色与权限

`UserDto.roles` 字段为 JSON 列表，结构示例：

```json
[
  {
    "project_id": "philipine",
    "role_list": [
      {"name": "supply"},
      {"name": "warehouse"},
      {"name": "sale"}
    ]
  }
]
```

权限常量定义在 [ec_erp_api/common/request_context.py](../../ec_erp_api/common/request_context.py)：

| 常量 | 值 | 用途 |
| ---- | -- | ---- |
| `PMS_SUPPLIER` | `"supply"` | 供应商/SKU/采购模块 |
| `PMS_WAREHOUSE` | `"warehouse"` | 仓库/打印模块 |
| `PMS_SALE` | `"sale"` | 销售模块 |

`validate_user_permission(permission_name)` 校验规则：
1. Session 无 `user_name`：返回 `False`
2. `user.is_admin == True`：直接 `True`
3. 否则在 `roles` 中找到 `project_id == 当前 session project_id` 的 `role_list`，存在 `name == permission_name` 即 `True`

## 业务模块权限对应

| Blueprint | 权限 |
| --------- | ---- |
| `system` | 无需权限校验（仅登录态） |
| `supplier` | `PMS_SUPPLIER` |
| `warehouse` | `PMS_WAREHOUSE` |
| `sale` | `PMS_SALE` |

## 注意事项

- 登录失败次数无限制（业务上无锁定逻辑），密码 SHA256 强度依赖明文复杂度
- session_secret_key 一旦更换，所有用户需重新登录
- 多 project 场景下，用户 `default_project_id` 决定首次登录写入 session 的 `project_id`
