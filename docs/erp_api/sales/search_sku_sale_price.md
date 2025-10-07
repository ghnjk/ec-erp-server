# 搜索SKU销售价格

## 接口信息

- **接口路径**: `/erp_api/sale/search_sku_sale_price`
- **请求方法**: POST
- **接口描述**: 搜索和查询SKU销售价格信息，支持模糊搜索
- **权限要求**: 需要 `PMS_SALE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 否 | SKU编码（模糊搜索），为空则查询全部 |
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
| ∟ records | array | SKU销售价格列表 |
| &nbsp;&nbsp;∟ project_id | string | 所属项目ID |
| &nbsp;&nbsp;∟ sku | string | SKU编码 |
| &nbsp;&nbsp;∟ unit_price | float | 销售单价 |
| &nbsp;&nbsp;∟ create_time | string | 创建时间 |
| &nbsp;&nbsp;∟ modify_time | string | 修改时间 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "sku": "Golden",
  "current_page": 1,
  "page_size": 20
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "total": 15,
    "records": [
      {
        "project_id": "philipine",
        "sku": "A-1-Golden-Maple leaf",
        "unit_price": 150.5,
        "create_time": "2024-10-01 10:30:00",
        "modify_time": "2024-10-05 15:20:00"
      },
      {
        "project_id": "philipine",
        "sku": "A-2-Golden-Oak leaf",
        "unit_price": 180.0,
        "create_time": "2024-10-02 11:20:00",
        "modify_time": "2024-10-02 11:20:00"
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
2. 获取搜索参数（sku、分页参数）
3. 从数据库查询SKU销售价格
   - 自动过滤当前项目的数据（project_id）
   - 如果提供了sku参数，使用模糊搜索（LIKE）
   - 按修改时间倒序排列
   - 应用分页参数
4. 统计总记录数
5. 将结果转换为字典格式
6. 返回分页结果

## 注意事项

- 查询结果会自动过滤为当前登录用户所属项目的数据
- SKU参数支持模糊搜索，会匹配SKU编码中包含该关键字的所有记录
- 结果按修改时间倒序排列，最新修改的记录在最前面
- 如果不提供sku参数，会返回当前项目所有SKU的销售价格
- 分页从1开始计数

