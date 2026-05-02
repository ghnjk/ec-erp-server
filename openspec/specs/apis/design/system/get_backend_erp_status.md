# 获取后端 ERP 登录状态

## 接口信息

- **接口路径**: `/erp_api/system/get_backend_erp_status`
- **请求方法**: POST
- **接口描述**: 获取当前后端 seller ERP 集成状态，包括平台类型、配置邮箱、仓库 ID 与登录态
- **权限要求**: 无（仅需登录态）
- **Handler**: [ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `get_backend_erp_status`

## 请求参数

无（依赖 session 与后端 `application.json` 配置）

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | ERP 状态对象 |
| ∟ erp_type | string | ERP 类型：`big_seller` 或 `up_seller` |
| ∟ email | string | 当前 ERP 配置邮箱 |
| ∟ warehouse_id | string | 当前 ERP 仓库 ID（字符串，避免长整型精度问题） |
| ∟ is_login | bool | 后端 ERP 当前是否已登录 |
| ∟ auto_login | bool | 本次状态检查是否允许自动登录 |
| ∟ message | string | 登录态检查结果或错误摘要 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户未登录（session 无 `user_name`） |

## 请求示例

```json
{
  "timestamp": "TRACE_1709991728857",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/system/get_backend_erp_status",
  "traceId": "TRACE_1709991728857",
  "body": {}
}
```

## 响应示例

### BigSeller 成功响应

```json
{
  "data": {
    "erp_type": "big_seller",
    "email": "seller@example.com",
    "warehouse_id": "34324",
    "is_login": true,
    "auto_login": true,
    "message": "big_seller login ok"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857
}
```

### UpSeller cookie 失效响应

```json
{
  "data": {
    "erp_type": "up_seller",
    "email": "seller@example.com",
    "warehouse_id": "19482246679281859",
    "is_login": false,
    "auto_login": false,
    "message": "up_seller cookie 已失效"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857
}
```

### 未登录错误响应

```json
{
  "result": 1001,
  "resultMsg": "not login.",
  "traceId": 1709991728857
}
```

## 业务逻辑说明

1. 校验当前 Flask session 是否存在登录用户；未登录返回 1001。
2. 调用 `seller_util.query_seller_status()`。
3. 当 `use_up_seller=false` 时，构造 BigSeller client 并调用 `login()`，允许复用 cookie 或自动账号密码登录。
4. 当 `use_up_seller=true` 时，构造 UpSeller client，仅 `load_cookies()` 后调用 `is_login()`，不调用 `login()`。
5. 返回 ERP 类型、邮箱、仓库 ID、登录态、自动登录标记与结果消息。

## 关联

- 状态 helper：[ec_erp_api/common/seller_util.py](../../../../../ec_erp_api/common/seller_util.py) `query_seller_status`
- 模块 spec：[system_module_spec.md](../../../system_module_spec.md)
- 业务文档：[docs/erp_api/system/get_backend_erp_status.md](../../../../../docs/erp_api/system/get_backend_erp_status.md)

## 注意事项

- 不返回密码、token、cookie 等敏感信息。
- BigSeller 状态检查可能触发自动登录，接口耗时受验证码识别与网络影响。
- UpSeller 状态检查不会自动登录，cookie 失效时需通过 `tools/up_seller_selenium_cookie.py` 重新保存 cookie。

## Change-Log

### 2026-05-02 - 新增后端 ERP 登录状态接口

**变更类型**：新增接口

**变更原因**：巴西项目切换 UpSeller 后，需要前端和运维能够查询后端 ERP 集成状态。

**变更内容**：
- 新增 `POST /erp_api/system/get_backend_erp_status`
- 返回 ERP 类型、配置邮箱、仓库 ID、登录态、自动登录标记与状态消息
- BigSeller 允许自动登录，UpSeller 只检查 cookie

**前端影响**：可新增状态展示或运维检查入口；现有接口不受影响。

**回滚方式**：删除新增路由与文档即可，不涉及数据迁移。

**关联代码改动**：
- handler：[ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `get_backend_erp_status`
- helper：[ec_erp_api/common/seller_util.py](../../../../../ec_erp_api/common/seller_util.py) `query_seller_status`
