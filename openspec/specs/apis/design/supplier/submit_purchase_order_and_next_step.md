# 提交采购单并进入下一步

## 接口信息

- **接口路径**: `/erp_api/supplier/submit_purchase_order_and_next_step`
- **请求方法**: POST
- **接口描述**: 保存采购单并自动推进到下一个采购步骤；从「已入库」到「完成」时同步入库到 BigSeller ERP
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `submit_purchase_order_and_next_step`

## 请求参数

请求体结构与 [save_purchase_order](./save_purchase_order.md) 一致，由 `build_purchase_order_from_req()` 共同解析。关键字段：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_type | int | 是 | 1=境内进货 / 2=境外线下 |
| purchase_step | string | 是 | 当前采购步骤（决定推进到哪一步） |
| 其他字段 | - | - | 见 save_purchase_order |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | 推进后的完整 PurchaseOrder DTO（字段同 search_purchase_order 列表项） |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误 |
| 1004 | 业务逻辑错误（如存在未确定数量的 SKU、状态非法） |
| 1008 | 业务执行失败（DB 异常 / BigSeller 入库失败） |

## 状态机推进规则（order_type=1 境内进货）

| 当前步骤 | 下一步 | 推进时操作 | 校验要求 |
|----------|--------|------------|----------|
| 草稿 | 供应商捡货中 | 去除 quantity=0 的 SKU | - |
| 供应商捡货中 | 待发货 | 保存供应价 (`store_sku_purchase_price`)；设置 `purchase_date = 今天` | 所有 `purchase_skus.quantity` 不能为 null |
| 待发货 | 海运中 | 复制 purchase_skus 到 store_skus；`check_in_quantity = quantity` | 海运信息（maritime_port、shipping_company、expect_arrive_warehouse_date）必填 |
| 海运中 | 已入库 | 更新 `store_skus.check_in_quantity` | `arrive_warehouse_date` 必填 |
| 已入库 | 完成 | 调用 BigSeller `add_stock_to_erp` 创建入库单 | `store_skus` 非空 |

## 状态机推进规则（order_type=2 境外线下）

| 当前步骤 | 下一步 | 推进时操作 |
|----------|--------|------------|
| 草稿 | 境外拣货 | 去除 quantity=0 的 SKU |
| 境外拣货 | 已出库 | 调用 BigSeller 出库扣减库存 |
| 已出库 | 完成 | - |

## 请求示例

### 草稿 → 供应商捡货中

```json
{
  "body": {
    "order_type": 1,
    "purchase_order_id": 2,
    "supplier_id": 4,
    "purchase_step": "草稿",
    "purchase_skus": [
      { "sku": "A-11-Beige Reed leaf", "quantity": 10, "unit_price": 30 }
    ],
    "remark": "test"
  }
}
```

### 已入库 → 完成（同步 ERP）

```json
{
  "body": {
    "order_type": 1,
    "purchase_order_id": 2,
    "supplier_id": 4,
    "purchase_step": "已入库",
    "purchase_skus": [...],
    "store_skus": [
      { "sku": "A-11-Beige Reed leaf", "quantity": 10, "check_in_quantity": 10, "unit_price": 30 }
    ]
  }
}
```

## 响应示例

### 成功

```json
{
  "data": {
    "purchase_order_id": 2,
    "supplier_id": 4,
    "supplier_name": "新草地厂家(麦森人造草坪）",
    "purchase_step": "供应商捡货中",
    "order_type": 1,
    "sku_amount": 300,
    "pay_amount": 0,
    "pay_state": 0,
    "expect_arrive_warehouse_date": "2024-04-01",
    "maritime_port": "广州",
    "purchase_skus": [
      { "sku": "A-11-Beige Reed leaf", "sku_group": "藤条/芦苇叶", "sku_name": "米色芦苇叶", "quantity": 10, "unit_price": 30 }
    ],
    "store_skus": [],
    "project_id": "philipine"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 错误（业务校验失败）

```json
{ "result": 1004, "resultMsg": "存在未确定数量的sku", "traceId": 1709991821760 }
```

## 同步到 ERP 的逻辑（已入库 → 完成）

1. 调用 BigSeller `add_stock_to_erp` 创建入库单
2. 入库单备注格式：`ec-erp 采购单：{purchase_order_id} [入库单=IN-EC-{purchase_order_id}]`
3. 对每个 `store_sku`：
   - 价格转换：`unit_price / 100`（分→元）
   - 入库数量：`check_in_quantity * sku_unit_quantity`
4. 失败抛异常并返回 1008，**状态保持不变**

## 关联

- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)、[t_sku_purchase_price](../../../data-model/design/t_sku_purchase_price.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/submit_purchase_order_and_next_step.md](../../../../../docs/erp_api/supplier/submit_purchase_order_and_next_step.md)
- 第三方：[bigseller_integration_spec.md](../../../bigseller_integration_spec.md)
- 兄弟接口：[save_purchase_order](./save_purchase_order.md)

## 注意事项

- 每次只前进一步，不能跨步骤
- "已入库 → 完成" 调用 BigSeller，可能失败；失败时状态不变
- "供应商捡货中 → 待发货" 会自动写入 `t_sku_purchase_price`（更新历史价）
- 状态流转**不可逆**，操作前需要二次确认

## Change-Log

### 2024-10 - 新增 order_type 与 type=2 状态机

**变更类型**：修改请求参数 + 业务逻辑（不兼容）

**变更原因**：支持境外线下采购单（order_type=2），独立的状态机分支。

**前端影响**：前端必须传 order_type；type=2 的状态步骤不同。

**关联代码改动**：
- handler：`ec_erp_api/apis/supplier.py` `submit_purchase_order_and_next_step`、`_submit_purchase_order_type1`、`_submit_purchase_order_type2`
- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)

### 初始版本 - 提交采购单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：`ec_erp_api/apis/supplier.py` `submit_purchase_order_and_next_step`
