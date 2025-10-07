# 获取待打印订单的物流商列表

## 接口信息

- **接口路径**: `/erp_api/warehouse/get_wait_print_order_ship_provider_list`
- **请求方法**: POST
- **接口描述**: 获取当前仓库中待打印订单的物流服务商列表及订单数量
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限

## 请求参数

无需请求参数

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ ship_provider_list | array | 物流服务商列表 |
| &nbsp;&nbsp;∟ id | int | 物流服务商ID |
| &nbsp;&nbsp;∟ name | string | 物流服务商名称 |
| &nbsp;&nbsp;∟ count | int | 该物流商的待打印订单数量 |
| &nbsp;&nbsp;∟ inCount | int | 该物流商的待打印订单数量（同count） |
| &nbsp;&nbsp;∟ platform | string | 平台：shopee/lazada等 |
| &nbsp;&nbsp;∟ providerAgentId | int | 物流代理ID |
| &nbsp;&nbsp;∟ providerChannelId | int | 物流渠道ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{}
```

## 响应示例

### 成功响应

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "ship_provider_list": [
      {
        "id": 2443914,
        "providerAgentId": 1,
        "authType": null,
        "providerChannelId": 84,
        "trackingNoRequire": null,
        "isAdditional": null,
        "isSenderName": null,
        "name": "Shopee-PH-J&T Express",
        "count": 17,
        "platform": "shopee",
        "site": null,
        "defaultDeliveryType": null,
        "deliveryType": null,
        "callType": null,
        "authId": null,
        "authTimeStr": null,
        "defaultSenderAddress": null,
        "isSupportPickupTime": null,
        "platformProviderName": null,
        "inCount": 17
      },
      {
        "id": 2482504,
        "providerAgentId": 2,
        "authType": null,
        "providerChannelId": 275,
        "trackingNoRequire": null,
        "isAdditional": null,
        "isSenderName": null,
        "name": "Lazada-PH-J&T Express PH",
        "count": 21,
        "platform": "lazada",
        "site": null,
        "defaultDeliveryType": null,
        "deliveryType": null,
        "callType": null,
        "authId": null,
        "authTimeStr": null,
        "defaultSenderAddress": null,
        "isSupportPickupTime": null,
        "platformProviderName": null,
        "inCount": 21
      }
    ]
  }
}
```

## 业务逻辑说明

1. 验证用户权限
2. 获取配置中的仓库ID
3. 调用BigSeller API查询待打印订单的物流商统计
4. 返回物流商列表，每个物流商显示待打印订单数量

## 使用场景

此接口通常用于：
- 仓库管理页面展示待打印订单概览
- 按物流商分组显示待打印订单数量
- 用户选择物流商后，可调用 `search_wait_print_order` 查询该物流商的具体订单

## 注意事项

- 数据实时从BigSeller ERP系统获取
- count和inCount字段含义相同，都表示该物流商的待打印订单数量
- 需要先配置big_seller_warehouse_id才能正确获取数据

