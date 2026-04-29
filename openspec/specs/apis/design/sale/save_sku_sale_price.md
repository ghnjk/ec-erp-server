# 保存 SKU 销售价格

## 接口信息

- **接口路径**: `/erp_api/sale/save_sku_sale_price`
- **请求方法**: POST
- **接口描述**: 保存或更新 SKU 销售单价
- **权限要求**: 需要 `PMS_SALE` 权限
- **Handler**: [ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `save_sku_sale_price`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | SKU 编码（非空） |
| unit_price | float | 是 | 销售单价，**必须 > 0**（**单位：元**） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | `{}` |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（sku 空 / unit_price ≤ 0） |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "sku": "A-1-Golden-Maple leaf",
    "unit_price": 150.5
  }
}
```

## 响应示例

```json
{
  "data": {},
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

错误：

```json
{ "result": 1003, "resultMsg": "sku参数不能为空", "traceId": 1709991821760 }
```

## 业务逻辑说明

1. 权限校验
2. 校验 `sku != ""` 且 `unit_price > 0`
3. 取当前 project_id
4. `backend.store_sku_sale_price(...)` upsert
5. 返回 `pack_simple_response()`

## 关联

- 数据表：[t_sku_sale_price](../../../data-model/design/t_sku_sale_price.md)
- 模块 spec：[sale_module_spec.md](../../../sale_module_spec.md)
- 业务文档：[docs/erp_api/sales/save_sku_sale_price.md](../../../../../docs/erp_api/sales/save_sku_sale_price.md)

## 注意事项

- **金额单位：元（Float）**，与采购价的"分整数"约定不同
- 同一 (project, sku) 唯一一条记录
- project_id 自动从 session 获取

## Change-Log

### 初始版本 - 保存 SKU 销售价格

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `save_sku_sale_price`
- 数据表：`t_sku_sale_price`
