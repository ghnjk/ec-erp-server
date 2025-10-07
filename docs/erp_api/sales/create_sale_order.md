# 创建销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/create_sale_order`
- **请求方法**: POST
- **接口描述**: 创建新的销售订单
- **权限要求**: 需要 `PMS_SALE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_date | string | 是 | 订单日期，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS |
| sku | string | 是 | 商品SKU编码 |
| unit_price | float | 是 | 单价，必须大于0 |
| quantity | int | 是 | 数量，必须大于0 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 响应数据 |
| ∟ order_id | int | 创建成功的订单ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（必填参数为空或无效） |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "order_date": "2024-10-05 15:30:00",
  "sku": "A-1-Golden-Maple leaf",
  "unit_price": 150.5,
  "quantity": 100
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "order_id": 1001
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 错误响应

```json
{
  "result": 1003,
  "resultMsg": "sku参数不能为空",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 验证必填参数（order_date、sku、unit_price、quantity）
3. 解析订单日期（支持两种格式）
4. 计算订单总金额 = unit_price * quantity
5. 创建销售订单对象，初始状态为"待同步"
6. 保存到数据库
7. 返回新创建的订单ID

## 注意事项

- 订单日期支持两种格式：
  - `YYYY-MM-DD`（如：2024-10-05）
  - `YYYY-MM-DD HH:MM:SS`（如：2024-10-05 15:30:00）
- 订单总金额由系统自动计算，不需要传入
- 新创建的订单默认状态为"待同步"
- order_id由数据库自动生成，为自增主键
- 系统会自动设置create_time和modify_time

