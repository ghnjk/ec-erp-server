## ADDED Requirements

### Requirement: Supplier 模块提供删除 SKU 接口
Supplier 模块 SHALL 提供 `POST /erp_api/supplier/delete_sku`，接收非空字符串参数 `sku`，校验 `PMS_SUPPLIER` 权限，并在当前项目范围内调用 Backend 完成逻辑删除。

#### Scenario: 删除接口成功响应
- **WHEN** 有权限用户提交当前项目中存在且有效的 SKU
- **THEN** 接口返回成功响应且该 SKU 被标记为已删除

#### Scenario: 删除接口参数为空
- **WHEN** 请求中的 `sku` 缺失、为空或仅包含空白字符
- **THEN** 接口返回参数错误 1003

#### Scenario: SKU 不可删除
- **WHEN** 请求中的 SKU 在当前项目中不存在或已经删除
- **THEN** 接口返回不存在错误 1004

### Requirement: Supplier SKU 查询过滤逻辑删除记录
`search_sku` SHALL 在所有筛选、排序和分页场景中先限定当前项目且未删除（`is_delete = 0` 或 `is_delete IS NULL`）。

#### Scenario: 分页总数排除已删除记录
- **WHEN** 调用 `search_sku` 查询含有逻辑删除记录的数据集
- **THEN** `data.total` 与 `data.list` 均不包含逻辑删除记录

### Requirement: Supplier 批量添加恢复已删除 SKU
`add_sku` SHALL 仅忽略当前项目中未删除的同名 SKU；同名记录已删除时 SHALL 按新增流程恢复该记录。

#### Scenario: 恢复远端存在的 SKU
- **WHEN** 批量添加的 SKU 在本地已逻辑删除且在卖家平台仍存在
- **THEN** 接口将其恢复为 `is_delete = 0`、刷新 ERP 信息并增加成功计数
