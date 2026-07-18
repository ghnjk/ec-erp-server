## ADDED Requirements

### Requirement: 按 SKU 逻辑删除
系统 SHALL 提供受 Supplier 权限保护的接口，按当前项目和 SKU 将 `t_sku_info.Fis_delete` 设置为 1，且 SHALL NOT 物理删除记录或修改远端 ERP SKU。

#### Scenario: 成功删除有效 SKU
- **WHEN** 有 Supplier 权限的用户提交当前项目中存在且未删除的 SKU
- **THEN** 系统将该 SKU 标记为已删除并返回成功

#### Scenario: 拒绝无效请求
- **WHEN** 用户未提供有效 SKU、无 Supplier 权限，或 SKU 在当前项目中不存在或已删除
- **THEN** 系统返回对应参数、权限或不存在错误且不修改数据

### Requirement: 已删除 SKU 不出现在列表
SKU 分页查询 SHALL 仅返回当前项目中未删除的记录（`Fis_delete = 0` 或 `Fis_delete IS NULL`）。

#### Scenario: 查询包含已删除 SKU 的项目
- **WHEN** 当前项目同时存在有效和已逻辑删除的 SKU
- **THEN** 查询结果和总数仅包含有效 SKU

### Requirement: 重新添加恢复 SKU
批量添加 SHALL 在同 SKU 记录已逻辑删除时重新获取 ERP 信息并将其恢复为有效记录。

#### Scenario: 添加已删除 SKU
- **WHEN** 用户批量添加当前项目中 `Fis_delete = 1` 且远端 ERP 仍存在的 SKU
- **THEN** 系统刷新其 ERP 信息、设置 `Fis_delete = 0` 并计为成功

### Requirement: 前端二次确认
SKU 列表 SHALL 在最后一列提供删除文字按钮，点击后 SHALL 展示 SKU 图片和基本信息，并要求用户精确输入目标 SKU 才能提交删除。

#### Scenario: 输入不匹配
- **WHEN** 确认输入为空或与目标 SKU 不完全一致
- **THEN** 删除确认按钮保持禁用且不发起请求

#### Scenario: 输入匹配并删除
- **WHEN** 用户输入与目标 SKU 完全一致并确认
- **THEN** 前端调用删除接口，成功后提示用户并刷新 SKU 列表
