# 提案：SKU 打包信息增加体积（长宽高）字段

## Why

当前 `t_sku_info` 仅记录采购单位与单位换算数量（`Fsku_unit_name` / `Fsku_unit_quantity`），缺少 **打包后的物理尺寸**（长 / 宽 / 高）。这导致：

1. **海运费/装柜计算失真**：海运按体积或体积重计费，无法在采购单层面预估海运成本。
2. **拣货 / 装箱辅助缺失**：仓库无法基于 SKU 体积做装箱建议、货架占用规划。
3. **后续打印面单 / 报关数据无依据**：包裹尺寸需要重复人工填写。

业务侧已经在维护"采购单位 = N 个 SKU"的概念，自然延伸：每"采购单位"包装体积应作为 SKU 主数据落库，便于后续被采购、仓储、销售等模块复用。

## What Changes

- 在 `t_sku_info` 表新增 3 个字段，记录 **每个采购单位的打包尺寸**（单位：cm，默认 0，类型 `INT`）：
  - `Fsku_pack_length` 打包长度
  - `Fsku_pack_width` 打包宽度
  - `Fsku_pack_height` 打包高度
- `SkuDto` ORM 同步新增对应字段并加入 `columns` 列表。
- Supplier 模块 SKU 相关接口需要支持读写体积字段：
  - `/erp_api/supplier/save_sku`：请求参数新增 3 个字段（**可选**，未传时按 0 处理，向前兼容）。
  - `/erp_api/supplier/search_sku`：响应结构新增 3 个字段。
  - `/erp_api/supplier/add_sku`：批量添加时按默认值 0 写入；后续通过 `save_sku` 完善。
  - `/erp_api/supplier/sync_all_sku`：仅同步库存/销量/ERP 信息，**不覆盖**已存在的体积字段（保留旧值）。
- 数据库迁移：编写 `docs/sku_info_table_alt_<YYYYMMDD>_add_pack_volume.sql`，对存量库做 `ALTER TABLE ... ADD COLUMN ...`。
- 文档同步：
  - `openspec/specs/data-model/design/t_sku_info.md`：字段表 + DDL + Change-Log
  - `openspec/specs/apis/design/supplier/{search_sku,save_sku,add_sku,sync_all_sku}.md`：参数/响应表 + 示例 + Change-Log
  - `docs/erp_api/supplier/save_sku.md`、`docs/erp_api/supplier/search_sku.md`：业务文档
  - `docs/ec_erp_db.sql`：建表语句
- 兼容性：体积字段全部 **可选 + 默认 0**，不属于不兼容变更；前端不强制升级（升级才能展示/编辑）。

## Capabilities

### New Capabilities

无（本次变更复用现有能力）。

### Modified Capabilities

- `data-model`：`t_sku_info` 新增 3 列字段，DTO 与 SQL 同步。
- `supplier-module`：4 个 SKU 接口需要支持读取/保存打包体积字段。

## Impact

**代码影响**

- ORM：`ec_erp_api/models/mysql_backend.py` `SkuDto`
- API：`ec_erp_api/apis/supplier.py` 中 `save_sku` / `add_sku` / `sync_all_sku`（保留旧值）；`search_sku` 通过 DTO 自动透传
- 关联读取（无需改写，但需回归）：
  - `ec_erp_api/apis/supplier.py` `build_purchase_order_from_req`（采购单 SKU 快照，可选择是否带上体积）
  - `ec_erp_api/apis/sale.py` `create_sale_order` / `update_sale_order` / `submit_sale_order`（仅依赖 `erp_sku_id`、不读体积，无影响）
- 工具：`tools/import_sku.py`（新增字段使用默认 0，后续通过 `save_sku` 维护）
- 同步任务：`auto_sync_tools/sync_sku_inventory.py` 需保证不覆盖体积字段（直接复用 `sku_info` 实例字段，不会被覆盖）

**数据库影响**

- 单一 ALTER 语句（3 个 `ADD COLUMN`），低风险，可幂等
- 4 个国家库分别执行（philipine / india / malaysia / thailand）

**前端影响（ec-erp-static，可选后续升级）**

- `src/pages/supply/skuList.vue` 增加 3 列展示与可编辑（建议 follow-up）
- `src/apis/supplierApis.ts` 无需变化（调用端透传字段即可）

**第三方影响**

- 不涉及 BigSeller 接口

**回滚方式**

- `ALTER TABLE t_sku_info DROP COLUMN Fsku_pack_length, DROP COLUMN Fsku_pack_width, DROP COLUMN Fsku_pack_height;`
