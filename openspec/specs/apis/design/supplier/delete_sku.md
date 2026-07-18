# 删除 SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/delete_sku`
- **请求方法**: POST
- **接口描述**: 按当前项目和 SKU 逻辑删除 `t_sku_info` 记录
- **权限要求**: `PMS_SUPPLIER`
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `delete_sku`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | 完整 SKU；服务端去除首尾空白后校验 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | 成功时为空对象 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | SKU 为空 |
| 1004 | 当前项目中 SKU 不存在或已经删除 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "sku": "A-1-Green-Maple leaf"
  }
}
```

## 响应示例

```json
{
  "data": {},
  "result": 0,
  "resultMsg": "success",
  "traceId": 1780000000002
}
```

## 业务逻辑说明

1. 校验 `PMS_SUPPLIER` 权限。
2. 读取并 trim `sku`，空值返回 1003。
3. `backend.get_sku(sku)` 校验当前项目中的记录存在且 `is_delete != 1`。
4. `backend.delete_sku(sku)` 在事务中设置 `is_delete=1`、更新 `modify_time`。
5. 返回 `pack_response({})`。

## 关联

- 数据表：[t_sku_info](../../../data-model/design/t_sku_info.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/delete_sku.md](../../../../../docs/erp_api/supplier/delete_sku.md)

## 注意事项

- 逻辑删除，不物理删除、不级联、不调用远端卖家平台删除接口。
- `search_sku` 过滤 `is_delete != 0`；`add_sku` 可恢复已删除的同名 SKU。
- 前端精确输入 SKU 的二次确认属于交互保护，后端权威校验仍为权限、项目和 SKU 状态。

## Change-Log

### 2026-07-19 - 新增删除 SKU 接口

**变更类型**：新增接口。

**变更原因**：清理错误添加或停用的 SKU，同时保留历史关联数据。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `delete_sku`
- Backend：[ec_erp_api/models/mysql_backend.py](../../../../../ec_erp_api/models/mysql_backend.py) `delete_sku`
