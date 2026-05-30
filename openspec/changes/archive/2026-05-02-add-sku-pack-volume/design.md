# 设计：SKU 打包体积字段

## Context

`t_sku_info` 已经具备"采购单位"+"单位换算 SKU 数"概念，是一行 SKU 主数据中代表 **包装层面** 的字段。本次新增的"长 / 宽 / 高"是该包装层面的物理属性，与 `Fsku_unit_*` 同层语义。

参考：
- 表设计：[openspec/specs/data-model/design/t_sku_info.md](../../specs/data-model/design/t_sku_info.md)
- API 列表与变更管理：[openspec/specs/apis/spec.md](../../specs/apis/spec.md) `change_management`
- DB 变更管理：[openspec/specs/data-model/spec.md](../../specs/data-model/spec.md) `change_management`

约束：
- 多 project 支持：4 个国家库（philipine / india / malaysia / thailand）需分别 ALTER。
- 不允许使用外键，关联在应用层校验 → 本变更只动单表。
- ORM 与 SQL 必须**双写一致**（`mysql_backend.py` + `docs/ec_erp_db.sql`）。
- 所有 Dto 必须显式列出 `columns`，否则 `DtoUtil.to_dict` 不输出字段。
- API 接口请求字段使用 `request_util.get_int_param("xxx", 0)` 提供默认值，保证向前兼容。

## Goals / Non-Goals

**Goals**
- 在 SKU 主数据中沉淀 **每个采购单位** 的打包尺寸（长/宽/高），单位 cm，整数。
- 通过 `save_sku` 接口允许编辑；通过 `search_sku` 透传给前端。
- 数据库新建库与存量库均能平滑应用本变更（幂等 ALTER 脚本）。
- 所有改动向前兼容：旧前端 / 旧客户端不传该字段，仍能成功调用接口。

**Non-Goals**
- **不**计算体积重 / 海运费（留待后续 follow-up，需要业务规则确认）。
- **不**同步打包尺寸到 BigSeller（BigSeller 没有对应字段；后续若需要再扩展）。
- **不**在采购单 / 销售订单的 SKU 快照内冗余体积字段（首版仅在 `t_sku_info` 主数据维护，使用方按需读取）。
- **不**升级前端 `skuList.vue` 的列展示（首版仅完成后端能力，前端列展示作为 follow-up，由前端 PR 单独跟进）。

## Decisions

### D1：字段类型选择 `INT`，单位 cm

- **决定**：3 个字段均使用 `INT NOT NULL DEFAULT 0`，单位 cm。
- **替代方案**：`FLOAT`（保留小数）/ `DECIMAL(10,2)`（精确）/ `MM` 单位（精度更高）。
- **理由**：
  - 物流场景，cm 整数即可满足精度（行业普遍如此，BigSeller 的产品体积也是整数 cm）。
  - `INT` 对索引 / 比较 / 体积计算（`L*W*H`）友好，且与 `Fsku_unit_quantity` 类型一致。
  - 默认 0 表示"未填写"，与现有 `Fshipping_stock_quantity / Favg_sell_quantity` 等字段的"默认 0 = 未填写"惯例一致。

### D2：字段命名 `Fsku_pack_*`

- **决定**：`Fsku_pack_length` / `Fsku_pack_width` / `Fsku_pack_height`。
- **替代方案**：`Fpack_length` / `Fsku_length` / `Fbox_*`。
- **理由**：
  - 项目命名规范要求字段以 `F` + snake_case；
  - 含义为"按采购单位（包装）打包后的尺寸"，与 `Fsku_unit_*` 同前缀的"打包语义"对齐；
  - 不直接用 `Flength` 等过于通用的名字，避免和未来其他长度字段冲突。

### D3：放置位置（紧邻 `Fsku_unit_quantity`）

- **决定**：在 `Fsku_unit_quantity` 之后追加 3 个字段（DDL `ADD COLUMN ... AFTER Fsku_unit_quantity`）。
- **理由**：与"采购单位"业务语义连续，便于阅读与维护；不影响主键 / 索引顺序。

