## Context

`system.py` 目前只暴露用户登录与登录用户信息接口，无法从后端判断当前项目接入的 seller ERP 是否可用。此前默认依赖 BigSeller，supplier/warehouse 等模块会在业务调用时自动登录；巴西项目切换到 UpSeller 后，UpSeller 登录通常依赖人工维护 cookie 或 selenium，状态查询接口如果触发自动登录会带来浏览器弹窗、验证码和阻塞风险。

本变更基于现有 `use_up_seller` 配置和 `seller_util` 抽象层补充一个只读状态查询接口。接口属于 system 模块，遵循现有 `@api_post_request()` 响应包装，不新增数据库表，不改变用户登录态。

## Goals / Non-Goals

**Goals:**
- 在 system 模块新增 POST API 返回后端 seller ERP 的平台类型、配置邮箱、仓库 ID 和登录状态。
- BigSeller 状态检查允许自动登录，保持历史行为：cookie 可用则复用，cookie 失效则账号密码登录。
- UpSeller 状态检查只加载 cookie 并调用 `/api/is-login`，不触发 `UpSellerClient.login()`，避免自动 selenium/验证码流程。
- 状态查询失败时仍返回结构化结果，便于前端或运维展示错误原因。

**Non-Goals:**
- 不实现 UpSeller 自动登录、刷新 cookie 或人工登录流程。
- 不暴露密码、token、cookie 内容等敏感信息。
- 不修改 supplier/warehouse/sale 业务接口的行为。
- 不新增前端页面，只定义后端接口契约。

## Decisions

1. **新增 system API 而不是复用 `get_login_user_info`**

   `get_login_user_info` 是用户会话接口，混入 ERP 状态会改变现有响应结构并增加第三方调用耗时。新增 `/erp_api/system/get_backend_erp_status` 可以保持职责单一，也便于前端按需调用。

2. **状态检测逻辑放在 `seller_util`**

   `seller_util` 已经负责 BigSeller / UpSeller 的配置分支和 client 构造。新增一个只读 helper（如 `query_seller_status(auto_login_big_seller=True)`）可以复用配置解析，避免 `system.py` 直接理解 cookies 路径和不同 client 构造细节。

3. **BigSeller 使用自动登录，UpSeller 只检查 cookie**

   BigSeller 的自动登录已是现有后端调用模式，状态接口触发登录符合历史预期。UpSeller 登录会依赖 selenium/验证码/人工 cookie，状态接口必须只执行 `load_cookies()` + `is_login()`，不能调用 `login()`，否则会把一个只读状态接口变成可能阻塞的登录流程。

4. **响应返回配置邮箱和仓库 ID，但不返回敏感凭证**

   响应包含 `erp_type`、`email`、`warehouse_id`、`is_login`、`auto_login`、`message` 等字段。邮箱和仓库 ID 来自配置，属于运维可见基础信息；密码、ydm token、cookie 内容绝不返回。

5. **异常转换为业务状态而不是抛到装饰器**

   登录态检查依赖外部网络，失败时更适合返回 `is_login=false` 和错误消息，避免接口整体变成系统异常。只有配置缺失等不可恢复错误才返回明确错误码或消息。

## Risks / Trade-offs

- **BigSeller 自动登录可能增加接口耗时** → 状态接口只在显式调用时执行；可复用已有 cookie，失败时返回错误信息。
- **UpSeller cookie 过期时接口无法修复登录态** → 这是刻意约束，响应中返回 `is_login=false` 和提示，由运维执行 `tools/up_seller_selenium_cookie.py` 更新 cookie。
- **外部网络失败导致状态误判** → 响应 `message` 保留异常摘要，前端可展示为“检查失败”而不是“配置缺失”。
- **仓库 ID 类型在 UpSeller 为长整数字符串** → 响应统一以字符串返回 `warehouse_id`，避免 JavaScript 精度问题。
