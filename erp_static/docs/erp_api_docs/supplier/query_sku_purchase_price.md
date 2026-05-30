# 查询SKU采购价格

## 接口信息

- **接口路径**: `/erp_api/supplier/query_sku_purchase_price`
- **请求方法**: POST
- **接口描述**: 根据供应商ID和SKU编码查询单个SKU的采购价格
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| supplier_id | int | 是 | 供应商ID |
| sku | string | 是 | SKU编码 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ unit_price | int | 单价（单位：分），如果没有价格记录则返回0 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "supplier_id": 4,
  "sku": "A-1-Golden-Maple leaf"
}
```

## 响应示例

### 有价格记录

```json
{
  "data": {
    "unit_price": 102
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991949926
}
```

### 无价格记录

```json
{
  "data": {
    "unit_price": 0
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991949926
}
```

## 业务逻辑说明

1. 验证用户权限
2. 根据供应商ID和SKU查询采购价格记录
3. 如果找到记录，返回采购价格
4. 如果没有找到记录，返回单价为0

## 使用场景

此接口通常用于：
- 创建采购单时，自动填充SKU的历史采购价格
- 前端输入供应商和SKU后，显示历史价格供参考
- 采购价格比对和分析

## 注意事项

- 价格单位为"分"，显示时需要除以100转换为元
- 同一个SKU在不同供应商处可能有不同的价格
- 价格信息来自历史采购单记录
- 如果从未从该供应商采购过该SKU，会返回0