### D4：API 字段为可选（默认 0），保持向前兼容

- **决定**：`save_sku` 新增 3 个 **可选** 参数；`add_sku` 不引入新参数（写默认 0）；`sync_all_sku` 不动体积字段（保留旧值）；`search_sku` 响应新增 3 个字段（可能值为 0）。
- **替代方案**：将 3 个字段设为必填 → 老前端 / 老脚本会立刻 400 报错。
- **理由**：以"渐进式上线"原则，后端先支持，前端 / 工具按节奏改造；不破坏既有 mock & 自动化任务。

### D5：`sync_all_sku` 不覆盖体积字段

- **决定**：`sync_all_sku` 内的循环复用现有 `SkuDto` 实例（`item.inventory = ...`），未显式覆盖 `sku_pack_*`，因此体积字段会保留数据库中的旧值。代码无需新增逻辑。
- **理由**：避免一次同步把人工录入的体积数据清零。已通过现有实现自动满足该约束，需要 tasks 中加回归用例。

### D6：迁移脚本命名

- **决定**：新建 `docs/sku_info_table_alt_20260430_add_pack_volume.sql`，使用幂等 ALTER（`INFORMATION_SCHEMA` 检查或 `IF NOT EXISTS` 等）。
- **理由**：遵循 [data-model/spec.md](../../specs/data-model/spec.md) 第 4 节"编写 ALTER 升级脚本"中`docs/<table>_table_alt_<YYYYMMDD>_<desc>.sql` 命名约定。

## Risks / Trade-offs

| Risk | Mitigation |
| ---- | ---------- |
| 存量库 ALTER 长时间锁表 | `t_sku_info` 单库通常 < 10w 行，`ADD COLUMN` 默认 INSTANT/INPLACE，影响小；选择业务低峰期执行；脚本带回滚说明 |
| 多国家库忘记执行 | 在 ALTER 脚本头部注释明确 4 个国家逐一执行；运维清单加任务项 |
| `sync_all_sku` 误覆盖体积 | 现有实现复用 ORM 实例自动保留旧值；任务清单加 review 项 + 回归 SQL 抽样校验 |
| `save_sku` 新增 3 个可选参数后，前端误传 `null` | 通过 `request_util.get_int_param("xxx", 0)` 兜底，`None` 时落 0 |
| 体积字段为 0 的 SKU 在前端绘制装柜计算时被忽略 | 与前端约定：0 视为"未填写"，海运计算前端需提示用户补全（本变更不实现该逻辑）|

## Migration Plan

1. **代码灰度**：合入 ORM + SQL + API 改造（兼容默认 0），上线前后端无影响。
2. **执行 ALTER**：在每个国家库分别执行 `docs/sku_info_table_alt_20260430_add_pack_volume.sql`。
3. **回归验证**：
   - `SHOW CREATE TABLE t_sku_info`：确认 3 个字段已新增、默认 0、`INT NOT NULL`。
   - 调用 `search_sku`：响应 JSON 包含 3 个字段。
   - 调用 `save_sku`（带体积）→ 再次 `search_sku`：值已写入。
   - 触发 `sync_all_sku`：手工对比 1~2 行 SKU 的 `Fsku_pack_*`，确认未被清零。
4. **前端 follow-up**（非本次范围）：`skuList.vue` 增加列展示与可编辑（独立 PR）。
5. **回滚**：执行 `ALTER TABLE t_sku_info DROP COLUMN Fsku_pack_length, DROP COLUMN Fsku_pack_width, DROP COLUMN Fsku_pack_height;`，并回滚代码。

## Open Questions

- 后续是否需要在 `t_sku_info` 增加"打包重量 `Fsku_pack_weight` (g)"？业务需要时再开下一份提案，本次不引入。
- 体积是否需要写入 `t_purchase_order.purchase_skus` 快照以便历史溯源？暂不引入；如需要海运费推算"按当时体积"，再启动二次变更。
