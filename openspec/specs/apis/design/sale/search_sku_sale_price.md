# 搜索 SKU 销售价格

## 接口信息

- **接口路径**: `/erp_api/sale/search_sku_sale_price`
- **请求方法**: POST
- **接口描述**: 分页搜索 SKU 销售价格，支持模糊匹配
- **权限要求**: 需要 `PMS_SALE` 权限
- **Handler**: [ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `search_sku_sale_price`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 否 | SKU 模糊匹配（空字符串视为不限制） |
| current_page | int | 否 | 默认 1 |
| page_size | int | 否 | 默认 20 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.total | int | 总记录数 |
| data.list[] | array | 销售价格列表（按 modify_time DESC） |
| ∟ project_id | string | 项目 ID |
| ∟ sku | string | SKU 编码 |
| ∟ unit_price | float | 销售单价（**单位：元**） |
| ∟ create_time / modify_time | string | 时间字段 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "sku": "Golden",
    "current_page": 1,
    "page_size": 20
  }
}
```

## 响应示例

```json
{
  "data": {
    "total": 15,
    "list": [
      {
        "project_id": "philipine",
        "sku": "A-1-Golden-Maple leaf",
        "unit_price": 150.5,
        "create_time": "2024-10-01 10:30:00",
        "modify_time": "2024-10-05 15:20:00"
      }
    ]
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 权限校验
2. `offset = (current_page - 1) * page_size`
3. `backend.search_sku_sale_price(sku, offset, page_size)`，按 `Fmodify_time DESC` 排序
4. 返回 `{total, list}`

## 关联

- 数据表：[t_sku_sale_price](../../../data-model/design/t_sku_sale_price.md)
- 模块 spec：[sale_module_spec.md](../../../sale_module_spec.md)
- 业务文档：[docs/erp_api/sales/search_sku_sale_price.md](../../../../../docs/erp_api/sales/search_sku_sale_price.md)

## 注意事项

- 自动按当前 project 过滤
- 按 modify_time 倒序，最新修改在前
- 单位：元（Float）

## Change-Log

### 初始版本 - 搜索 SKU 销售价格接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `search_sku_sale_price`
- 数据表：`t_sku_sale_price`
