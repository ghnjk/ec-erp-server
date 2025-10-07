# 保存SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/save_sku`
- **请求方法**: POST
- **接口描述**: 保存或更新SKU信息，会从BigSeller平台同步SKU库存和详情
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | SKU编码 |
| sku_group | string | 是 | SKU分组 |
| sku_name | string | 是 | SKU名称 |
| sku_unit_name | string | 是 | SKU单位名称（如：箱、个、包） |
| sku_unit_quantity | int | 是 | SKU单位数量 |
| avg_sell_quantity | int | 是 | 平均日销量 |
| shipping_stock_quantity | int | 是 | 在途库存数量 |
| inventory_support_days | int | 是 | 库存支撑天数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 保存后的SKU对象 |
| ∟ sku | string | SKU编码 |
| ∟ sku_group | string | SKU分组 |
| ∟ sku_name | string | SKU名称 |
| ∟ sku_unit_name | string | SKU单位名称 |
| ∟ sku_unit_quantity | int | SKU单位数量 |
| ∟ inventory | int | 库存数量（从BigSeller同步） |
| ∟ avg_sell_quantity | float | 平均日销量 |
| ∟ inventory_support_days | int | 库存支撑天数 |
| ∟ shipping_stock_quantity | int | 在途库存数量 |
| ∟ erp_sku_id | string | ERP系统中的SKU ID |
| ∟ erp_sku_name | string | ERP系统中的SKU名称 |
| ∟ erp_sku_image_url | string | SKU图片URL |
| ∟ erp_sku_info | object | ERP系统中的SKU扩展信息 |
| ∟ project_id | string | 所属项目ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | SKU不存在于BigSeller系统 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "sku": "A-1-Golden-Maple leaf",
  "sku_group": "藤条/枫叶",
  "sku_name": "金色枫叶",
  "sku_unit_name": "包",
  "sku_unit_quantity": 100,
  "avg_sell_quantity": 20,
  "shipping_stock_quantity": 0,
  "inventory_support_days": 30
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "sku": "A-1-Golden-Maple leaf",
    "sku_group": "藤条/枫叶",
    "sku_name": "金色枫叶",
    "sku_unit_name": "包",
    "sku_unit_quantity": 100,
    "inventory": 4725,
    "avg_sell_quantity": 20,
    "inventory_support_days": 30,
    "shipping_stock_quantity": 0,
    "erp_sku_id": "27410427",
    "erp_sku_name": "金色枫叶1pcs",
    "erp_sku_image_url": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/xxx.jpg",
    "erp_sku_info": {},
    "project_id": "philipine"
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
  "resultMsg": "sku A-1-Golden-Maple leaf 不存在",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 从本地SKU管理器查找SKU ID
3. 如果本地没有，则从BigSeller平台加载所有SKU
4. 如果仍然找不到SKU，返回错误
5. 调用BigSeller API查询SKU详情
6. 统计所有仓库的可用库存
7. 组装SKU对象并保存到数据库
8. 返回保存后的SKU信息

## 注意事项

- SKU必须在BigSeller系统中存在
- 库存数量会实时从BigSeller同步
- ERP相关字段（erp_sku_id、erp_sku_name、erp_sku_image_url）会自动从BigSeller获取
- 如果本地SKU管理器中没有该SKU，会自动从BigSeller加载全量SKU

