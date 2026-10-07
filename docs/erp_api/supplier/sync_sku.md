# 同步单个SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/sync_sku`
- **请求方法**: POST
- **接口描述**: 从当前登录国家的 ERP 同步一个已存在 SKU 的库存、ERP 信息和日销
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | 商品 SKU，必须已经存在于当前国家且未删除 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0 表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 同步后的 SKU |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | SKU 为空，或当前国 ERP 中不存在。不会新建本地记录 |
| 1004 | 当前国家本地没有该 SKU，或已经删除 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "sku": "A-1-Golden-Maple leaf"
}
```

## 响应示例

```json
{
  "data": {
    "sku": "A-1-Golden-Maple leaf",
    "sku_group": "藤条/枫叶",
    "sku_name": "金色枫叶",
    "inventory": 4725,
    "erp_sku_name": "金色枫叶1pcs",
    "avg_sell_quantity": 22.0,
    "inventory_support_days": 214,
    "project_id": "philipine"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 校验权限，并确认本地存在未删除的 SKU。
2. 按 `sync_all_sku` 的单条规则更新库存、ERP 名称、图片、ERP SKU ID、平均日销和库存支撑天数。
3. 不修改 sku 分组、商品名、采购单位、单位的 SKU 数、打包长宽高和海运中数量。
4. ERP 中没有该 SKU 时返回错误，不新建记录。

## 注意事项

- 平均日销为 ERP 平均日销乘以 1.1。
- 库存支撑天数在平均日销大于 0.01 时用库存除以平均日销，否则用库存除以 0.01。
- 导入流程里，新增 SKU 只有在 ERP 确认存在并完成字段写入后才调用本接口。
