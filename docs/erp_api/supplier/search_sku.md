# 搜索SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/search_sku`
- **请求方法**: POST
- **接口描述**: 根据多个条件搜索SKU商品列表，支持分页和排序
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码，从1开始 |
| page_size | int | 是 | 每页记录数 |
| sku | string | 否 | SKU编码，模糊匹配 |
| sku_group | string | 否 | SKU分组名称，模糊匹配 |
| sku_name | string | 否 | SKU名称，模糊匹配 |
| inventory_support_days | int | 否 | 库存支撑天数，默认0（不限制） |
| sort | array | 否 | 排序规则数组 |

### 排序参数说明

sort数组中每个元素包含：
- `field`: 排序字段名
- `order`: 排序方向，`asc`升序或`desc`降序

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ total | int | 总记录数 |
| ∟ list | array | SKU列表 |
| &nbsp;&nbsp;∟ sku | string | SKU编码 |
| &nbsp;&nbsp;∟ sku_group | string | SKU分组 |
| &nbsp;&nbsp;∟ sku_name | string | SKU名称 |
| &nbsp;&nbsp;∟ sku_unit_name | string | SKU单位名称 |
| &nbsp;&nbsp;∟ sku_unit_quantity | int | SKU单位数量 |
| &nbsp;&nbsp;∟ inventory | int | 库存数量 |
| &nbsp;&nbsp;∟ avg_sell_quantity | float | 平均日销量 |
| &nbsp;&nbsp;∟ inventory_support_days | int | 库存支撑天数 |
| &nbsp;&nbsp;∟ shipping_stock_quantity | int | 在途库存数量 |
| &nbsp;&nbsp;∟ erp_sku_id | string | ERP系统中的SKU ID |
| &nbsp;&nbsp;∟ erp_sku_name | string | ERP系统中的SKU名称 |
| &nbsp;&nbsp;∟ erp_sku_image_url | string | SKU图片URL |
| &nbsp;&nbsp;∟ erp_sku_info | object | ERP系统中的SKU扩展信息 |
| &nbsp;&nbsp;∟ project_id | string | 所属项目ID |
| &nbsp;&nbsp;∟ create_time | string | 创建时间 |
| &nbsp;&nbsp;∟ modify_time | string | 修改时间 |
| &nbsp;&nbsp;∟ modify_user | string | 修改人 |
| &nbsp;&nbsp;∟ is_delete | int | 是否删除 |
| &nbsp;&nbsp;∟ version | int | 版本号 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

### 基本查询
```json
{
  "current_page": 1,
  "page_size": 10
}
```

### 带条件查询
```json
{
  "current_page": 1,
  "page_size": 10,
  "sku": "A-1",
  "sku_group": "藤条",
  "inventory_support_days": 30,
  "sort": [
    {
      "field": "inventory_support_days",
      "order": "asc"
    }
  ]
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "list": [
      {
        "avg_sell_quantity": 18.4286,
        "create_time": "2024-03-01 22:33:04",
        "erp_sku_id": "27410427",
        "erp_sku_image_url": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/20230603074446b4bf29067f2227517d260057c6385011.jpg?imageView2/1/w/300/h/300",
        "erp_sku_info": {},
        "erp_sku_name": "金色枫叶1pcs",
        "inventory": 4725,
        "inventory_support_days": 256,
        "is_delete": null,
        "modify_time": "2024-03-09 08:00:03",
        "modify_user": null,
        "project_id": "philipine",
        "shipping_stock_quantity": 0,
        "sku": "A-1-Golden-Maple leaf",
        "sku_group": "藤条/枫叶",
        "sku_name": "金色枫叶",
        "sku_unit_name": "",
        "sku_unit_quantity": 1,
        "version": null
      }
    ],
    "total": 1
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 解析查询条件（如果为空字符串则转为None）
3. 根据条件查询数据库
4. 支持多字段模糊搜索
5. 支持按库存支撑天数筛选
6. 支持多字段排序
7. 返回分页结果

## 注意事项

- 所有字符串类型的查询条件支持模糊匹配
- 空字符串会被转换为None，表示不限制该条件
- 库存支撑天数 = 库存数量 / 平均日销量
- 接口会自动过滤当前项目的数据

