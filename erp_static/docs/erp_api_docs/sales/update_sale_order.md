# 更新销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/update_sale_order`
- **请求方法**: POST
- **接口描述**: 更新现有销售订单的信息，支持更新订单日期、SKU列表、状态
- **权限要求**: 需要 `PMS_SALE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | int | 是 | 订单ID |
| order_date | string | 否 | 订单日期，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS |
| sale_sku_list | array | 否 | 销售SKU列表，如果提供则必须至少包含一个SKU项 |
| ∟ sku | string | 是 | 商品SKU编码 |
| ∟ sku_group | string | 否 | SKU分组（若不传则从数据库获取） |
| ∟ sku_name | string | 否 | 商品名称（若不传则从数据库获取） |
| ∟ erp_sku_image_url | string | 否 | 商品图片链接（若不传则从数据库获取） |
| ∟ unit_price | float | 是 | 单价，必须大于0 |
| ∟ quantity | int | 是 | 数量，必须大于0 |
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
| 1003 | 参数错误（order_id无效、日期格式错误、sale_sku_list格式错误等） |
| 1004 | 订单不存在 |
| 1008 | 权限不足 |

## 请求示例

### 示例1：更新订单状态

```json
{
  "order_id": 1001,
  "status": "已同步"
}
```

### 示例2：更新SKU列表

```json
{
  "order_id": 1001,
  "sale_sku_list": [
    {
      "sku": "A-1-Golden-Maple leaf",
      "unit_price": 160.0,
      "quantity": 120
    },
    {
      "sku": "G-1-Golden-grape leaves",
      "unit_price": 100.0,
      "quantity": 60
    }
  ]
}
```

### 示例3：更新订单日期和SKU列表

```json
{
  "order_id": 1001,
  "order_date": "2024-10-06 10:00:00",
  "sale_sku_list": [
    {
      "sku": "A-1-Golden-Maple leaf",
      "unit_price": 160.0,
      "quantity": 120
    }
  ],
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
3. 从数据库查询现有订单（自动过滤当前项目）
4. 如果订单不存在，返回错误
5. 确保订单的project_id与当前用户一致
6. 根据提供的参数更新订单字段：
   - order_date：更新订单日期
   - sale_sku_list：更新SKU列表
     - 验证每个SKU项的必填字段
     - 从数据库获取SKU信息补充缺失字段
     - 计算每个SKU的总金额
     - 重新计算订单总金额
   - status：更新订单状态
7. 更新数据库记录
8. 返回成功响应

## 注意事项

- 只能更新当前项目的订单，不同项目间的订单相互隔离
- 订单ID是必填参数，其他参数都是可选的
- 只有提供的参数会被更新，未提供的参数保持不变
- 订单日期支持两种格式：`YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`
- 如果修改了sale_sku_list，系统会自动重新计算total_amount
- sale_sku_list如果提供，必须是非空数组
- 每个SKU项必须包含sku、unit_price、quantity字段
- sku_group、sku_name、erp_sku_image_url可选，系统会自动从数据库获取补充
- 系统会自动更新modify_time字段
- 可以通过此接口修改订单状态
