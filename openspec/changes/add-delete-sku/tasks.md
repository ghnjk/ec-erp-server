## 1. 后端逻辑删除

- [x] 1.1 在 `MysqlBackend` 新增按当前项目和 SKU 逻辑删除的方法
- [x] 1.2 在 Supplier Blueprint 新增 `POST /delete_sku`，完成权限、参数和存在性校验
- [x] 1.3 修改 `search_sku`，过滤 `is_delete != 0` 的记录
- [x] 1.4 修改 `add_sku`，忽略有效同名 SKU，并恢复已逻辑删除的同名 SKU

## 2. 前端与 Mock

- [x] 2.1 在 `supplierApis.ts` 增加带请求类型的 `deleteSku` 封装
- [x] 2.2 在 Supplier Mock 注册删除接口并增加成功响应 JSON
- [x] 2.3 在 SKU 列表末列增加必显的“删除”文字按钮
- [x] 2.4 实现删除确认对话框，展示图片和基本信息，精确输入 SKU 后才允许提交
- [x] 2.5 删除成功后提示并刷新当前 SKU 列表

## 3. 文档同步

- [x] 3.1 新增 `docs/erp_api/supplier/delete_sku.md` 并更新 API README 索引
- [x] 3.2 新增 OpenSpec `delete_sku` API 设计文档
- [x] 3.3 更新 Supplier 模块、`search_sku`、`add_sku` 和 `t_sku_info` 设计文档

## 4. 验证

- [x] 4.1 运行 OpenSpec 校验并确认变更达到 apply-ready
- [x] 4.2 运行 Python 语法检查及相关后端测试
- [x] 4.3 运行前端 lint、类型/构建检查并确认无新增诊断
