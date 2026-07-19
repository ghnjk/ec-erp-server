# seller-sku-sync 能力规约

## Purpose

本能力定义 ERP SKU 主数据 / 库存定时同步链路在统一 `SellerClient` 抽象下应满足的行为契约，覆盖 `auto_sync_tools/sync_all_sku.py` 与 `auto_sync_tools/sync_sku_inventory.py` 两个脚本，并约束这两个脚本对 BigSeller / UpSeller 双 ERP 的兼容方式（统一通过 `SellerClient` 适配层访问 `SkuDetail` / `InventoryDetail`，禁止直接读取各 ERP 的私有字段或私有配置键）。

相关规约：

- [auto_sync_tools_spec.md](../auto_sync_tools_spec.md)：自动同步任务总体规约（脚本列表、crontab 部署、日志重定向等）。
- [bigseller_integration_spec.md](../bigseller_integration_spec.md)：BigSeller 第三方集成规约（`BigSellerClient`、`SkuManager`、cookie 持久化、验证码识别等底层能力）。

## Requirements

### Requirement: 自动同步脚本必须使用统一 SellerClient 抽象

`auto_sync_tools/sync_all_sku.py` 与 `auto_sync_tools/sync_sku_inventory.py` SHALL 通过 `ec_erp_api.common.seller_util.build_seller_client()` 获取 `SellerClient` 实例，**不得**直接 `import` `ec_erp_api.common.big_seller_util.build_big_seller_client` 或 `ec_erp_api.common.big_seller_util.build_sku_manager`。

约束：

- 仓库 ID（如脚本需要）SHALL 通过 `ec_erp_api.common.seller_util.get_seller_warehouse_id()` 获取，**不得**直接读 `application.json` 中的 `big_seller_warehouse_id` 等 BigSeller 私有键；如脚本不需要仓库 ID，应**直接省略该局部变量**，由 adapter 内部持有。
- SKU/库存查询 SHALL 通过 `SellerClient.query_sku_detail(sku)` / `SellerClient.query_sku_inventory_detail(sku)` 走 `SkuDetail` / `InventoryDetail` 抽象，**不得**访问 BigSeller 原生字段（`warehouseVoList` / `avgDailySales` / `available` 等）。
- 同步脚本 SHALL NOT 在内部分支判断 `application.json:use_up_seller`；ERP 路由由 `seller_util` 统一负责。

#### Scenario: BigSeller 项目执行 `sync_all_sku.py`
- **GIVEN** 项目 `application.json` 中 `use_up_seller=false`（或未配置）
- **WHEN** 在 `auto_sync_tools` 目录执行 `python sync_all_sku.py`
- **THEN** 脚本 SHALL 通过 `build_seller_client()` 拿到 `BigSellerAdapter` 实例
- **AND** 调用 `seller.refresh_local_sku_cache()` 后，BigSeller 全量 SKU 列表 SHALL 写入 `cookies/all_sku.json` 与 `cookies/all_variant_sku_mapping.json`
- **AND** 不 import `big_seller_util.build_big_seller_client` 或 `big_seller_util.build_sku_manager`。

#### Scenario: UpSeller 项目执行 `sync_all_sku.py`
- **GIVEN** 项目 `application.json` 中 `use_up_seller=true` 且 `up_seller` 配置完整
- **WHEN** 在 `auto_sync_tools` 目录执行 `python sync_all_sku.py`
- **THEN** 脚本 SHALL 通过 `build_seller_client()` 拿到 `UpSellerAdapter` 实例
- **AND** 调用 `seller.refresh_local_sku_cache()` 后，UpSeller 全量 SKU 列表 SHALL 写入 `cookies/all_up_seller_sku.json`
- **AND** 不触发 BigSeller 登录或 `cookies/big_seller.cookies` 写盘。

### Requirement: SellerClient 协议必须暴露 `refresh_local_sku_cache` 方法

`ec/seller_client.py:SellerClient` 协议 SHALL 增加方法签名：

```python
def refresh_local_sku_cache(self) -> None: ...
```

