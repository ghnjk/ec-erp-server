# 同步所有SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/sync_all_sku`
- **请求方法**: POST
- **接口描述**: 同步数据库中所有SKU的库存、销量等信息，从BigSeller平台实时更新
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

无需请求参数

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 同步结果 |
| ∟ update_count | int | 成功更新的SKU数量 |
| ∟ fail_count | int | 失败的SKU数量 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "update_count": 150,
    "fail_count": 2
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 从数据库查询当前项目的所有SKU（最多10000条）
3. 加载BigSeller的SKU映射关系
4. 对每个SKU执行以下操作：
   - 从SKU管理器获取SKU ID
   - 如果找不到，从BigSeller加载全量SKU（只加载一次）
   - 调用BigSeller API查询库存明细
   - 调用BigSeller API查询SKU详情
   - 更新以下字段：
     - inventory（库存数量）
     - erp_sku_name（ERP SKU名称）
     - erp_sku_image_url（SKU图片URL）
     - erp_sku_id（ERP SKU ID）
     - avg_sell_quantity（平均日销量）
     - inventory_support_days（库存支撑天数）
   - 保存到数据库
   - 每个SKU处理后休眠0.3秒（避免请求过快）
5. 返回更新统计

## 计算规则

- **平均日销量**: `avgDailySales * 1.1`（BigSeller的平均日销量 × 1.1）
- **库存支撑天数**: `库存数量 / 平均日销量`（如果平均日销量≤0.01，则除以0.01）

## 注意事项

- 此接口会查询所有SKU，如果数量较多会比较耗时
- 每个SKU查询间隔0.3秒，防止请求过快
- 如果某个SKU在BigSeller中找不到，会记录失败但继续处理其他SKU
- 建议在非业务高峰期执行
- 可以通过定时任务在每天固定时间自动同步（如凌晨）

