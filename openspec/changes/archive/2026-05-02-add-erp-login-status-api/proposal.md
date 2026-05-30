## Why

巴西项目切换到 UpSeller 后，后端 ERP 集成状态不再只等价于 BigSeller 自动登录状态。运维和前端需要一个轻量接口确认当前项目使用的 ERP 平台、登录态、账号邮箱和仓库 ID，便于发现 cookie 失效或配置错误。

## What Changes

- 新增系统接口，用于返回后端 seller ERP 集成基础状态。
- 接口返回当前 seller 平台类型（BigSeller / UpSeller）、基础账号邮箱、仓库 ID、是否已登录，以及登录检查信息。
- BigSeller 路径检查状态时允许自动登录，复用现有 cookie 和账号密码登录机制。
- UpSeller 路径检查状态时不自动登录，只读取现有 cookie 判断登录态，避免触发 selenium/人工验证码流程。
- 未引入破坏性变更，现有登录用户信息接口保持不变。

## Capabilities

### New Capabilities
- `erp-login-status`: 获取后端 seller ERP 集成状态、账号邮箱和仓库 ID 信息。

### Modified Capabilities
- `apis`: system 模块新增一个后端 ERP 登录状态查询接口。

## Impact

- 影响 `ec_erp_api/apis/system.py`：新增 system API 路由。
- 影响 `ec_erp_api/common/seller_util.py`：补充 seller 状态检测能力，区分 BigSeller 自动登录与 UpSeller 只检查 cookie。
- 影响 `docs/erp_api/`：新增接口文档并更新接口索引。
- 复用现有 `BigSellerClient`、`UpSellerClient`、`application.json` 中的 seller 配置和 cookies 文件。