- `ec/big_seller_adapter.py:BigSellerAdapter` SHALL 实现该方法，行为等价于 `SkuManager.load_and_update_all_sku(BigSellerClient)`，结果落到 `cookies/all_sku.json` + `cookies/all_variant_sku_mapping.json`。
- `ec/up_seller_adapter.py:UpSellerAdapter` SHALL 实现该方法，行为等价于 `UpSellerSkuManager.load_and_update_all_sku(UpSellerClient)`，结果落到 `cookies/all_up_seller_sku.json`。
- 该方法 SHALL 不抛异常退出登录态；如上游接口失败，按各自 client 的异常路径抛出，**不得**静默忽略。

#### Scenario: BigSeller adapter 刷新本地 SKU 缓存
- **GIVEN** `BigSellerAdapter` 实例已登录
- **WHEN** 调用 `refresh_local_sku_cache()`
- **THEN** `cookies/all_sku.json` SHALL 被覆盖写入新的 SKU 全量数据
- **AND** `cookies/all_variant_sku_mapping.json` SHALL 同步更新。

#### Scenario: UpSeller adapter 刷新本地 SKU 缓存
- **GIVEN** `UpSellerAdapter` 实例已登录
- **WHEN** 调用 `refresh_local_sku_cache()`
- **THEN** `cookies/all_up_seller_sku.json` SHALL 被覆盖写入 UpSeller 全量 SKU 数据。

### Requirement: `sync_sku_inventory.py` 必须按抽象字段重写库存计算

`auto_sync_tools/sync_sku_inventory.py` 的库存与销量计算 SHALL 完全基于 `SkuDetail` / `InventoryDetail` 字段；**不得**保留 `get_real_inventory(client, warehouse_id, sku_id)` 这种直接遍历 `warehouseVoList` 的辅助函数。

字段映射（写回 `t_sku_info`）SHALL 为：

| `t_sku_info` 字段 | 源 |
| ---- | ---- |
| `inventory` | `SkuDetail.inventory_in_warehouse` |
| `erp_sku_id` | `SkuDetail.erp_sku_id` |
| `erp_sku_name` | `SkuDetail.title` 优先；为空时回落 `InventoryDetail.title` |
| `erp_sku_image_url` | `SkuDetail.image_url` 优先；为空时回落 `InventoryDetail.image_url` |
| `shipping_stock_quantity` | `load_all_shipping_sku_info(backend)` 返回值（保持现状） |

约束：

- 同步脚本 SHALL 在每条 SKU 处理后保留 `time.sleep(0.3)` 节流（与现状一致）；
- 单条 SKU 异常 SHALL `print` 报错并 `continue`，**不得**中断整体任务；
- `sync_sku_inventory.py` SHALL NOT 修改 `Fsku_pack_length` / `Fsku_pack_width` / `Fsku_pack_height`（与 `add-sku-pack-volume` 已有约束一致），通过复用 `backend.search_sku()` 返回的 ORM 实例自动满足。

#### Scenario: BigSeller 项目同步若干 SKU
- **GIVEN** BigSeller 项目，3 个 SKU 在 ERP 中已存在
- **WHEN** 执行 `python sync_sku_inventory.py`
- **THEN** 每个 SKU 的 `t_sku_info.inventory` SHALL 等于该 SKU 在 `big_seller_warehouse_id` 对应仓库的 `available`（与 `BigSellerAdapter.query_sku_detail` 一致）
- **AND** `erp_sku_name` SHALL 等于 BigSeller 返回的 `title`
- **AND** 脚本完整执行不抛异常。

#### Scenario: UpSeller 项目同步若干 SKU
- **GIVEN** UpSeller 项目，3 个 SKU 在 ERP 中已存在
- **WHEN** 执行 `python sync_sku_inventory.py`
- **THEN** 每个 SKU 的 `t_sku_info.inventory` SHALL 等于 UpSeller `warehouseVOS` 中匹配 `warehouseId` 的 `available`
- **AND** `erp_sku_name` SHALL 取 UpSeller `query_sku_detail.title`，为空时回落 `query_sku_inventory_detail.skuTitle`
- **AND** 脚本完整执行不抛异常。

### Requirement: UpSeller 必须按 14 个完整自然日统计单 SKU 日均销量

`SellerClient.load_sku_avg_daily_sales(begin_date, end_date)` SHALL：

