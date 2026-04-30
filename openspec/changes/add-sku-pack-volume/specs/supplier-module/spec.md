# Delta Spec：supplier-module（SKU 接口支持打包体积字段）

## ADDED Requirements

### Requirement: /erp_api/supplier/save_sku 必须支持读写打包体积字段

`/erp_api/supplier/save_sku` 请求体 SHALL 接受 3 个 **可选** 整型参数：

| 参数 | 类型 | 必填 | 默认 | 说明 |
| ---- | ---- | ---- | ---- | ---- |
| `sku_pack_length` | int | 否 | 0 | 每个采购单位的打包长度（cm） |
| `sku_pack_width` | int | 否 | 0 | 每个采购单位的打包宽度（cm） |
| `sku_pack_height` | int | 否 | 0 | 每个采购单位的打包高度（cm） |

约束：
- 服务端 SHALL 通过 `request_util.get_int_param("sku_pack_length", 0)` 等带默认值的方式读取，未传或传 `null` 时落 0。
- 接口 SHALL 在构造 `SkuDto` 时把 3 个字段透传到 ORM。
- 响应体 `data` 字段（`DtoUtil.to_dict(SkuDto)`）SHALL 包含 3 个字段的当前值。

#### Scenario: 旧客户端不传体积字段（向前兼容）

- **WHEN** 调用方仅传统老字段（`sku, sku_group, sku_name, sku_unit_*, avg_sell_quantity, ...`），不传体积字段
- **THEN** 接口 SHALL 返回成功
- **AND** 数据库中体积 3 个字段 SHALL 被写入 0（首次创建）或保持旧值（已有记录被覆盖式 upsert 时，由于参数读默认 0，会写为 0；调用方应当传完整字段以避免清零，参见下一个 Scenario）

#### Scenario: 客户端传完整体积字段

- **WHEN** 请求体包含 `"sku_pack_length": 30, "sku_pack_width": 20, "sku_pack_height": 15`
- **THEN** 落库后 `Fsku_pack_length=30, Fsku_pack_width=20, Fsku_pack_height=15`
- **AND** 响应 JSON 中 `data.sku_pack_length / sku_pack_width / sku_pack_height` SHALL 等于 30 / 20 / 15

### Requirement: /erp_api/supplier/search_sku 响应必须包含打包体积字段

`/erp_api/supplier/search_sku` 返回的 `data.list[*]` SHALL 包含 `sku_pack_length` / `sku_pack_width` / `sku_pack_height` 3 个字段。

约束：
- 实现层不需要新增逻辑：通过 `SkuDto.columns` 自动透传，前提是 `SkuDto` 已加入 3 个字段（依赖 data-model 变更）。
- 文档（design + docs/erp_api）SHALL 在响应字段表中显式列出。

#### Scenario: 分页查询返回包含体积字段

- **WHEN** 调用 `/erp_api/supplier/search_sku` 任意条件
- **THEN** 响应中每个 SKU 对象 SHALL 含 `sku_pack_length`, `sku_pack_width`, `sku_pack_height` 三个 key
- **AND** 未填写的 SKU 三个字段值 SHALL 为 0

### Requirement: /erp_api/supplier/add_sku 默认体积字段为 0

`/erp_api/supplier/add_sku` 在批量初始化 SKU 时 SHALL 写入体积字段默认值 0；不引入新的请求参数。

约束：
- 不修改请求参数（仅 `skus` 多行字符串）。
- 在构造 `SkuDto(...)` 时显式传 `sku_pack_length=0, sku_pack_width=0, sku_pack_height=0`，或依赖 ORM 列默认值。
- 后续通过 `save_sku` 完善体积。

#### Scenario: 批量添加后体积字段为 0

- **WHEN** 通过 `/erp_api/supplier/add_sku` 添加新 SKU
- **THEN** 数据库中该 SKU 行的 3 个体积字段 SHALL 为 0
- **AND** 调用 `search_sku` 返回值的 3 个体积字段 SHALL 为 0

### Requirement: /erp_api/supplier/sync_all_sku 不得覆盖体积字段

`/erp_api/supplier/sync_all_sku` SHALL NOT 修改 `Fsku_pack_length` / `Fsku_pack_width` / `Fsku_pack_height`。

约束：
- 当前实现复用 ORM 实例 `item`，仅显式覆盖 `inventory / erp_sku_* / avg_sell_quantity / inventory_support_days`，其他字段（含体积）保留旧值。
- 若未来重构为重新构造 `SkuDto`，必须显式从旧记录读出体积并写回。

#### Scenario: 同步前后体积保持

- **GIVEN** 数据库中某 SKU 的体积为 (30, 20, 15)
- **WHEN** 触发 `/erp_api/supplier/sync_all_sku`
- **THEN** 同步完成后该 SKU 的体积 SHALL 仍为 (30, 20, 15)

### Requirement: SKU 相关接口的 design 与业务文档必须同步更新

每个受影响接口的 design 文档与业务文档 SHALL 同步更新：

- design 文档（`openspec/specs/apis/design/supplier/`）：
  - `save_sku.md`
  - `search_sku.md`
  - `add_sku.md`
  - `sync_all_sku.md`
- 业务文档（`docs/erp_api/supplier/`）：
  - `save_sku.md`
  - `search_sku.md`
- 模块 spec：`openspec/specs/supplier_module_spec.md`（`save_sku` 段落补充体积字段）

每个 design 文档 SHALL 在文末 `## Change-Log` 章节追加变更条目，含变更类型 / 原因 / 内容 / 前端影响 / 回滚方式。

#### Scenario: design / 业务文档同步

- **WHEN** 阅读上述文档
- **THEN** 请求/响应字段表 SHALL 包含 3 个体积字段（`save_sku` 是请求 + 响应；`search_sku` 是响应；`add_sku` / `sync_all_sku` 是响应或保留说明）
- **AND** Change-Log 章节 SHALL 追加新条目
