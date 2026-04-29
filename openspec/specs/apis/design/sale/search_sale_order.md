# 搜索销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/search_sale_order`
- **请求方法**: POST
- **接口描述**: 多条件分页查询销售订单，自动过滤已删除订单
- **权限要求**: 需要 `PMS_SALE` 权限
- **Handler**: [ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `search_sale_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 订单状态精确匹配（`新建` / `已同步`） |
| begin_date | string | 否 | 开始日期 `YYYY-MM-DD` |
| end_date | string | 否 | 结束日期 `YYYY-MM-DD` |
| current_page | int | 否 | 默认 1 |
| page_size | int | 否 | 默认 20 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.total | int | 总记录数 |
| data.list[] | array | 订单列表（按 `Forder_id DESC`） |
| ∟ order_id | int | 订单 ID |
| ∟ order_date | string | 订单日期 |
| ∟ sale_sku_list[] | array | SKU 清单（已解析为数组） |
| &nbsp;&nbsp;∟ sku, sku_group, sku_name, erp_sku_image_url, unit_price, quantity, total_amount | - | - |
| ∟ total_amount | float | 订单总金额（**单位：元**） |
| ∟ status | string | 状态 |
| ∟ is_delete | int | 0=未删除 |
| ∟ create_time / modify_time | string | 时间字段 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

### 按日期范围

```json
{
  "body": {
    "begin_date": "2024-10-01",
    "end_date": "2024-10-31",
    "current_page": 1,
    "page_size": 20
  }
}
```

### 按状态

```json
{
  "body": {
    "status": "新建",
    "current_page": 1,
    "page_size": 20
  }
}
```

## 响应示例

```json
{
  "data": {
    "total": 25,
    "list": [
      {
        "order_id": 1001,
        "order_date": "2024-10-05 15:30:00",
        "sale_sku_list": [
          {
            "sku": "A-1-Golden-Maple leaf",
            "sku_group": "A-Golden",
            "sku_name": "Golden Maple leaf",
            "erp_sku_image_url": "https://example.com/images/maple.jpg",
            "unit_price": 150.5,
            "quantity": 100,
            "total_amount": 15050.0
          }
        ],
        "total_amount": 15050.0,
        "status": "已同步",
        "is_delete": 0,
        "create_time": "2024-10-05 15:30:00",
        "modify_time": "2024-10-05 16:20:00"
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
2. 解析查询条件（空字符串视为不限制）
3. `backend.search_sale_order(status, begin_date, end_date, offset, page_size)`：
   - 自动过滤 `Fis_delete = 0`
   - 自动按 project_id 过滤
   - 按 `Forder_id DESC` 排序
4. 解析 `sale_sku_list` 字符串为数组
5. 返回 `{total, list}`

## 关联

- 数据表：[t_sale_order](../../../data-model/design/t_sale_order.md)
- 模块 spec：[sale_module_spec.md](../../../sale_module_spec.md)
- 业务文档：[docs/erp_api/sales/search_sale_order.md](../../../../../docs/erp_api/sales/search_sale_order.md)

## 注意事项

- 已删除订单不会出现在结果中
- 不支持按 SKU 模糊搜索（JSON 字段性能差）
- 按 order_id 倒序，最新订单在前
- 多条件 AND 关系
- 单位：元（Float）

## Change-Log

### 初始版本 - 搜索销售订单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `search_sale_order`
- 数据表：`t_sale_order`
