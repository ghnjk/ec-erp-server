## Why

SKU 列表目前缺少删除能力，错误添加或已停用的 SKU 会长期出现在主数据列表中。需要提供受权限控制的逻辑删除，并通过输入完整 SKU 的二次确认降低误删风险。

## What Changes

- 新增 `POST /erp_api/supplier/delete_sku`，按当前项目和 SKU 逻辑删除 `t_sku_info` 记录。
- `search_sku` 仅返回未删除的 SKU。
- `add_sku` 遇到已逻辑删除的同名 SKU 时恢复并刷新其 ERP 信息，而不是忽略。
- SKU 列表末列新增“删除”文字按钮；确认对话框展示 SKU 基本信息和图片，并要求用户精确输入 SKU 后才能提交。
- 同步前端 API 封装、Mock、接口文档和 OpenSpec 设计文档。

## Capabilities

### New Capabilities

- `sku-deletion`: 定义 SKU 逻辑删除、列表隐藏、重新添加恢复及前端二次确认行为。

### Modified Capabilities

- `supplier-module`: Supplier 模块新增删除 SKU 接口，并调整 SKU 查询与批量添加语义。

## Impact

- 后端：`ec_erp_api/apis/supplier.py`、`ec_erp_api/models/mysql_backend.py`
- 前端：`erp_static/src/apis/supplierApis.ts`、`erp_static/src/pages/supply/skuList.vue`
- Mock：`erp_static/mock/api/supplier.ts` 及对应响应 JSON
- 文档：`docs/erp_api/supplier/`、`docs/erp_api/README.md`、`openspec/specs/`
- 数据库不新增字段、不物理删除、不级联删除关联业务数据，也不修改 BigSeller/UpSeller 远端 SKU。
