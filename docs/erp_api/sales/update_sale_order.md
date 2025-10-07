# 更新销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/update_sale_order`
- **请求方法**: POST
- **接口描述**: 更新现有销售订单的信息
- **权限要求**: 需要 `PMS_SALE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | int | 是 | 订单ID |
| order_date | string | 否 | 订单日期，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS |
| sku | string | 否 | 商品SKU编码 |
| unit_price | float | 否 | 单价，必须大于0 |
| quantity | int | 否 | 数量，必须大于0 |
| status | string | 否 | 订单状态（待同步、已同步） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 空对象 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（order_id无效、日期格式错误等） |
| 1004 | 订单不存在 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "order_id": 1001,
  "unit_price": 160.0,
  "quantity": 120,
  "status": "已同步"
}
```

## 响应示例

### 成功响应

```json
{
  "data": {},
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 错误响应

```json
{
  "result": 1004,
  "resultMsg": "订单不存在: 1001",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 验证订单ID参数
3. 从数据库查询现有订单
4. 如果订单不存在，返回错误
5. 根据提供的参数更新订单字段：
   - order_date：更新订单日期
   - sku：更新商品SKU
   - unit_price：更新单价
   - quantity：更新数量
   - status：更新订单状态
6. 重新计算订单总金额
7. 更新数据库记录
8. 返回成功响应

## 注意事项

- 订单ID是必填参数，其他参数都是可选的
- 只有提供的参数会被更新，未提供的参数保持不变
- 订单日期支持两种格式：`YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`
- 如果修改了unit_price或quantity，系统会自动重新计算total_amount
- 系统会自动更新modify_time字段
- 可以通过此接口修改订单状态

