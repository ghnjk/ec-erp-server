# UpSeller 人工登录

## 接口信息

- **接口路径**: `/erp_api/system/up_seller_manual_login`
- **请求方法**: POST
- **接口描述**: 调用 `tools/up_seller_cookie.py` 完成 UpSeller 协议登录；支持两阶段（发码 / 带邮箱验证码登录），返回完整脚本日志与登录状态
- **权限要求**: 无（仅需登录态）；且后台须启用 `use_up_seller=true`
- **Handler**: [ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `up_seller_manual_login`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| email_code | string | 否 | 邮箱二次校验验证码；不传表示第一阶段（尝试登录并在需要时发码） |

依赖 session 与后端 `application.json` 配置：`ydm_token`、`up_seller.mail`、`up_seller.password`、`cookies_dir`。

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 登录结果 |
| ∟ login_status | string | `logged_in` / `need_email_code` / `failed` |
| ∟ logs | string | 子进程 stdout+stderr 全文 |
| ∟ exit_code | int | 脚本退出码；超时为 `-1` |
| ∟ message | string | 简短说明 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户未登录（session 无 `user_name`） |
| 1003 | 参数/业务错误（非 UpSeller 环境、缺少配置、脚本不存在等） |

## 请求示例

### 第一阶段（发码 / 尝试登录）

```json
{
  "timestamp": "TRACE_1709991728857",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/system/up_seller_manual_login",
  "traceId": "TRACE_1709991728857",
  "body": {}
}
```

### 第二阶段（提交邮箱验证码）

```json
{
  "timestamp": "TRACE_1709991728857",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/system/up_seller_manual_login",
  "traceId": "TRACE_1709991728857",
  "body": {
    "email_code": "123456"
  }
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
    "logs": "Cookie 文件: ...\n登录成功，cookies 已保存到: ...\n",
    "exit_code": 0,
    "message": "UpSeller 登录成功"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857
}
```

### 非 UpSeller 环境

```json
{
  "result": 1003,
  "resultMsg": "当前环境未启用 UpSeller（use_up_seller != true）",
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

1. 校验 Flask session 登录用户；未登录返回 1001。
2. 调用 `seller_util.run_up_seller_manual_login(email_code)`。
3. 校验 `use_up_seller=true`，并从配置读取邮箱、密码、`ydm_token`、cookie 路径。
4. 使用 **`sys.executable`** 在仓库根目录执行：
   `tools/up_seller_cookie.py --email ... --password ... --ydm-token ... --cookie-file ... --force [--email-code ...]`
5. 按退出码映射 `login_status`：`0→logged_in`，`2→need_email_code`，其它→`failed`；超时按 `failed`（`exit_code=-1`）。
6. 返回完整日志与状态，供前端人工登录页展示。

## 关联

- helper：[ec_erp_api/common/seller_util.py](../../../../../ec_erp_api/common/seller_util.py) `run_up_seller_manual_login`
- 登录脚本：[tools/up_seller_cookie.py](../../../../../tools/up_seller_cookie.py)
- 业务文档：[docs/erp_api/system/up_seller_manual_login.md](../../../../../docs/erp_api/system/up_seller_manual_login.md)

## 注意事项

- 不返回密码、token、cookie 明文配置；日志中脚本自身可能打印账号邮箱，前端按运维查看用途展示。
- 接口可能较慢（验证码识别 + 腾讯/Turnstile），建议前端超时不低于 5 分钟；后端子进程超时 300 秒。
- 仅 UpSeller 环境可用；BigSeller 请勿调用本接口。

## Change-Log

### 2026-07-12 - 新增 UpSeller 人工登录接口

**变更类型**：新增接口

**变更原因**：UpSeller 不支持状态接口自动登录，需提供人工触发协议登录（含邮箱二次校验）的运维入口。

**变更内容**：
- 新增 `POST /erp_api/system/up_seller_manual_login`
- 子进程调用 `tools/up_seller_cookie.py`，返回 `login_status` / `logs` / `exit_code`

**前端影响**：Header 增加「人工登陆」入口，新增页面 `UpSellerManualLogin`。

**回滚方式**：删除新增路由、helper 与文档即可，不涉及数据迁移。

**关联代码改动**：
- handler：[ec_erp_api/apis/system.py](../../../../../ec_erp_api/apis/system.py) `up_seller_manual_login`
- helper：[ec_erp_api/common/seller_util.py](../../../../../ec_erp_api/common/seller_util.py) `run_up_seller_manual_login`
