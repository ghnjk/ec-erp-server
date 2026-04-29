# 删除销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/delete_sale_order`
- **请求方法**: POST
- **接口描述**: 逻辑删除销售订单（`is_delete = 1`）
- **权限要求**: 需要 `PMS_SALE` 权限
- **Handler**: [ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `delete_sale_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | int | 是 | 订单 ID |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | `{}` |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（order_id 无效） |
| 1004 | 订单不存在 |
| 1008 | 权限不足 |

## 请求示例

```json
{ "body": { "order_id": 1001 } }
```

## 响应示例

```json
{ "data": {}, "result": 0, "resultMsg": "success", "traceId": 1709991821760 }
```

错误：

```json
{ "result": 1004, "resultMsg": "订单不存在: 1001", "traceId": 1709991821760 }
```

## 业务逻辑说明

1. 权限校验
2. 校验 `order_id`
3. `backend.delete_sale_order(order_id)`：将 `Fis_delete = 1`、更新 `Fmodify_time`

## 关联

- 数据表：[t_sale_order](../../../data-model/design/t_sale_order.md)
- 模块 spec：[sale_module_spec.md](../../../sale_module_spec.md)
- 业务文档：[docs/erp_api/sales/delete_sale_order.md](../../../../../docs/erp_api/sales/delete_sale_order.md)

## 注意事项

- 仅逻辑删除（`is_delete = 1`），数据物理保留
- `search_sale_order` 自动过滤 `is_delete = 0`，已删除订单不可见
- 如需恢复，可直接 UPDATE 该字段为 0

## Change-Log

### 初始版本 - 删除销售订单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `delete_sale_order`
- 数据表：`t_sale_order`
