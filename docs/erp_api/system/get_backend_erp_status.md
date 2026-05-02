# 获取后端 ERP 登录状态

## 接口信息

- **接口路径**: `/erp_api/system/get_backend_erp_status`
- **请求方法**: POST
- **接口描述**: 获取当前后端 seller ERP 集成状态，包括平台类型、配置邮箱、仓库 ID 与登录态

## 请求参数

无需请求参数。

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功，其他表示失败 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | ERP 状态对象 |
| ∟ erp_type | string | ERP 类型：`big_seller` 或 `up_seller` |
| ∟ email | string | 当前 ERP 配置邮箱 |
| ∟ warehouse_id | string | 当前 ERP 仓库 ID |
| ∟ is_login | bool | 后端 ERP 当前是否已登录 |
| ∟ auto_login | bool | 本次状态检查是否允许自动登录 |
| ∟ message | string | 登录态检查结果或错误摘要 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户未登录 |

## 请求示例

```json
{}
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

1. 校验当前 session 是否已登录，未登录返回 1001。
2. 根据 `use_up_seller` 判断当前 ERP 类型。
3. BigSeller：允许调用 `login()` 自动登录，优先复用 cookie。
4. UpSeller：只读取 `up_seller.cookies` 并调用登录态检查，不触发 selenium 登录。
5. 返回平台、邮箱、仓库 ID、登录态、自动登录标记和消息。

## 注意事项

- 不返回密码、token、cookie 等敏感信息。
- `warehouse_id` 统一返回字符串，避免 UpSeller 长整型仓库 ID 在前端精度丢失。
- UpSeller cookie 失效后，需要通过 `tools/up_seller_selenium_cookie.py` 重新保存 cookie。
