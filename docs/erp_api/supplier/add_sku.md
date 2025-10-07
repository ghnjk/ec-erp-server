# 批量添加SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/add_sku`
- **请求方法**: POST
- **接口描述**: 批量添加SKU，从BigSeller平台同步SKU信息和库存，自动计算平均销量和库存支撑天数
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skus | string | 是 | SKU编码列表，每行一个SKU，支持换行分隔 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 操作结果 |
| ∟ success_count | int | 成功添加的数量 |
| ∟ ignore_count | int | 忽略的数量（已存在） |
| ∟ fail_count | int | 失败的数量 |
| ∟ detail | object | 详细结果，key为SKU编码，value为操作结果 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "skus": "A-1-Golden-Maple leaf\nA-1-Green-Maple leaf\nA-1-Red-Maple leaf"
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "success_count": 2,
    "ignore_count": 1,
    "fail_count": 0,
    "detail": {
      "A-1-Golden-Maple leaf": "ignored",
      "A-1-Green-Maple leaf": "success",
      "A-1-Red-Maple leaf": "success"
    }
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 部分失败响应

```json
{
  "data": {
    "success_count": 1,
    "ignore_count": 1,
    "fail_count": 1,
    "detail": {
      "A-1-Golden-Maple leaf": "ignored",
      "A-1-Green-Maple leaf": "success",
      "INVALID-SKU": "sku INVALID-SKU 不存在"
    }
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 解析输入的SKU列表（按换行符分隔）
3. 对每个SKU执行以下操作：
   - 检查数据库中是否已存在，存在则忽略
   - 从本地SKU管理器查找SKU ID
   - 如果找不到，从BigSeller加载全量SKU（只加载一次）
   - 查询BigSeller获取SKU详情和库存
   - 查询BigSeller获取库存明细，计算平均日销量
   - 计算库存支撑天数
   - 保存到数据库
4. 返回操作统计结果和详细信息

## 计算规则

- **平均日销量**: `avgDailySales * 1.1`（BigSeller的平均日销量 × 1.1）
- **库存支撑天数**: `库存数量 / 平均日销量`（如果平均日销量≤0.01，则除以0.01）

## 默认值说明

批量添加时，以下字段使用默认值：
- `sku_group`: "待定"
- `sku_name`: ""（空字符串）
- `sku_unit_name`: ""（空字符串）
- `sku_unit_quantity`: 1
- `shipping_stock_quantity`: 0

## 注意事项

- SKU必须在BigSeller系统中存在
- 已存在的SKU不会重复添加
- 库存数据实时从BigSeller同步
- 自动计算平均销量和库存支撑天数
- 如果某个SKU添加失败，不影响其他SKU的添加
- 建议后续通过`save_sku`接口完善SKU的分组、名称等信息

