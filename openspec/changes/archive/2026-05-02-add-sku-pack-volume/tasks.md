# Tasks：add-sku-pack-volume

## 1. ORM 与建表 SQL

- [x] 1.1 在 `ec_erp_api/models/mysql_backend.py` 的 `SkuDto` 中新增 3 个字段：`sku_pack_length` / `sku_pack_width` / `sku_pack_height`，类型 `Mapped[int] = Column('Fsku_pack_length', Integer, default=0, server_default="0", comment='打包长度（cm）')`，三个字段语法保持一致
- [x] 1.2 在 `SkuDto.columns` 列表中追加 `sku_pack_length / sku_pack_width / sku_pack_height` 三项，确保 `DtoUtil.to_dict` 能输出
- [x] 1.3 更新 `docs/ec_erp_db.sql` 中 `t_sku_info` 的 `CREATE TABLE` 语句，在 `Fsku_unit_quantity` 之后追加 3 个 `INT NOT NULL DEFAULT 0` 字段及中文注释

## 2. 存量库 ALTER 脚本

- [x] 2.1 创建 `docs/sku_info_table_alt_20260430_add_pack_volume.sql`：
  - 顶部注释：变更背景、风险评估（低）、执行说明（4 个国家库分别执行）、回滚方式
  - 使用 `INFORMATION_SCHEMA.COLUMNS` 检查列存在或 MySQL 8 `ADD COLUMN IF NOT EXISTS`，保证幂等
  - 3 个 `ADD COLUMN ... AFTER Fsku_unit_quantity`，全部 `INT NOT NULL DEFAULT 0`，含 cm 注释
- [x] 2.2 在脚本中显式给出回滚 SQL（注释形式）：`ALTER TABLE t_sku_info DROP COLUMN Fsku_pack_length, DROP COLUMN Fsku_pack_width, DROP COLUMN Fsku_pack_height;`

## 3. Supplier 模块 API 改造

- [x] 3.1 修改 `ec_erp_api/apis/supplier.py` 的 `save_sku`：
  - 通过 `request_util.get_int_param("sku_pack_length", 0)` 等读取 3 个新参数
  - 在构造 `SkuDto(...)` 时传入 3 个字段
- [x] 3.2 修改 `ec_erp_api/apis/supplier.py` 的 `add_sku`：
  - 在批量构造 `SkuDto(...)` 时显式传 `sku_pack_length=0, sku_pack_width=0, sku_pack_height=0`（语义化默认）
- [x] 3.3 检查 `ec_erp_api/apis/supplier.py` 的 `sync_all_sku`：
  - 确认仅显式覆盖 `inventory / erp_sku_* / avg_sell_quantity / inventory_support_days / shipping_stock_quantity`，不动体积字段
  - 在函数注释或文档中标注"不覆盖打包体积字段"
- [x] 3.4 `search_sku` 无需代码改动（依赖 `SkuDto.columns` 自动透传），人工 review 验证

## 4. 关联代码与工具兼容性

- [x] 4.1 `tools/import_sku.py`：在构造 `SkuDto(...)` 时显式传 `sku_pack_length=0, sku_pack_width=0, sku_pack_height=0`，避免 ORM 默认值在 `INSERT` 时遗漏（保险写法）
- [x] 4.2 `auto_sync_tools/sync_sku_inventory.py`：与 3.3 同义务 review，确认不修改体积字段；不需新增逻辑
- [x] 4.3 `ec_erp_api/apis/supplier.py` 中 `build_purchase_order_from_req`：保持现状（采购单 SKU 快照不冗余体积字段，本变更不引入），人工 review 注释一行说明
- [x] 4.4 `ec_erp_api/apis/sale.py` 中 `create_sale_order` / `update_sale_order` / `submit_sale_order`：仅依赖 `erp_sku_id` 等字段，不读体积，无需改动；人工 review 验证

## 5. design 文档更新（openspec/specs）

