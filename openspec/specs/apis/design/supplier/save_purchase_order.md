# 保存采购单

## 接口信息

- **接口路径**: `/erp_api/supplier/save_purchase_order`
- **请求方法**: POST
- **接口描述**: 保存或更新采购单（草稿保存，不改变状态）
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `save_purchase_order`

## 请求参数

由 `build_purchase_order_from_req()` 解析。

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_type | int | 是 | 1=境内进货 / 2=境外线下 |
| purchase_order_id | int | 否 | 0 或不传表示新建；> 0 表示更新 |
| supplier_id | int | order_type=1 必填 | order_type=2 时固定为 10000000（线下销售） |
| purchase_step | string | 是 | 当前采购步骤 |
| pay_amount | int | 否 | 支付金额（分），默认 0 |
| pay_state | int | 否 | 0/1，默认 0 |
| purchase_date | string | 否 | YYYY-MM-DD |
| expect_arrive_warehouse_date | string | 否 | 预计到仓日期 |
| arrive_warehouse_date | string | 否 | 实际到仓日期 |
| maritime_port | string | 否 | 海运港口 |
| shipping_company | string | 否 | 物流公司 |
| shipping_fee | string | 否 | 海运费 |
| remark | string | 否 | 备注 |
| purchase_skus[] | array | 是 | 采购 SKU 列表 |
| ∟ sku | string | 是 | SKU 编码 |
| ∟ quantity | int | 否（草稿可为 null） | 采购数量 |
| ∟ unit_price | int | 是 | 单价（**分**） |
| store_skus[] | array | 否 | 入库 SKU 列表（入库阶段使用） |
| ∟ sku | string | 是 | SKU 编码 |
| ∟ quantity | int | 是 | 采购数量 |
| ∟ check_in_quantity | int | 是 | 实际入库数量 |
| ∟ unit_price | int | 是 | 单价（**分**） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 通常为空 `{}` |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误（如 supplier 不存在、SKU 不存在） |
| 1008 | 权限不足 |

## 请求示例

### 新建草稿

```json
{
  "body": {
    "order_type": 1,
    "purchase_order_id": 0,
    "supplier_id": 4,
    "purchase_step": "草稿",
    "pay_amount": 0,
    "pay_state": 0,
    "expect_arrive_warehouse_date": "2024-04-01",
    "maritime_port": "广州",
    "remark": "test",
    "purchase_skus": [
      { "sku": "A-11-Beige Reed leaf", "quantity": null, "unit_price": 30 },
      { "sku": "A-11-Blue Reed leaf", "quantity": 10, "unit_price": 30 }
    ],
    "store_skus": []
  }
}
```

### 更新已有

```json
{
  "body": {
    "order_type": 1,
    "purchase_order_id": 2,
    "supplier_id": 4,
    "purchase_step": "草稿",
    "pay_amount": 90,
    "pay_state": 1,
    "purchase_date": "2024-03-02",
    "shipping_fee": "0.3",
    "purchase_skus": [
      { "sku": "A-11-Beige Reed leaf", "quantity": 1, "unit_price": 30 }
    ],
    "store_skus": []
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

## 业务逻辑说明

1. 权限校验
2. `build_purchase_order_from_req()`：
   - 校验 `order_type` 取值
   - 校验 supplier 存在（type=1）
   - 校验所有 SKU 存在
   - 自动补充 supplier_name、SKU 分组/名称
   - 计算 `sku_amount = sum(quantity * unit_price)`（仅 quantity 不为 null）
3. `backend.store_purchase_order(order)`：upsert
4. 返回成功

## 关联

- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/save_purchase_order.md](../../../../../docs/erp_api/supplier/save_purchase_order.md)
- 兄弟接口：[submit_purchase_order_and_next_step](./submit_purchase_order_and_next_step.md)

## 注意事项

- 本接口**不**改变 `purchase_step`，仅做数据保存
- 如需推进状态机，使用 `submit_purchase_order_and_next_step`
- 草稿阶段 `quantity` 可为 null
- `sku_amount` 自动计算
- 金额单位：**分**

## Change-Log

### 2024-10 - 新增 order_type 必填参数

**变更类型**：修改请求参数（不兼容）

**变更原因**：支持境外线下采购单类型。

**前端影响**：必须传 order_type。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `save_purchase_order`、`build_purchase_order_from_req`
- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)

### 初始版本 - 保存采购单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：`ec_erp_api/apis/supplier.py` `save_purchase_order`
- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)
