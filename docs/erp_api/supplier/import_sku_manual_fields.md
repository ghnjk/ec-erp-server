# 导入SKU可编辑字段

## 接口信息

- **接口路径**: `/erp_api/supplier/import_sku_manual_fields`
- **请求方法**: POST
- **接口描述**: 只写入商品 SKU 的可编辑字段，不从文件或请求中更新库存、日销、海运中数量和 ERP 展示字段
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | 商品 SKU |
| sku_group | string | 是 | sku 分组 |
| sku_name | string | 是 | 商品名 |
| sku_unit_name | string | 是 | 采购单位 |
| sku_unit_quantity | int | 是 | 单位的 SKU 数，必须大于 0 |
| sku_pack_length | int | 否 | 打包长（cm），默认 0 |
| sku_pack_width | int | 否 | 打包宽（cm），默认 0 |
| sku_pack_height | int | 否 | 打包高（cm），默认 0 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0 表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 写入后的 SKU |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 可编辑字段不合法，或当前国 ERP 没有该 SKU，因此未插入、未恢复 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "sku": "A-1-Golden-Maple leaf",
  "sku_group": "藤条/枫叶",
  "sku_name": "金色枫叶",
  "sku_unit_name": "包",
  "sku_unit_quantity": 100,
  "sku_pack_length": 30,
  "sku_pack_width": 20,
  "sku_pack_height": 15
}
```

## 响应示例

```json
{
  "data": {
    "sku": "A-1-Golden-Maple leaf",
    "sku_group": "藤条/枫叶",
    "sku_name": "金色枫叶",
    "sku_unit_name": "包",
    "sku_unit_quantity": 100,
    "sku_pack_length": 30,
    "sku_pack_width": 20,
    "sku_pack_height": 15,
    "inventory": 0,
    "avg_sell_quantity": 0,
    "inventory_support_days": 0,
    "shipping_stock_quantity": 0,
    "erp_sku_id": "",
    "erp_sku_name": "",
    "erp_sku_image_url": "",
    "project_id": "philipine"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 校验权限和可编辑字段。
2. 当前国家已有未删除记录时，只更新 7 个可编辑字段，库存和 ERP 字段保持原值，不访问 ERP。
3. 当前国家没有记录，或记录已逻辑删除时，先查询当前国 ERP。ERP 没有该 SKU 则返回错误，不插入、不恢复。
4. ERP 有该 SKU 时才插入新记录或恢复已删除记录。新记录的库存、日销、海运中数量和 ERP 字段先写空或 0，由 `/sync_sku` 再填充。

## 注意事项

- 不读取请求中的库存、日销、BigSeller 商品名等同步字段。
- 跨国家导入时写入的是当前登录国家，不是文件名中的国家。
