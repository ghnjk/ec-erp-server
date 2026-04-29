# 搜索待打印订单

## 接口信息

- **接口路径**: `/erp_api/warehouse/search_wait_print_order`
- **请求方法**: POST
- **接口描述**: 按物流商 ID 分页查询待打印订单
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限
- **Handler**: [ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `search_wait_print_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| shipping_provider_id | string | 是 | 物流商 ID |
| current_page | int | 是 | 当前页码 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.total | int | 总订单数 |
| data.list[] | array | 订单列表（裁剪字段） |
| ∟ id | int | 订单 ID |
| ∟ platformOrderId | string | 平台订单号 |
| ∟ shopId / shopName | - | 店铺信息 |
| ∟ platform | string | shopee / lazada |
| ∟ viewStatus | string | 订单状态 |
| ∟ packageNo | string | 包裹号 |
| ∟ amount / amountUnit | - | 订单金额与币种 |
| ∟ buyerUsername / contactPerson / recipient | - | 收货信息 |
| ∟ buyerShippingCarrier | string | 买家选择的物流 |
| ∟ shippingCarrierId / shippingCarrierName | - | 物流商 |
| ∟ trackingNo | string | 物流单号 |
| ∟ orderCreateTime / orderCreateTimeStr | - | 订单时间 |
| ∟ paymentMethod | string | 支付方式 |
| ∟ orderItemList[] | array | 商品明细 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "shipping_provider_id": "2482504",
    "current_page": 1,
    "page_size": 10
  }
}
```

## 响应示例

```json
{
  "data": {
    "list": [
      {
        "id": 5133175528,
        "shopId": 2100179,
        "shopName": "Green lawn (09204889221)",
        "platformOrderId": "908069598574548",
        "platform": "lazada",
        "viewStatus": "To Ship",
        "packageNo": "BS8H16335832",
        "amount": "1890.80",
        "amountUnit": "PHP",
        "buyerShippingCarrier": "standard - J&T Express PH",
        "shippingCarrierId": 2482504,
        "shippingCarrierName": "Lazada-PH-J&T Express PH",
        "trackingNo": "820082003415",
        "orderCreateTime": 1727679900000,
        "orderCreateTimeStr": "2024-09-30 07:05",
        "orderItemList": [
          { "id": 2754347099, "varSku": "Yellow(CW-7)-2*4m", "varAttr": "2M x 4M (H2.5cm)", "quantity": 1, "image": "https://...", "varOriginalPrice": "1821.60", "amount": "1821.60" }
        ]
      }
    ],
    "total": 171
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991729751
}
```

## 业务逻辑说明

1. 权限校验
2. 调用 BigSeller `search_wait_print_order(shipping_provider_id, page, page_size)`
3. 裁剪部分敏感字段，返回 `{total, list}`

## 关联

- 第三方：[bigseller_integration_spec.md](../../../bigseller_integration_spec.md)
- 模块 spec：[warehouse_module_spec.md](../../../warehouse_module_spec.md)
- 业务文档：[docs/erp_api/warehouse/search_wait_print_order.md](../../../../../docs/erp_api/warehouse/search_wait_print_order.md)

## 注意事项

- 数据实时来自 BigSeller，不入库
- 订单按时间倒序
- 仅状态为「待打印」的返回

## Change-Log

### 初始版本 - 搜索待打印订单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `search_wait_print_order`
- 第三方：BigSellerClient
