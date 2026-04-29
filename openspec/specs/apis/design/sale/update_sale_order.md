# 更新销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/update_sale_order`
- **请求方法**: POST
- **接口描述**: 更新已有销售订单的字段
- **权限要求**: 需要 `PMS_SALE` 权限
- **Handler**: [ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `update_sale_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | int | 是 | 订单 ID |
| order_date | string | 否 | 订单日期 |
| sale_sku_list[] | array | 否 | 提供时必须非空，每项校验同 [create_sale_order](./create_sale_order.md) |
| status | string | 否 | 订单状态（`新建` / `已同步`） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | `{}` |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（order_id 无效、日期格式错、sale_sku_list 格式错） |
| 1004 | 订单不存在 |
| 1008 | 权限不足 |

## 请求示例

### 仅更新状态

```json
{ "body": { "order_id": 1001, "status": "已同步" } }
```

### 更新 SKU 列表

```json
{
  "body": {
    "order_id": 1001,
    "sale_sku_list": [
      { "sku": "A-1-Golden-Maple leaf", "unit_price": 160.0, "quantity": 120 }
    ]
  }
}
```

### 综合更新

```json
{
  "body": {
    "order_id": 1001,
    "order_date": "2024-10-06 10:00:00",
    "sale_sku_list": [
      { "sku": "A-1-Golden-Maple leaf", "unit_price": 160.0, "quantity": 120 }
    ],
    "status": "已同步"
  }
}
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
3. `backend._get_sale_order(session, order_id)`，校验 project_id 与 session 一致
4. 不存在 → 1004
5. 按提供字段更新：
   - `order_date`
   - `sale_sku_list`：补充 sku_group/name/url，重新计算 total_amount
   - `status`
6. `backend.update_sale_order(order)`

## 关联

- 数据表：[t_sale_order](../../../data-model/design/t_sale_order.md)
- 模块 spec：[sale_module_spec.md](../../../sale_module_spec.md)
- 业务文档：[docs/erp_api/sales/update_sale_order.md](../../../../../docs/erp_api/sales/update_sale_order.md)
- 兄弟接口：[create_sale_order](./create_sale_order.md)、[delete_sale_order](./delete_sale_order.md)

## 注意事项

- 仅支持更新当前 project 的订单
- `order_id` 必填，其他可选；未提供的字段保持不变
- 修改 `sale_sku_list` 会重算 `total_amount`
- 单位：元（Float）

## Change-Log

### 初始版本 - 更新销售订单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `update_sale_order`
- 数据表：`t_sale_order`
