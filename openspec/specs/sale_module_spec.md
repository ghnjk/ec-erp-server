# Sale 模块规约（销售管理）

## 模块概述

Sale 模块管理 SKU 销售单价与销售订单，支持向 BigSeller ERP 同步出库。

- 文件：[ec_erp_api/apis/sale.py](../../ec_erp_api/apis/sale.py)
- Blueprint：`sale_apis`
- url_prefix：`/erp_api/sale`
- 权限：`PMS_SALE` (`"sale"`)

## 接口清单（7 个）

每个接口的详细字段、示例与 Change-Log 见 [apis/design/sale/](./apis/design/sale/)。接口规约与变更管理流程见 [apis/spec.md](./apis/spec.md)。

| 路径 | 函数 | 数据表 | Design |
| ---- | ---- | ------ | ------ |
| `/erp_api/sale/save_sku_sale_price` | `save_sku_sale_price` | t_sku_sale_price | [save_sku_sale_price.md](./apis/design/sale/save_sku_sale_price.md) |
| `/erp_api/sale/search_sku_sale_price` | `search_sku_sale_price` | t_sku_sale_price | [search_sku_sale_price.md](./apis/design/sale/search_sku_sale_price.md) |
| `/erp_api/sale/create_sale_order` | `create_sale_order` | t_sale_order | [create_sale_order.md](./apis/design/sale/create_sale_order.md) |
| `/erp_api/sale/update_sale_order` | `update_sale_order` | t_sale_order | [update_sale_order.md](./apis/design/sale/update_sale_order.md) |
| `/erp_api/sale/delete_sale_order` | `delete_sale_order` | t_sale_order | [delete_sale_order.md](./apis/design/sale/delete_sale_order.md) |
| `/erp_api/sale/submit_sale_order` | `submit_sale_order` | t_sale_order + BigSeller | [submit_sale_order.md](./apis/design/sale/submit_sale_order.md) |
| `/erp_api/sale/search_sale_order` | `search_sale_order` | t_sale_order | [search_sale_order.md](./apis/design/sale/search_sale_order.md) |

## 接口定义

### 1. `save_sku_sale_price`

- 参数：
  - `sku` (string, **必填、非空**)
  - `unit_price` (float, **必填且 > 0**)
- 业务：upsert `t_sku_sale_price`
- 返回：`pack_simple_response()`
- 错误码：`1003` 参数错误

### 2. `search_sku_sale_price`

- 参数：
  - `sku` (string, 可空)
  - `current_page` (int, 默认 **1**)
  - `page_size` (int, 默认 **20**)
- 返回：`{total, list: [SkuSalePrice...]}`

### 3. `create_sale_order`

- 参数：
  - `order_date` (string, **必填**, YYYY-MM-DD)
  - `sale_sku_list` (array, **必填、非空数组**)，每项：
    - `sku` (string, 必填)
    - `unit_price` (float, **> 0**)
    - `quantity` (int, **> 0**)
- 业务：构造 `SaleOrder(status=新建)` 写入数据库，自增 `order_id` 返回
- 返回：`pack_simple_response({order_id})`
- 错误码：`1003` 参数错误

### 4. `update_sale_order`

- 参数：
  - `order_id` (int, **必填、有效**)
  - `order_date` (string, 可选)
  - `sale_sku_list` (array, 可选；提供时需为非空数组，且每项校验同 create)
  - `status` (string, 可选)
- 业务：合并字段后 `update_sale_order`
- 返回：`pack_simple_response()`

### 5. `delete_sale_order`

- 参数：`order_id` (int)
- 业务：逻辑删除 `Fis_delete = 1`（不物理删除）
- 返回：`pack_simple_response()`

### 6. `submit_sale_order`

- 参数：`order_id` (int)
- 业务：
  1. 查询订单
  2. 调用 `sync_sale_order_to_erp(order, BigSellerClient)`：将 SKU 出库写入 BigSeller
  3. 成功后将订单 `status` 置为 `已同步`
- 错误码：`1003`～`1008`（参数 / 状态 / BigSeller 异常）

### 7. `search_sale_order`

- 参数：
  - `status` (string, 可空)
  - `begin_date` (string, 可空)
  - `end_date` (string, 可空)
  - `current_page` (int, 默认 1)
  - `page_size` (int, 默认 20)
- 业务：分页查询未删除的销售订单（`is_delete == 0`），`sale_sku_list` 解析为数组返回
- 返回：`{total, list: [SaleOrder...]}`

## 销售订单状态机

```
新建 → 已同步
        ↑
   submit_sale_order
```

`status` 字段为字符串，目前已知值：
- `新建`：通过 `create_sale_order` 创建后默认状态
- `已同步`：调用 `submit_sale_order` 成功后

## 数据表特性

### `t_sku_sale_price`

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `Fproject_id` | string(128) | 项目 ID |
| `Fsku` | string(128) | SKU 编码 |
| `Funit_price` | **float** | 销售单价（**注意：与采购价的"分整型"约定不同，此处为浮点元值**） |
| `Fcreate_time` / `Fmodify_time` | datetime | |

主键：`(Fproject_id, Fsku)`

### `t_sale_order`

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `Forder_id` | int | autoincrement 主键 |
| `Fproject_id` | string(128) | index |
| `Forder_date` | datetime | 订单日期 |
| `Fsale_sku_list` | longtext (utf8mb4_bin) | JSON 序列化 SKU 销售清单 |
| `Ftotal_amount` | float | 订单总额（浮点元值） |
| `Fstatus` | string(128) | 订单状态 |
| `Fis_delete` | int | 0=有效，1=已删除（index） |
| `Fcreate_time` / `Fmodify_time` | datetime | |

> **类型一致性提示**：ORM 对 `Fsale_sku_list` 使用 JSON，SQL 建表使用 `LONGTEXT utf8mb4_bin`，需保证序列化/反序列化一致。

## 错误码

| 错误码 | 含义 |
| ------ | ---- |
| 1003 | 参数错误（缺失字段、值非法） |
| 1004 | 状态机错误（如重复同步） |
| 1008 | 业务执行失败（DB 异常 / BigSeller 异常） |

## 注意事项

- `unit_price` 与 `total_amount` 在销售模块中均为 **浮点元值**，与供应链模块的"分整数"不同；新增字段时请遵循已有约定
- `submit_sale_order` 涉及外部 BigSeller 库存出库，是不可逆操作，需在 UI 层做二次确认
- 删除使用逻辑删除，`search_sale_order` 默认过滤 `is_delete == 0`
