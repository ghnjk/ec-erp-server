# 提案：自动同步任务支持 BigSeller / UpSeller 双 ERP

## Why

当前 `auto_sync_tools/sync_all_sku.py` 与 `auto_sync_tools/sync_sku_inventory.py` 仍直接绑定 `build_big_seller_client()` / `build_sku_manager()` 与 `BigSellerClient` 原生字段，**与 BigSeller ERP 强耦合**。新切到 UpSeller ERP 的 project（`use_up_seller=true`）执行这两个脚本时会出现：

1. 仍然登录 BigSeller，但项目实际数据在 UpSeller，**同步内容与生产数据错位**；
2. 直接读取 `big_seller_warehouse_id`、调用 `query_sku_inventory_detail(sku, warehouse_id)` 的原始 dict 字段（`avgDailySales`/`available`），**UpSeller 字段命名不同**（`warehouseVOS` / 大写 `warehouseId` / 无 `avgDailySales`），调用即报错或字段漂空；
3. 与 `ec_erp_api/apis/supplier.py` 已经统一到 `build_seller_client()` 的设计割裂，运维与开发都需要为不同 ERP 维护两条路径。

`apis/supplier.py` 已经通过 `ec_erp_api/common/seller_util.build_seller_client()`、`ec/seller_client.SellerClient` 抽象屏蔽了 BigSeller / UpSeller 差异（`SkuDetail` / `InventoryDetail` / `StockMoveItem`），定时任务侧应当对齐同一抽象，**让两个国家库无差别使用同一份脚本与同一份 crontab**。

## What Changes

- 将 `auto_sync_tools/sync_all_sku.py`、`auto_sync_tools/sync_sku_inventory.py` 的 SKU/库存查询统一改造为基于 `ec_erp_api.common.seller_util.build_seller_client()` 的 `SellerClient` 抽象：
  - 不再 `from ec_erp_api.common.big_seller_util import build_big_seller_client, build_sku_manager`；
  - 改为 `from ec_erp_api.common.seller_util import build_seller_client, get_seller_warehouse_id`；
  - 通过 `seller.query_sku_detail(sku)` / `seller.query_sku_inventory_detail(sku)` 拿 `SkuDetail` / `InventoryDetail`，**不再手写 BigSeller 原生字段**；
  - 仓库 ID 从 `get_seller_warehouse_id()` 取，禁止直读 `config["big_seller_warehouse_id"]`。
- `sync_all_sku.py` 不再调用 `SkuManager.load_and_update_all_sku(BigSellerClient)`，改为通过 `SellerClient` 暴露的统一刷新入口（详见 design.md D1）刷新当前 ERP 的本地 SKU 缓存（BigSeller → `cookies/all_sku.json`，UpSeller → `cookies/all_up_seller_sku.json`）。
- `sync_sku_inventory.py` 计算 `avg_sell_quantity` / `inventory_support_days` 时按 `InventoryDetail.avg_daily_sales` 取值；UpSeller 当前不暴露日销均量（值为 0），保持 0 → `inventory_support_days` 取兜底逻辑（与 BigSeller 老逻辑等价路径），**不得回写 0 抹掉数据库中已有的非 0 历史值**（详见 design.md D3）。
- `auto_sync_tools_spec.md` 模块规约更新：脚本表"主要用途"列与 `sync_all_sku.py` / `sync_sku_inventory.py` 的"流程"小节，全部改为 SellerClient 统一抽象口径，并新增 UpSeller 行为说明（avg_daily_sales=0、本地缓存路径等）。
- **不修改** BigSeller / UpSeller 的 client / adapter / 工厂代码，本变更仅替换两条调用链路。
- **不**新增 ERP 抽象 API（仅在必要时为"刷新本地 SKU 缓存"在 SellerClient 协议上加一个最小方法，详见 design.md D1）。
- **不**触碰 `sync_order_to_es.py`、`sync_shop_statics_to_es.py`、`auto_preload_order.py`、`auto_return_refund_order_to_warehouse.py` —— 这几个脚本目前仍只在 BigSeller 项目运行，按现状保留；后续若也要 UpSeller 化，再单独提案。

## Capabilities

### New Capabilities
- `seller-sku-sync`: 描述 ERP SKU 主数据 + 库存定时同步链路在统一 SellerClient 抽象下应满足的行为契约，覆盖 `auto_sync_tools/sync_all_sku.py`、`auto_sync_tools/sync_sku_inventory.py` 两个脚本，并显式声明它们对 BigSeller / UpSeller 的兼容要求。

### Modified Capabilities
<!-- 现有 supplier-module spec 已经针对统一 SellerClient 改造完成，本次仅作用于自动化脚本。
     `auto_sync_tools_spec.md` 当前是描述性文档而非需求型 spec 文件，其内容更新放在 tasks 中处理；
     无需在变更里以 delta 形式重写 -->

## Impact

**代码影响**

- 修改文件：
  - `auto_sync_tools/sync_all_sku.py`
  - `auto_sync_tools/sync_sku_inventory.py`
- 可能新增最小 API：`ec/seller_client.py` 协议、`ec/big_seller_adapter.py`、`ec/up_seller_adapter.py` 增加 `refresh_local_sku_cache()` 方法（详见 design.md D1）。
- 文档：
  - `openspec/specs/auto_sync_tools_spec.md`
  - `openspec/changes/support-upseller-sku-sync/specs/seller-sku-sync/spec.md`（本变更产出）

**数据影响**

- 不改变 MySQL `t_sku_info` schema，仅改动同步脚本的写入逻辑路径。
- BigSeller 项目运行结果保持不变（接入路径替换为抽象，行为等价）。
- UpSeller 项目首次执行 `sync_sku_inventory` 时：
  - `inventory` / `erp_sku_name` / `erp_sku_image_url` 来自 UpSeller `warehouseVOS`（详见 `up_seller_adapter`）；
  - `avg_sell_quantity`、`inventory_support_days` 行为见 design.md D3。

**部署影响**

- crontab 命令保持不变（仍是 `python sync_all_sku.py` / `python sync_sku_inventory.py`）。
- UpSeller 项目需要保证 `application.json` 含完整 `up_seller` 块（mail / password / warehouse_id），且 `cookies/up_seller.cookies` 已通过登录写入；首次执行可能触发 UpSeller selenium 登录流程（与 supplier.py 相同行为）。

**回滚方式**

- `git revert` 两个脚本的改动即可恢复 BigSeller 直连版本；无数据库回滚成本。
