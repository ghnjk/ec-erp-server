# UpSeller 人工登录

## 接口信息

- **接口路径**: `/erp_api/system/up_seller_manual_login`
- **请求方法**: POST
- **接口描述**: 调用 `tools/up_seller_cookie.py` 完成 UpSeller 协议登录；支持两阶段（发码 / 带邮箱验证码登录），返回完整脚本日志与登录状态
- **权限要求**: 需要 ERP 用户登录态；且后台须启用 `use_up_seller=true`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| email_code | string | 否 | 邮箱二次校验验证码；不传表示第一阶段 |

账号、密码、云码 token、cookie 路径均从后端 `application.json` 读取，前端无需也不应传入。

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功，其他表示失败 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 登录结果 |
| ∟ login_status | string | `logged_in` / `need_email_code` / `failed` |
| ∟ logs | string | 子进程完整输出 |
| ∟ exit_code | int | 脚本退出码；超时为 `-1` |
| ∟ message | string | 简短说明 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户未登录 |
| 1003 | 非 UpSeller 环境、缺少配置或脚本不存在 |

## 请求示例

### 第一阶段

```json
{}
```

### 第二阶段

```json
{
  "email_code": "123456"
}
```

## 响应示例

### 需要邮箱验证码

```json
{
  "data": {
    "login_status": "need_email_code",
    "logs": "Cookie 文件: ...\n需要 email verification code ...\n",
    "exit_code": 2,
    "message": "需要邮箱验证码，请查收邮件后再次提交"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857
}
```

### 登录成功

```json
{
  "data": {
    "login_status": "logged_in",
    "logs": "登录成功，cookies 已保存到: ...\n",
    "exit_code": 0,
    "message": "UpSeller 登录成功"
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
2. 校验 `use_up_seller=true`，否则返回 1003。
3. 使用当前 Python 解释器（`sys.executable`）执行 `tools/up_seller_cookie.py`，固定带 `--force`。
4. 第一阶段不传 `email_code`；若脚本退出码为 2，返回 `need_email_code`。
5. 第二阶段传入 `email_code`，脚本带 `--email-code` 完成二次校验。
6. 退出码 `0` → `logged_in`，其它非 2 → `failed`。

## 注意事项

- 接口耗时可能较长（图片验证码、腾讯/Turnstile），前端超时建议 5 分钟以上。
- 不向客户端返回密码 / token 配置明文。
- 仅用于 UpSeller；BigSeller 请继续使用原有自动登录路径。
