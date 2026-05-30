# 保存采购单

## 接口信息

- **接口路径**: `/erp_api/supplier/save_purchase_order`
- **请求方法**: POST
- **接口描述**: 保存或更新采购单信息（草稿保存）
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| purchase_order_id | int | 否 | 采购单ID，新建时不传或传0 |
| supplier_id | int | 是 | 供应商ID |
| purchase_step | string | 是 | 采购步骤 |
| pay_amount | int | 否 | 支付金额（单位：分），默认0 |
| pay_state | int | 否 | 支付状态，0未支付，1已支付，默认0 |
| purchase_date | string | 否 | 采购日期，格式：YYYY-MM-DD |
| expect_arrive_warehouse_date | string | 否 | 预计到达仓库日期 |
| arrive_warehouse_date | string | 否 | 实际到达仓库日期 |
| maritime_port | string | 否 | 海运港口 |
| shipping_company | string | 否 | 物流公司 |
| shipping_fee | string | 否 | 运费 |
| remark | string | 否 | 备注 |
| purchase_skus | array | 是 | 采购SKU列表 |
| ∟ sku | string | 是 | SKU编码 |
| ∟ quantity | int | 否 | 采购数量，草稿阶段可以为null |
| ∟ unit_price | int | 是 | 单价（单位：分） |
| store_skus | array | 否 | 入库SKU列表（入库阶段使用） |
| ∟ sku | string | 是 | SKU编码 |
| ∟ quantity | int | 是 | 采购数量 |
| ∟ unit_price | int | 是 | 单价（单位：分） |
| ∟ check_in_quantity | int | 是 | 实际入库数量 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

### 新建采购单草稿

```json
{
  "purchase_order_id": 0,
  "supplier_id": 4,
  "purchase_step": "草稿",
  "pay_amount": 0,
  "pay_state": 0,
  "expect_arrive_warehouse_date": "2024-04-01",
  "maritime_port": "广州",
  "remark": "test",
  "purchase_skus": [
    {
      "sku": "A-11-Beige Reed leaf",
      "quantity": null,
      "unit_price": 30
    },
    {
      "sku": "A-11-Blue Reed leaf",
      "quantity": 10,
      "unit_price": 30
    }
  ],
  "store_skus": []
}
```

### 更新已有采购单

```json
{
  "purchase_order_id": 2,
  "supplier_id": 4,
  "purchase_step": "草稿",
  "pay_amount": 90,
  "pay_state": 1,
  "purchase_date": "2024-03-02",
  "expect_arrive_warehouse_date": "2024-04-01",
  "maritime_port": "广州",
  "shipping_fee": "0.3",
  "remark": "test 1",
  "purchase_skus": [
    {
      "sku": "A-11-Beige Reed leaf",
      "quantity": 1,
      "unit_price": 30
    }
  ],
  "store_skus": []
}
```

## 响应示例

### 成功响应

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 验证供应商是否存在
3. 验证所有SKU是否存在
4. 组装采购单对象：
   - 自动获取供应商名称
   - 补充SKU的分组、名称等信息
   - 计算SKU总金额（仅quantity不为null的）
5. 保存到数据库
6. 返回成功响应

## 采购流程说明

此接口用于草稿保存，不会改变采购单状态。如需提交并进入下一步，请使用 `/erp_api/supplier/submit_purchase_order_and_next_step` 接口。

## 注意事项

- purchase_order_id为0或不传表示新建
- 草稿阶段，purchase_skus中的quantity可以为null
- sku_amount会自动计算（quantity不为null的SKU的总金额）
- 金额单位为"分"
- 系统会自动补充SKU的详细信息（sku_group、sku_name等）
- 接口只保存，不改变采购流程状态