- [x] 5.1 更新 `openspec/specs/data-model/design/t_sku_info.md`：
  - `## CREATE TABLE` 代码块：追加 3 个字段
  - `## 字段说明` 表：追加 3 行
  - `## DTO 类` 代码块：追加 3 个 `Mapped[int] = Column(...)` 与 `columns` 列表
  - `## Change-Log` 章节：追加新条目（含 ALTER 脚本与回滚方式）
  - "存量库 ALTER 脚本" 区块同步给出本次脚本内容
- [x] 5.2 更新 `openspec/specs/apis/design/supplier/save_sku.md`：
  - 请求参数表追加 3 个可选 int 字段（默认 0）
  - 响应字段表追加 3 个 int 字段
  - 请求/响应示例 JSON 加入示例值（如 30/20/15）
  - `## Change-Log` 追加条目
- [x] 5.3 更新 `openspec/specs/apis/design/supplier/search_sku.md`：
  - 响应参数表追加 3 个 int 字段
  - 响应示例 JSON 增加 3 个字段
  - `## Change-Log` 追加条目
- [x] 5.4 更新 `openspec/specs/apis/design/supplier/add_sku.md`：
  - 注意事项中说明"新增的打包体积字段默认 0，需通过 save_sku 完善"
  - `## Change-Log` 追加条目（说明默认值行为）
- [x] 5.5 更新 `openspec/specs/apis/design/supplier/sync_all_sku.md`：
  - 注意事项中显式声明"sync_all_sku 不修改打包体积字段"
  - `## Change-Log` 追加条目
- [x] 5.6 更新 `openspec/specs/supplier_module_spec.md` 第 3 段（`save_sku`）描述，参数清单追加 3 个体积字段（标注"可选，默认 0"）
- [x] 5.7 更新 `openspec/specs/data-model/spec.md` 如有总览（金额单位约定 / 命名例外等）变化（本次预计无变化，仅 review 即可）

## 6. 业务文档更新（docs/erp_api）

- [x] 6.1 更新 `docs/erp_api/supplier/save_sku.md`：请求 / 响应字段表追加 3 个体积字段，示例 JSON 同步增加
- [x] 6.2 更新 `docs/erp_api/supplier/search_sku.md`：响应字段表追加 3 个体积字段，示例 JSON 同步增加
- [x] 6.3 更新 `docs/erp_api/README.md` 如包含字段总览（review 即可）：README 不含字段总览，无需改动

## 7. 验证

- [ ] 7.1 本地起 MySQL 应用 ALTER 脚本（首次执行 + 重复执行），确认幂等不报错 **[需运行环境]**
- [ ] 7.2 执行 `SHOW CREATE TABLE t_sku_info`，确认 3 列存在、`INT NOT NULL DEFAULT 0`、注释正确 **[需运行环境]**
- [ ] 7.3 调用 `/erp_api/supplier/save_sku`（带 `sku_pack_length=30, sku_pack_width=20, sku_pack_height=15`）→ 调用 `/erp_api/supplier/search_sku` 验证返回值正确 **[需运行环境]**
- [ ] 7.4 不传体积字段调用 `/erp_api/supplier/save_sku`（兼容性回归）→ 服务端返回 0，无报错 **[需运行环境]**
- [ ] 7.5 调用 `/erp_api/supplier/sync_all_sku`（小批量），抽样 1~2 行体积字段确认未被覆盖 **[需运行环境]**
- [x] 7.6 静态校验：`python3 -c "import ast; ast.parse(...)"` 通过 4 个改动 Python 文件（mysql_backend / supplier / sync_sku_inventory / import_sku）；`grep` 验证 `SkuDto` 中已包含 `sku_pack_length / sku_pack_width / sku_pack_height` 三个 `Mapped[int]=Column(...)` 与 `columns` 列表项；运行时 `DtoUtil.to_dict(SkuDto(...))` 测试需在含 `sqlalchemy` 的项目 venv（`ec_erp_env`）执行
- [ ] 7.7 全量回归：`search_sku` / `add_sku` / 创建采购单 / 创建销售订单链路冒烟，无新增异常 **[需运行环境]**

## 8. 上线 / 跟进

- [x] 8.1 PR review：cursorrules + openspec 文档检查（命名、注释、Change-Log、变更管理流程）—— 自检通过；详见对话中的 PR self-review checklist

