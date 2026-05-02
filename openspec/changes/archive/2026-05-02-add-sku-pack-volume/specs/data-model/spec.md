# Delta Spec：data-model（t_sku_info 新增打包体积字段）

## ADDED Requirements

### Requirement: t_sku_info 必须支持打包体积字段（长/宽/高，cm）

`t_sku_info` SHALL 包含 3 个新字段，用于记录"每个采购单位"打包后的物理尺寸（cm）：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fsku_pack_length` | INT | 是 | 0 | 打包长度（cm） |
| `Fsku_pack_width` | INT | 是 | 0 | 打包宽度（cm） |
| `Fsku_pack_height` | INT | 是 | 0 | 打包高度（cm） |

约束：
- 字段语义：**每个采购单位（`Fsku_unit_name`，含 `Fsku_unit_quantity` 个 SKU）** 的打包尺寸；不是单个 SKU 自身的尺寸。
- 默认 0 表示"未填写"，不参与体积计算。
- 字段类型 `INT NOT NULL DEFAULT 0`，单位固定 cm。
- DDL 中 3 个字段 SHALL 紧跟在 `Fsku_unit_quantity` 之后（`AFTER Fsku_unit_quantity`）。
- `SkuDto` ORM SHALL 同步新增 3 个字段并加入 `columns` 列表，否则 `DtoUtil.to_dict` 不输出。

#### Scenario: 新建库执行 docs/ec_erp_db.sql

- **WHEN** 在新国家库执行最新 `docs/ec_erp_db.sql`
- **THEN** `t_sku_info` 表 SHALL 包含 `Fsku_pack_length` / `Fsku_pack_width` / `Fsku_pack_height` 3 列
- **AND** 类型 SHALL 为 `INT NOT NULL DEFAULT 0`
- **AND** 注释分别为 "打包长度（cm）"、"打包宽度（cm）"、"打包高度（cm）"

#### Scenario: 存量库执行 ALTER 脚本

- **WHEN** 在已有数据的国家库执行 `docs/sku_info_table_alt_<YYYYMMDD>_add_pack_volume.sql`
- **THEN** 3 个字段 SHALL 被新增，且既有数据行的 3 个字段值 SHALL 为 0（默认值）
- **AND** 该脚本 SHALL 是幂等的：重复执行不应报错（已存在则跳过）

#### Scenario: ORM 与 SQL 双写一致

- **WHEN** 通过 `SkuDto(...)` 构造对象并经 `DtoUtil.to_dict` 序列化
- **THEN** 输出 dict SHALL 包含 `sku_pack_length` / `sku_pack_width` / `sku_pack_height` 3 个 key
- **AND** `SkuDto.columns` 列表 SHALL 包含上述 3 个字段名

### Requirement: t_sku_info Change-Log 必须记录打包体积字段新增

[openspec/specs/data-model/design/t_sku_info.md](../../../../specs/data-model/design/t_sku_info.md) 文件 SHALL 在 `## Change-Log` 章节追加一条 "新增打包体积字段" 的记录，并在文件主体内：
- 更新 `## CREATE TABLE` 代码块
- 更新 `## 字段说明` 表格
- 更新 `## DTO 类` 代码块（含 `columns`）

#### Scenario: design 文档同步更新

- **WHEN** 阅读 `openspec/specs/data-model/design/t_sku_info.md`
- **THEN** `## CREATE TABLE` 章节 SHALL 出现新增 3 个字段
- **AND** `## 字段说明` 表 SHALL 出现新增 3 行
- **AND** `## DTO 类` 章节 SHALL 出现新增 3 个 `Mapped[int] = Column(...)` 定义且 `columns` 列表内含新字段
- **AND** `## Change-Log` 章节 SHALL 追加一条新条目，含变更类型 / 原因 / 内容 / ALTER 脚本 / 回滚方式

### Requirement: sync_all_sku 不得覆盖打包体积字段

`auto_sync_tools/sync_sku_inventory.py` 与 `/erp_api/supplier/sync_all_sku` 在同步库存 / 销量 / ERP 信息时 SHALL NOT 覆盖 `Fsku_pack_length` / `Fsku_pack_width` / `Fsku_pack_height` 字段。

#### Scenario: 同步任务保留体积字段旧值

- **WHEN** 一行 SKU 的 `Fsku_pack_length=30, Fsku_pack_width=20, Fsku_pack_height=15`，触发 `sync_all_sku` 或定时任务 `sync_sku_inventory`
- **THEN** 该行 3 个体积字段 SHALL 保持为 30 / 20 / 15，不被清零或更改
