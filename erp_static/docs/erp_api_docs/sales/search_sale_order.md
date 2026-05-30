# 搜索销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/search_sale_order`
- **请求方法**: POST
- **接口描述**: 搜索和查询销售订单，支持多条件筛选，只返回未删除的订单
- **权限要求**: 需要 `PMS_SALE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 订单状态（待同步、已同步） |
| begin_date | string | 否 | 开始日期，格式：YYYY-MM-DD |
| end_date | string | 否 | 结束日期，格式：YYYY-MM-DD |
| current_page | int | 否 | 当前页码，默认为1 |
| page_size | int | 否 | 每页大小，默认为20 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 分页数据 |
| ∟ total | int | 总记录数 |
| ∟ list | array | 销售订单列表 |
| &nbsp;&nbsp;∟ order_id | int | 订单ID |
| &nbsp;&nbsp;∟ order_date | string | 订单日期 |
| &nbsp;&nbsp;∟ sale_sku_list | array | 销售SKU列表 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku | string | 商品SKU |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku_group | string | SKU分组 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku_name | string | 商品名称 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ erp_sku_image_url | string | 商品图片链接 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ unit_price | float | 单价 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ quantity | int | 数量 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ total_amount | float | 该SKU总金额 |
| &nbsp;&nbsp;∟ total_amount | float | 订单总金额 |
| &nbsp;&nbsp;∟ status | string | 订单状态 |
| &nbsp;&nbsp;∟ is_delete | int | 是否删除（0：未删除，1：已删除） |
| &nbsp;&nbsp;∟ create_time | string | 创建时间 |
| &nbsp;&nbsp;∟ modify_time | string | 修改时间 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

### 示例1：搜索特定日期范围的订单

```json
{
  "begin_date": "2024-10-01",
  "end_date": "2024-10-31",
  "current_page": 1,
  "page_size": 20
}
```

### 示例2：搜索待同步的订单

```json
{
  "status": "待同步",
  "current_page": 1,
  "page_size": 20
}
```

## 响应示例

### 成功响应

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
          },
          {
            "sku": "G-1-Golden-grape leaves",
            "sku_group": "G-Golden",
            "sku_name": "Golden grape leaves",
            "erp_sku_image_url": "https://example.com/images/grape.jpg",
            "unit_price": 95.0,
            "quantity": 50,
            "total_amount": 4750.0
          }
        ],
        "total_amount": 19800.0,
        "status": "已同步",
        "is_delete": 0,
        "create_time": "2024-10-05 15:30:00",
        "modify_time": "2024-10-05 16:20:00"
      },
      {
        "order_id": 1000,
        "order_date": "2024-10-04 10:15:00",
        "sale_sku_list": [
          {
            "sku": "A-2-Golden-Oak leaf",
            "sku_group": "A-Golden",
            "sku_name": "Golden Oak leaf",
            "erp_sku_image_url": "https://example.com/images/oak.jpg",
            "unit_price": 180.0,
            "quantity": 50,
            "total_amount": 9000.0
          }
        ],
        "total_amount": 9000.0,
        "status": "待同步",
        "is_delete": 0,
        "create_time": "2024-10-04 10:15:00",
        "modify_time": "2024-10-04 10:15:00"
      }
    ]
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 错误响应

```json
{
  "result": 1008,
  "resultMsg": "权限不足",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 获取搜索条件：
   - status：精确匹配订单状态
   - begin_date：订单日期大于等于开始日期
   - end_date：订单日期小于等于结束日期
3. 构建查询条件：
   - 自动过滤当前项目的订单（project_id）
   - 自动过滤is_delete=0的订单
4. 从数据库查询符合条件的订单
5. 按订单ID倒序排列
6. 应用分页参数
7. 统计总记录数
8. 将结果转换为字典格式，并将sale_sku_list从JSON字符串解析为数组
9. 返回分页结果

## 注意事项

- 查询结果会自动过滤为当前登录用户所属项目的订单
- 所有搜索条件都是可选的，不提供任何条件将返回当前项目所有未删除的订单
- 不再支持按SKU搜索（因为sale_sku_list是JSON字段，模糊搜索性能差）
- status参数是精确匹配，可选值：待同步、已同步
- begin_date和end_date可以单独使用或组合使用
- 日期筛选使用订单日期（order_date）字段
- 结果按订单ID倒序排列，最新的订单在最前面
- 分页从1开始计数
- 多个搜索条件之间是AND关系
- 只返回is_delete=0的订单，已删除的订单不会出现在结果中
- sale_sku_list字段在响应中已解析为数组，可直接使用
