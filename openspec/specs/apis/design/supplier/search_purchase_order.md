# 搜索采购单

## 接口信息

- **接口路径**: `/erp_api/supplier/search_purchase_order`
- **请求方法**: POST
- **接口描述**: 分页查询采购单列表，按 `order_type` 过滤
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_purchase_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_type | int | 是 | 1=境内进货采购单，2=境外线下采购单 |
| current_page | int | 是 | 当前页码 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.total | int | 总记录数 |
| data.list[] | array | 采购单列表（按 purchase_order_id 倒序） |
| ∟ purchase_order_id | int | 采购单 ID |
| ∟ supplier_id / supplier_name | - | 供应商信息 |
| ∟ order_type | int | 采购单类型 |
| ∟ purchase_step | string | 采购步骤（见状态机） |
| ∟ sku_amount | int | SKU 总金额（**分**） |
| ∟ pay_amount | int | 支付金额（**分**） |
| ∟ pay_state | int | 0=未支付 / 1=已支付 |
| ∟ purchase_date | string | 采购日期 |
| ∟ expect_arrive_warehouse_date | string | 预计到仓日期 |
| ∟ arrive_warehouse_date | string | 实际到仓日期 |
| ∟ maritime_port / shipping_company / shipping_fee | string | 海运信息 |
| ∟ remark | string | 备注 |
| ∟ purchase_skus[] | array | 采购 SKU 列表 |
| &nbsp;&nbsp;∟ sku, sku_group, sku_name, quantity, unit_price | - | - |
| ∟ store_skus[] | array | 入库 SKU 列表 |
| &nbsp;&nbsp;∟ sku, sku_group, sku_name, quantity, check_in_quantity, unit_price | - | - |
| ∟ project_id, create_time, modify_time | - | 通用字段 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | order_type 参数非法 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "order_type": 1,
    "current_page": 1,
    "page_size": 10
  }
}
```

## 响应示例

```json
{
  "data": {
    "list": [
      {
        "arrive_warehouse_date": null,
        "create_time": "2024-03-02 21:51:09",
        "expect_arrive_warehouse_date": "2024-04-01",
        "maritime_port": "广州",
        "modify_time": "2024-03-02 21:53:52",
        "op_log": null,
        "order_type": 1,
        "pay_amount": 90,
        "pay_state": 1,
        "project_id": "philipine",
        "purchase_date": "2024-03-02",
        "purchase_order_id": 2,
        "purchase_skus": [
          { "quantity": 1, "sku": "A-11-Beige Reed leaf", "sku_group": "藤条/芦苇叶", "sku_name": "米色芦苇叶", "unit_price": 30 }
        ],
        "purchase_step": "完成",
        "remark": "test 1",
        "shipping_company": null,
        "shipping_fee": "0.3",
        "sku_amount": 90,
        "store_skus": [
          { "check_in_quantity": 1, "quantity": 1, "sku": "A-11-Beige Reed leaf", "sku_group": "藤条/芦苇叶", "sku_name": "米色芦苇叶", "unit_price": 30 }
        ],
        "supplier_id": 4,
        "supplier_name": "新草地厂家(麦森人造草坪）"
      }
    ],
    "total": 2
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991870811
}
```

## 业务逻辑说明

1. 权限校验
2. 校验 `order_type ∈ {1, 2}`
3. `backend.search_purchase_order(offset, page_size, order_type)`，按 `purchase_order_id DESC` 排序
4. 返回分页结果

## 状态机

### order_type=1 境内进货
```
草稿 → 供应商捡货中 → 待发货 → 海运中 → 已入库 → 完成
```

### order_type=2 境外线下
```
草稿 → 境外拣货 → 已出库 → 完成
```

## 关联

- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/search_purchase_order.md](../../../../../docs/erp_api/supplier/search_purchase_order.md)

## 注意事项

- 金额单位：**分**
- `purchase_skus` 与 `store_skus` 可能不一致（实际入库数量可能与采购数量不同）
- 自动按当前 project_id 过滤

## Change-Log

### 2024-10 - 新增 order_type 必填参数

**变更类型**：修改请求参数（不兼容）

**变更原因**：采购单分为境内进货与境外线下两类，需按类型过滤。

**变更内容**：
- `order_type` 改为必填，取值 1 或 2

**前端影响**：必须传 order_type；前端列表页应分两个 tab。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_purchase_order`
- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)（新增 `Forder_type` 字段，详见表 design 的 Change-Log）

### 初始版本 - 搜索采购单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：`ec_erp_api/apis/supplier.py` `search_purchase_order`
- 数据表：[t_purchase_order](../../../data-model/design/t_purchase_order.md)
