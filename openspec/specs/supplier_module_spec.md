# Supplier 模块规约（供应商/SKU/采购）

## 模块概述

Supplier 模块提供供应商管理、SKU 主数据管理、SKU 采购价格、采购订单全流程管理。

- 文件：[ec_erp_api/apis/supplier.py](../../ec_erp_api/apis/supplier.py)
- Blueprint：`supplier_apis`
- url_prefix：`/erp_api/supplier`
- 权限：`PMS_SUPPLIER` (`"supply"`)，管理员放行

## 接口清单（10 个）

每个接口的详细字段、示例与 Change-Log 见 [apis/design/supplier/](./apis/design/supplier/)。接口规约与变更管理流程见 [apis/spec.md](./apis/spec.md)。

| 路径 | 函数 | 主要数据表 | Design |
| ---- | ---- | ---------- | ------ |
| `/erp_api/supplier/search_supplier` | `search_supplier` | t_supplier_info | [search_supplier.md](./apis/design/supplier/search_supplier.md) |
| `/erp_api/supplier/search_sku` | `search_sku` | t_sku_info | [search_sku.md](./apis/design/supplier/search_sku.md) |
| `/erp_api/supplier/save_sku` | `save_sku` | t_sku_info | [save_sku.md](./apis/design/supplier/save_sku.md) |
| `/erp_api/supplier/add_sku` | `add_sku` | t_sku_info | [add_sku.md](./apis/design/supplier/add_sku.md) |
| `/erp_api/supplier/sync_all_sku` | `sync_all_sku` | t_sku_info | [sync_all_sku.md](./apis/design/supplier/sync_all_sku.md) |
| `/erp_api/supplier/search_sku_purchase_price` | `search_sku_purchase_price` | t_sku_purchase_price | [search_sku_purchase_price.md](./apis/design/supplier/search_sku_purchase_price.md) |
| `/erp_api/supplier/query_sku_purchase_price` | `query_sku_purchase_price` | t_sku_purchase_price | [query_sku_purchase_price.md](./apis/design/supplier/query_sku_purchase_price.md) |
| `/erp_api/supplier/search_purchase_order` | `search_purchase_order` | t_purchase_order | [search_purchase_order.md](./apis/design/supplier/search_purchase_order.md) |
| `/erp_api/supplier/save_purchase_order` | `save_purchase_order` | t_purchase_order | [save_purchase_order.md](./apis/design/supplier/save_purchase_order.md) |
| `/erp_api/supplier/submit_purchase_order_and_next_step` | `submit_purchase_order_and_next_step` | t_purchase_order | [submit_purchase_order_and_next_step.md](./apis/design/supplier/submit_purchase_order_and_next_step.md) |

## 接口定义

### 1. `search_supplier`

- 参数：`current_page` (int)，`page_size` (int)
- 调用：`backend.search_suppliers(offset, page_size)`
- 返回：`pack_pagination_result(total, list<SupplierDto>)`

### 2. `search_sku`

- 参数：
  - `sku` (string, 可空)
  - `sku_group` (string, 可空)
  - `sku_name` (string, 可空)
  - `inventory_support_days` (int, 默认 0)
  - `sort` (任意，可为列表)
  - `current_page` (int)，`page_size` (int)
- 调用：`backend.search_sku(sku_group, sku_name, sku, offset, page_size, inventory_support_days, sort_types)`
- 返回：`pack_pagination_result(total, list<SkuDto>)`

### 3. `save_sku`

- 参数：
  - `sku` (string, 必填)
  - `sku_group` (string)、`sku_name` (string)、`sku_unit_name` (string)
  - `sku_unit_quantity` (int)、`avg_sell_quantity` (int)、`shipping_stock_quantity` (int)、`inventory_support_days` (int)
  - `sku_pack_length` (int, 可选, 默认 0)、`sku_pack_width` (int, 可选, 默认 0)、`sku_pack_height` (int, 可选, 默认 0)：每个采购单位的打包尺寸（cm）
- 业务：通过 `SkuManager` + `BigSellerClient` 查询 ERP SKU、库存，构造 `SkuDto` 后落库
- 返回：`pack_response(DtoUtil.to_dict(s))`

### 4. `add_sku`

- 参数：`skus` (string, 必填)：多行 SKU 文本
- 业务：批量补充 SKU 主数据，对每个 sku 执行 ERP 查询并写入数据库
- 返回：`pack_response({success_count, ignore_count, fail_count, detail})`

### 5. `sync_all_sku`

- 参数：无
- 业务：触发全量同步本地 SKU 主数据库（依赖 BigSellerClient + SkuManager）
- 返回：`pack_response({update_count, fail_count})`

