# 保存SKU销售价格

## 接口信息

- **接口路径**: `/erp_api/sale/save_sku_sale_price`
- **请求方法**: POST
- **接口描述**: 保存或更新SKU销售价格信息
- **权限要求**: 需要 `PMS_SALE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | SKU编码 |
| unit_price | float | 是 | 销售单价，必须大于0 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 空对象 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（sku为空、unit_price无效） |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "sku": "A-1-Golden-Maple leaf",
  "unit_price": 150.5
}
```

## 响应示例

### 成功响应

```json
{
  "data": {},
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 错误响应

```json
{
  "result": 1003,
  "resultMsg": "sku参数不能为空",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 验证必填参数（sku、unit_price）
3. 获取当前登录用户的项目ID
4. 创建或更新SKU销售价格记录
   - 自动关联当前项目ID
   - 如果当前项目下该SKU已存在销售价格，则更新价格
   - 如果当前项目下该SKU不存在销售价格，则创建新记录
5. 保存到数据库
6. 返回成功响应

## 注意事项

- SKU销售价格按项目隔离，不同项目的SKU价格互不影响
- 同一个项目下，同一个SKU只能有一个销售价格
- 保存时会自动更新 `modify_time` 字段
- 如果是首次保存，会设置 `create_time` 字段
- project_id 会自动从当前登录会话中获取，无需手动传入

