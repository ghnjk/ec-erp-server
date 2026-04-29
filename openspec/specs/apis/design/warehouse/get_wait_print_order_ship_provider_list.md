# 获取待打印订单的物流商列表

## 接口信息

- **接口路径**: `/erp_api/warehouse/get_wait_print_order_ship_provider_list`
- **请求方法**: POST
- **接口描述**: 获取当前仓库的待打印订单按物流商分组统计
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限
- **Handler**: [ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `get_order_statics`（**注意：函数名与路径名不一致，以路径为准**）

## 请求参数

无

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.ship_provider_list[] | array | 物流商列表 |
| ∟ id | int | 物流商 ID |
| ∟ name | string | 物流商名称（如 `Shopee-PH-J&T Express`） |
| ∟ count | int | 该物流商待打印订单数 |
| ∟ inCount | int | 同 count |
| ∟ platform | string | 平台：`shopee` / `lazada` 等 |
| ∟ providerAgentId | int | 物流代理 ID |
| ∟ providerChannelId | int | 物流渠道 ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{ "body": {} }
```

## 响应示例

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "ship_provider_list": [
      { "id": 2443914, "name": "Shopee-PH-J&T Express", "count": 17, "inCount": 17, "platform": "shopee", "providerAgentId": 1, "providerChannelId": 84 },
      { "id": 2482504, "name": "Lazada-PH-J&T Express PH", "count": 21, "inCount": 21, "platform": "lazada", "providerAgentId": 2, "providerChannelId": 275 }
    ]
  }
}
```

## 业务逻辑说明

1. 权限校验
2. 读取 `app_config.big_seller_warehouse_id`
3. 调用 BigSeller `get_wait_print_order_ship_provider_list(warehouse_id)`
4. 直接透传响应

## 关联

- 第三方：[bigseller_integration_spec.md](../../../bigseller_integration_spec.md)
- 模块 spec：[warehouse_module_spec.md](../../../warehouse_module_spec.md)
- 业务文档：[docs/erp_api/warehouse/get_wait_print_order_ship_provider_list.md](../../../../../docs/erp_api/warehouse/get_wait_print_order_ship_provider_list.md)
- 兄弟接口：[search_wait_print_order](./search_wait_print_order.md)

## 注意事项

- 数据实时来自 BigSeller，不入库
- 必须配置 `big_seller_warehouse_id`
- 函数名 `get_order_statics` 是历史遗留命名，保持现有不动

## Change-Log

### 初始版本 - 物流商待打印订单统计

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `get_order_statics`
- 第三方：BigSellerClient
