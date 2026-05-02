# UpSeller Web 接口调研

调研入口：`https://app.upseller.com/zh-CN/home`

UpSeller 与 BigSeller 的 Web 接口思路相似：前端通过 cookie 维持登录态，业务接口集中在 `https://app.upseller.com/api/...`，普通业务请求大多是 JSON POST。与 BigSeller 最大差异是登录提交：UpSeller 前端会把登录表单整体加密后，以 `application/x-www-form-urlencoded` 的 `body` 字段提交。

## 1. 登录

### 页面

- 登录页：`GET /zh-CN/login`
- 首页：`GET /zh-CN/home`
- 前端静态资源：`https://cdn.upseller.cn/us-web/2026-04/...`

### 登录态检查

- URL：`GET /api/is-login`
- 请求参数：`reqTime` 可选，前端有封装但实测不传也可返回。
- 未登录响应：

```json
{
  "code": 0,
  "msg": "success",
  "data": false,
  "version": "6.8.1",
  "extraInfo": null
}
```

### 用户信息

- URL：`GET /api/user-info`
- 未登录响应：`code=2001, msg=validated.failed`
- 登录后用于确认用户、权限、店铺等信息。

### 国家判断

- URL：`GET /api/getCountryCode`
- 响应示例：`{"code":0,"msg":"success","data":"CN"}`
- 前端逻辑：`CN` 会走腾讯云验证码，非 `CN` 会走 Cloudflare Turnstile；国家只影响人机验证 token，不影响当前 `app.upseller.com` 的 `body` 加密 key。

### 图片验证码

- URL：`GET /api/vcode?email={email}&t={timestamp}`
- 响应：`data:image/jpg;base64,...`
- 可用 `ec.verifycode.YdmVerify.common_verify(image_base64, "10110")` 识别 4 位数英验证码。

### 登录提交

- URL：`POST /api/login`
- Content-Type：`application/x-www-form-urlencoded`
- 请求体：`body={encrypted_text}`
- 前端原始表单在加密前大致为：

```json
{
  "email": "邮箱",
  "password": "前端加密后的密码字段",
  "vcode": "图片验证码",
  "remember": 1,
  "timeStamper": 1710000000000,
  "deviceId": "浏览器设备 ID",
  "token": "TencentCaptcha ticket 或 Cloudflare token",
  "randStr": "TencentCaptcha randstr，非 CN 场景为空"
}
```

#### body 加密算法

通过反编译 `bundle.index.*.js` 模块 89907 与 `bundle.login.*.js` 中 `doLogin`，
确认前端 `c.S(...)` 函数对应：

- 算法：AES-256-ECB + PKCS7 + Base64
- 密钥（32 字节 UTF-8 串）：当前 `app.upseller.com` / `app.upseller.cn` 登录页使用 `2Y4Mgj$hwJV6qa62z64#b2!HkLz2pP5g`；旧的非 app 域名分支才会走 `Y6MxcOCNj5Pjx$@rwMW6VNVa8fYVOTR&`
- 拼接规则：`c.S(t, e)` 把非空参数用字面量 `±±` (UTF-8 `0xC2 0xB1 0xC2 0xB1`) 连接后再加密

登录提交分两步：

1. `password` 字段：`c.S(原密码, timeStamper)` —— 加密 `"原密码±±时间戳"`，与外层 payload 的 `timeStamper` 保持一致
2. `merged_payload` 字段顺序来自 `Object.assign({}, formData, {}, overrides)`，即 `email,password,vcode,remember,token,randStr,timeStamper,deviceId`
3. `body` 字段：`c.S(JSON.stringify(merged_payload))` —— 整体 JSON 再做一次加密

`UpSellerClient.login()` 默认使用 `build_default_login_body_encoder()` 完成上述两步加密；
当 `getCountryCode` 返回 CN 时仍需注入 TencentCaptcha token/randStr。
如需走自定义加密通路，可在构造 `UpSellerClient` 时通过 `login_body_encoder=` 注入。

## 2. SKU 信息查询

### SKU 列表（单 SKU / KIT）

- URL：`POST /api/sku/index-single`
- 请求方式：JSON POST
- 前端列表页：`/zh-CN/products/product-list`
- 常用请求参数：

```json
{
  "pageNum": 1,
  "pageSize": 50,
  "sortName": null,
  "sortValue": null,
  "searchGroup": 1,
  "searchType": "1",
  "searchValue": "SKU 或别名",
  "catalogIds": null,
  "mappingStatus": null,
  "stockStatus": null,
  "saleStatus": null
}
```

