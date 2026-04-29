# 创建销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/create_sale_order`
- **请求方法**: POST
- **接口描述**: 创建新的销售订单，支持多 SKU
- **权限要求**: 需要 `PMS_SALE` 权限
- **Handler**: [ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `create_sale_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_date | string | 是 | 订单日期，`YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS` |
| sale_sku_list[] | array | 是 | 销售 SKU 列表，至少 1 项 |
| ∟ sku | string | 是 | SKU 编码 |
| ∟ sku_group | string | 否 | 不传则从 t_sku_info 补充 |
| ∟ sku_name | string | 否 | 不传则从 t_sku_info 补充 |
| ∟ erp_sku_image_url | string | 否 | 不传则从 t_sku_info 补充 |
| ∟ unit_price | float | 是 | 单价，> 0（**单位：元**） |
| ∟ quantity | int | 是 | 数量，> 0 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.order_id | int | 新创建订单 ID（autoincrement） |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（必填缺失 / 无效值 / 空数组） |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "order_date": "2024-10-05 15:30:00",
    "sale_sku_list": [
      { "sku": "A-1-Golden-Maple leaf", "unit_price": 150.5, "quantity": 100 },
      { "sku": "G-1-Golden-grape leaves", "unit_price": 95.0, "quantity": 50 }
    ]
  }
}
```

## 响应示例

```json
{
  "data": { "order_id": 1001 },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

错误：

```json
{ "result": 1003, "resultMsg": "sale_sku_list参数必须是非空数组", "traceId": 1709991821760 }
```

## 业务逻辑说明

1. 权限校验
2. 校验 `order_date` 与 `sale_sku_list` 必填
3. 遍历每个 SKU 项：
   - 校验 `sku`、`unit_price > 0`、`quantity > 0`
   - 缺失 `sku_group/sku_name/erp_sku_image_url` 时从 [t_sku_info](../../../data-model/design/t_sku_info.md) 自动补充
   - 计算 `total_amount = unit_price * quantity`
4. 累加订单总金额
5. 解析订单日期（支持两种格式）
6. 取当前 project_id
7. 构造 `SaleOrder`（status=`新建`，is_delete=0）
8. `backend.create_sale_order(order)`，返回 autoincrement order_id

## 关联

- 数据表：[t_sale_order](../../../data-model/design/t_sale_order.md)、[t_sku_info](../../../data-model/design/t_sku_info.md)
- 模块 spec：[sale_module_spec.md](../../../sale_module_spec.md)
- 业务文档：[docs/erp_api/sales/create_sale_order.md](../../../../../docs/erp_api/sales/create_sale_order.md)

## 注意事项

- project_id 自动从 session 获取
- 订单日期支持两种格式
- 单价/总金额单位：**元（Float）**
- `sale_sku_list` 在 DB 中以 JSON 序列化存储

## Change-Log

### 初始版本 - 创建销售订单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `create_sale_order`
- 数据表：`t_sale_order`、`t_sku_info`