### 6. `search_sku_purchase_price`

- 参数：`current_page` (int)，`page_size` (int)
- 调用：`backend.search_sku_purchase_price(offset, page_size)`
- 返回：`pack_pagination_result(total, list<SkuPurchasePriceDto>)`

### 7. `query_sku_purchase_price`

- 参数：`supplier_id` (int)，`sku` (string)
- 业务：查询特定供应商的特定 SKU 单价（无记录则单价 0）
- 返回：`pack_response({unit_price})`

### 8. `search_purchase_order`

- 参数：
  - `order_type` (int, **必填**, 取值 1 或 2)
  - `current_page`、`page_size`
- 业务：分页查询采购单，按 `order_type` 过滤
- 错误码：`1003` 参数非法

### 9. `save_purchase_order`

- 参数：见下方 **采购单 Body 结构**
- 业务：保存采购单（草稿态或当前步骤），不切换状态
- 返回：`pack_response({})`

### 10. `submit_purchase_order_and_next_step`

- 参数：见下方 **采购单 Body 结构**
- 业务：在保存基础上推进 `purchase_step` 状态机：
  - `order_type==1`（境内进货）走 `_submit_purchase_order_type1`
  - `order_type==2`（境外线下）走 `_submit_purchase_order_type2`，可能触发 `sync_stock_to_erp`（入库）/`sync_stock_out_to_erp`（出库）
- 错误码：`1003`（参数）/`1004`（状态非法）/`1008`（业务异常）

## 采购单 Body 结构（save / submit 共用）

由 `build_purchase_order_from_req()` 解析：

| 字段 | 类型 | 必填 | 说明 |
| ---- | ---- | ---- | ---- |
| `order_type` | int | 是 | 1=境内进货采购单；2=境外线下采购单 |
| `purchase_order_id` | int | 修改时必填 | 不存在时新建（DB autoincrement） |
| `supplier_id` | int | `order_type==1` 必填 | type=2 时固定为 10000000（线下销售） |
| `purchase_step` | string | 是 | 状态见下文 |
| `pay_amount` | int | 否 | 已付金额（**单位：分**），默认 0 |
| `pay_state` | int | 否 | 支付状态，默认 0 |
| `purchase_date` | string | 否 | 采购日期（YYYY-MM-DD） |
| `expect_arrive_warehouse_date` | string | 否 | 预计到仓日期 |
| `maritime_port` | string | 否 | 海运港口 |
| `shipping_company` | string | 否 | 物流商 |
| `shipping_fee` | string | 否 | 物流费 |
| `arrive_warehouse_date` | string | 否 | 实际到仓日期 |
| `remark` | string | 否 | 备注 |
| `purchase_skus` | array | 否 | 列表项 `{sku, unit_price, quantity}` |
| `store_skus` | array | 否 | 列表项 `{sku, unit_price, quantity, check_in_quantity}` |

数量字段 `quantity` 在保存时若非空会被 `int(...)` 转换。

## 采购单状态机（`purchase_step`）

```
草稿 → 供应商捡货中 → 待发货 → 海运中 → 已入库 → 完成
```

每次状态推进由 `submit_purchase_order_and_next_step` 触发：

```mermaid
flowchart LR
    Draft[草稿]
    SupplierPicking[供应商捡货中]
    WaitShip[待发货]
    Shipping[海运中]
    Stored[已入库]
    Done[完成]

    Draft --> SupplierPicking
    SupplierPicking --> WaitShip
    WaitShip --> Shipping
    Shipping --> Stored
    Stored --> Done
```

## 错误码

| 错误码 | 含义 |
| ------ | ---- |
| 1003 | 参数错误 |
| 1004 | 状态机校验失败（如不能跳过中间步骤） |
| 1008 | 业务执行失败（DB 异常、第三方异常等） |

## 与 BigSeller 的交互

- `save_sku`、`add_sku`、`sync_all_sku` 通过 `big_seller_util.build_big_seller_client()` 获取 `BigSellerClient` 单例（300s 缓存，超时重新登录）
- `submit_purchase_order_and_next_step` 在 `order_type==2` 状态推进到入库时调用 `add_stock_to_erp`、出库时调用 BigSeller 库存出库

## 注意事项

- **金额单位**：`unit_price` 在 `t_sku_purchase_price` 与 `t_purchase_order.sku_amount/pay_amount` 中均为 **整数（分）**
- 保存采购单时不严格校验 SKU 是否存在 / 数量为正，业务校验在 `submit` 时进行
- `purchase_skus` 与 `store_skus` 的差异：前者为采购单中的 SKU 计划，后者为实际入库 SKU（可能因供应商替换而不同）