- BigSeller 返回 `None`，继续使用 `InventoryDetail.avg_daily_sales`；
- UpSeller 返回指定 `[begin_date, end_date)` 的单 SKU 日均销量字典；
- `sync_sku_inventory.py` SHALL 传入 `[today-17天, today-3天)`，排除最近 3 个完整自然日并固定使用 14 天作分母；
- UpSeller 区间完整加载成功时，未出现在字典中的 SKU SHALL 视为真实零销量并覆盖历史值；
- 任一天加载失败时 SHALL 返回失败，由脚本打印一次告警、继续库存同步并保留历史均量。

UpSeller 每日原始变种销量 SHALL 原子缓存到
`{cookies_dir}/up_seller_sales/YYYY-MM-DD.json`。已有有效缓存不得重复请求上游；损坏或版本
不兼容的缓存可以重新抓取，但只有完整抓取成功后才能替换目标文件。

#### Scenario: UpSeller 组合 SKU 拆分后计算均量
- **GIVEN** 平台变种 SKU 映射到组合 SKU `GROUP`，且 `groupVOS` 包含 `SINGLE × 6`
- **AND** 14 天内 `GROUP` 售出 2 件
- **WHEN** 加载区间日均销量
- **THEN** `SINGLE` 的累计销量 SHALL 为 12
- **AND** 日均销量 SHALL 为 `12 / 14`。

#### Scenario: UpSeller 完整区间内真实零销量
- **GIVEN** 14 个日期缓存均完整
- **AND** 数据库某 SKU 未出现在任何销售记录中
- **WHEN** 执行 `sync_sku_inventory.py`
- **THEN** 该 SKU `avg_sell_quantity` SHALL 更新为 0
- **AND** `inventory_support_days` SHALL 按 `inventory / 0.01` 计算。

#### Scenario: UpSeller 销量接口失败时保留历史均量
- **GIVEN** 数据库中某 SKU `avg_sell_quantity = 5.5`
- **AND** 14 天中任一天销量抓取失败
- **WHEN** 执行 `sync_sku_inventory.py`
- **THEN** 库存同步 SHALL 继续
- **AND** 该 SKU `avg_sell_quantity` SHALL 仍为 5.5。

### Requirement: UpSeller 销售变种必须精确映射并拆为最终单 SKU

平台销售行 SHALL 按以下优先级映射内部 SKU：

1. `(shopId, platform, variationId)` 匹配 `relationVos.platformVariantsId`；
2. `(shopId, platform, variationSku)` 匹配 `relationVos.platformSku`；
3. `variationSku` 精确匹配 `all_up_seller_sku.json` 的 SKU 键。

系统 SHALL NOT 使用模糊 SKU 匹配。组合 SKU SHALL 根据 `groupVOS[].varSku/num` 递归拆分，
并检测循环、缺失子 SKU、空组合明细及无效数量；无法映射或拆分的销售行 SHALL 记录告警并跳过。
若区间内存在销量但全部销售行都无法映射，统计 SHALL 失败并触发保留历史均量的降级路径，
不得把所有 SKU 错误清零。

#### Scenario: BigSeller 真实日销
- **GIVEN** 数据库中某 SKU `avg_sell_quantity = 5.5`、`inventory = 100`
- **AND** BigSeller 返回 `avg_daily_sales = 10.0`
- **WHEN** 执行 `sync_sku_inventory.py`
- **THEN** 数据库中该 SKU `avg_sell_quantity` SHALL 被更新为 `round(10.0 * 1.1, 2) = 11.0`
- **AND** `inventory_support_days` SHALL 等于 `int(100 / 11.0) = 9`。

### Requirement: `sync_sku_inventory.py` 必须保留多 project 切换能力

`sync_sku_inventory.py` SHALL 继续从 `application.json` 读 `sync_tool_project_id`（默认 `philipine`）来构造 `MysqlBackend`；`build_backend()` SHALL 继续来自 `ec_erp_api.common.big_seller_util`（与 ERP 解耦），本变更**不**搬动该工厂位置。

约束：

- `sync_sku_inventory.py` 单次仍只处理一个 project；
- `build_backend(project_id)` 与 `build_seller_client()` 在脚本中可同时存在，分别负责数据库与 ERP。

#### Scenario: 切换 project_id
- **GIVEN** `application.json` 中 `sync_tool_project_id = "india"`
- **WHEN** 执行 `python sync_sku_inventory.py`
- **THEN** 脚本 SHALL 使用 `build_backend("india")` 连接对应 MySQL 实例
- **AND** 同步结果 SHALL 仅落到 `india` 数据库的 `t_sku_info`。
