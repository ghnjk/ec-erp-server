# 查询 SKU 采购价格

## 接口信息

- **接口路径**: `/erp_api/supplier/query_sku_purchase_price`
- **请求方法**: POST
- **接口描述**: 按 (supplier_id, sku) 查询单条采购价
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `query_sku_purchase_price`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| supplier_id | int | 是 | 供应商 ID |
| sku | string | 是 | SKU 编码 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.unit_price | int | 单价（**单位：分**），无记录返回 0 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "supplier_id": 4,
    "sku": "A-1-Golden-Maple leaf"
  }
}
```

## 响应示例

### 有价格记录

```json
{
  "data": { "unit_price": 102 },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991949926
}
```

### 无价格记录

```json
{
  "data": { "unit_price": 0 },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991949926
}
```

## 业务逻辑说明

1. 权限校验
2. 调用 `backend.get_sku_purchase_price(supplier_id, sku)`
3. 找到记录返回 `unit_price`，否则返回 0

## 关联

- 数据表：[t_sku_purchase_price](../../../data-model/design/t_sku_purchase_price.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/query_sku_purchase_price.md](../../../../../docs/erp_api/supplier/query_sku_purchase_price.md)

## 使用场景

- 创建采购单时回填历史价格
- 选择供应商后显示参考价
- 价格比对/分析

## 注意事项

- 单位：**分**
- 历史价格来自采购单 `供应商捡货中 → 待发货` 时的自动写入
- 从未采购过该 SKU 时返回 0

## Change-Log

### 初始版本 - 查询 SKU 采购价格接口

**变更类型**：新增接口

**变更原因**：采购单创建时需要快速回查历史价格。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `query_sku_purchase_price`
- 数据表：[t_sku_purchase_price](../../../data-model/design/t_sku_purchase_price.md)