- `searchGroup=1`：全部单 SKU/KIT 入口使用。
- `searchGroup=0,isSingle=1`：前端“单 SKU”页签。
- `searchGroup=2`：前端“KIT”页签。
- 搜索类型：
  - `1`：SKU / SKU Alias
  - `2`：Product Name
  - `3`：Number
  - `4`：Store SKU
  - `5`：Barcode
  - `6`：Store Product ID
  - `7`：SPU
  - `8`：Variant ID

### 多变体 SKU 列表

- URL：`POST /api/sku/index-variants`
- 参数与 `/api/sku/index-single` 基本一致。

### SKU 详情

- 单 SKU：`POST /api/sku/detail-single`
- 多变体 SPU：`POST /api/sku/detail-spu`
- KIT：`POST /api/sku/detail-group`
- 请求体：

```json
{
  "id": "前端列表返回的 idStr 或 id"
}
```

### SKU 关联/映射参考接口

- `GET /api/sku/sku-relation-detail?skuId={idStr}`
- `POST /api/product-map-sku/index`
- `POST /api/product-map-sku/map`
- `POST /api/product-map-sku/unmap`

本次 client 只落 SKU 查询和详情，映射接口暂不实现。

## 3. SKU 库存

### 仓库列表

- 全量仓库：`POST /api/warehouse/index`
- 可用仓库：`POST /api/warehouse/list-enable`
- 3PL 仓库：`GET /api/warehouse/tpl-list`

### 库存列表

- URL：`POST /api/warehouse-sku/list`
- 前端列表页：`/zh-CN/inventory/list`
- 常用请求参数：

```json
{
  "pageNum": 1,
  "pageSize": 50,
  "warehouseId": "仓库 ID",
  "searchType": "1",
  "searchValue": "SKU",
  "catalogIds": null,
  "stockStatusList": null,
  "saleStatus": null,
  "sortName": null,
  "sortValue": null
}
```

- 库存搜索类型：
  - `1`：SKU
  - `2`：Product Name
  - `3`：Shelf No
  - `4`：Barcode
  - `8`：3PL Code

### 单 SKU 仓库库存

- URL：`POST /api/warehouse-sku/one-sku`
- 请求体：

```json
{
  "id": "SKU id 或 idStr"
}
```

用于查询某个 SKU 在各仓库下的库存/可用库存。

### 手动入库/出库

- 入库保存：`POST /api/warehouse-inout-list/add-in`
- 入库提交审核：`POST /api/warehouse-inout-list/add-in-to-examine`
- 出库保存：`POST /api/warehouse-inout-list/add-out`
- 出库提交审核：`POST /api/warehouse-inout-list/add-out-to-examine`
- 入库单列表：`POST /api/warehouse-inout-list/in-list`
- 出库单列表：`POST /api/warehouse-inout-list/out-list`
- 入出库详情：`POST /api/warehouse-inout-list/get-inout-detail`

前端入出库列表常见筛选参数：

```json
{
  "pageNum": 1,
  "pageSize": 50,
  "warehouseId": "仓库 ID",
  "inoutClass": null,
  "searchType": "1",
  "searchValue": "SKU",
  "inoutType": "in"
}
```

入库保存的字段需要以后用真实页面提交再补齐；当前 `UpSellerClient.add_stock_to_erp(req)` 保持透传，方便用抓包确认后的请求体直接调用。

## 4. Python Client 对应方法

- `login(email, password)`：优先复用 cookie；无 cookie 时识别图片验证码，并使用默认 `build_default_login_body_encoder()`（AES-256-ECB/PKCS7+Base64）完成前端 `body` 加密；CN 场景仍需注入 TencentCaptcha token/randStr。
- `is_login()`：调用 `/api/is-login`。
- `get_user_info()`：调用 `/api/user-info`。
- `load_all_sku()`：分页调用 `/api/sku/index-single`。
- `query_sku_page()`：SKU 列表通用查询。
- `query_sku_detail()`：按 `single/spu/group` 调详情接口。
- `query_warehouse_list()`：仓库列表。
- `query_sku_inventory_page()`：库存列表通用查询。
- `query_sku_inventory_detail()`：按 SKU + 仓库查库存行。
- `query_product_warehouse_list()`：查 SKU 仓库库存分布。
- `add_stock_to_erp()` / `out_stock_from_erp()`：入库/出库请求体透传。
