# 搜索待打印订单

## 接口信息

- **接口路径**: `/erp_api/warehouse/search_wait_print_order`
- **请求方法**: POST
- **接口描述**: 根据物流服务商ID分页查询待打印的订单列表
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| shipping_provider_id | string | 是 | 物流服务商ID |
| current_page | int | 是 | 当前页码，从1开始 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ total | int | 总订单数 |
| ∟ list | array | 订单列表 |
| &nbsp;&nbsp;∟ id | int | 订单ID |
| &nbsp;&nbsp;∟ platformOrderId | string | 平台订单号 |
| &nbsp;&nbsp;∟ shopId | int | 店铺ID |
| &nbsp;&nbsp;∟ shopName | string | 店铺名称 |
| &nbsp;&nbsp;∟ platform | string | 平台：shopee/lazada |
| &nbsp;&nbsp;∟ viewStatus | string | 订单状态 |
| &nbsp;&nbsp;∟ packageNo | string | 包裹号 |
| &nbsp;&nbsp;∟ amount | string | 订单金额 |
| &nbsp;&nbsp;∟ amountUnit | string | 金额币种 |
| &nbsp;&nbsp;∟ buyerUsername | string | 买家用户名 |
| &nbsp;&nbsp;∟ contactPerson | string | 联系人 |
| &nbsp;&nbsp;∟ recipient | string | 收货地址 |
| &nbsp;&nbsp;∟ buyerShippingCarrier | string | 买家选择的物流 |
| &nbsp;&nbsp;∟ shippingCarrierId | int | 物流服务商ID |
| &nbsp;&nbsp;∟ shippingCarrierName | string | 物流服务商名称 |
| &nbsp;&nbsp;∟ trackingNo | string | 物流单号 |
| &nbsp;&nbsp;∟ orderCreateTime | long | 订单创建时间戳 |
| &nbsp;&nbsp;∟ orderCreateTimeStr | string | 订单创建时间字符串 |
| &nbsp;&nbsp;∟ paymentMethod | string | 支付方式 |
| &nbsp;&nbsp;∟ orderItemList | array | 订单商品列表 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ id | int | 商品项ID |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ varSku | string | 商品SKU |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ varAttr | string | 商品属性 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ quantity | int | 数量 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ image | string | 商品图片URL |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ itemPlatformState | string | 商品平台状态 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ varOriginalPrice | string | 原价 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ amount | string | 金额 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "shipping_provider_id": "2482504",
  "current_page": 1,
  "page_size": 10
}
```

## 响应示例

由于响应数据较大，这里展示简化版本。完整数据请参考 `docs/sample_response/warehouse/search_wait_print_order.json`。

### 成功响应

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
        "buyerUsername": "Emylene Buco Alfredo",
        "contactPerson": "Emylene Alfredo",
        "recipient": "Bulacan, Philippines",
        "buyerShippingCarrier": "standard - J&T Express PH",
        "shippingCarrierId": 2482504,
        "shippingCarrierName": "Lazada-PH-J&T Express PH",
        "trackingNo": "820082003415",
        "orderCreateTime": 1727679900000,
        "orderCreateTimeStr": "2024-09-30 07:05",
        "paymentMethod": "Prepaid",
        "orderItemList": [
          {
            "id": 2754347099,
            "varSku": "Yellow(CW-7)-2*4m",
            "varAttr": "2M x 4M (H2.5cm)",
            "quantity": 1,
            "image": "https://ph-live.slatic.net/p/xxx.jpg",
            "itemPlatformState": "已打包",
            "varOriginalPrice": "1821.60",
            "amount": "1821.60"
          }
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

1. 验证用户权限
2. 调用BigSeller API，根据物流服务商ID和分页参数查询待打印订单
3. 返回订单列表

## 使用场景

此接口用于：
- 仓库打单页面展示待打印订单
- 用户选择订单后，调用打印相关接口
- 查看订单详情，包括商品、收货地址、物流信息等

## 注意事项

- 数据实时从BigSeller ERP系统获取
- 订单列表按时间倒序排列
- 订单状态为"待打印"的才会返回
- orderItemList包含订单的所有商品明细

