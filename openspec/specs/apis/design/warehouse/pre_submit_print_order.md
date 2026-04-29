# 预提交打印订单

## 接口信息

- **接口路径**: `/erp_api/warehouse/pre_submit_print_order`
- **请求方法**: POST
- **接口描述**: 预处理打印任务，解析订单 SKU 并检查拣货备注完整性
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限
- **Handler**: [ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `pre_submit_print_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_list | array | 是 | 订单列表，来自 [search_wait_print_order](./search_wait_print_order.md) 的响应 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.task_id | string | 所有 SKU 拣货备注齐全时返回 task_id；否则为 null |
| data.need_manual_mark_sku_list[] | array | 需要补录拣货备注的 SKU |
| ∟ sku | string | SKU 编码 |
| ∟ image_url | string | SKU 图片 URL |
| ∟ desc | string | 案例说明 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "order_list": [
      {
        "id": 5133175528,
        "shopId": 2100179,
        "platformOrderId": "908069598574548",
        "orderItemList": [
          { "varSku": "Yellow(CW-7)-2*4m", "quantity": 1 }
        ]
      }
    ]
  }
}
```

## 响应示例

### 拣货备注齐全

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "task_id": "172766506566",
    "need_manual_mark_sku_list": []
  }
}
```

### 缺失拣货备注

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "task_id": null,
    "need_manual_mark_sku_list": [
      {
        "sku": "Lawn-3.5m*5m",
        "image_url": "https://cf.shopee.ph/file/ph-11134207-7r98v-lzg47xuonptmd6",
        "desc": "案例：买家购买3个[G-10-TWO] => 实际扣除sku: 20个[G-10]"
      }
    ]
  }
}
```

## 业务逻辑说明

1. 权限校验
2. `OrderAnalysis.parse_all_orders(order_list)` 解析订单：
   - 单一 SKU：直接取 `inventorySku`
   - 组合 SKU：从 `varSkuGroupVoList` 拆分（若组合本身有备注则不拆）
3. 检查每个 SKU 是否在 [t_sku_picking_note](../../../data-model/design/t_sku_picking_note.md) 中存在且字段齐全
4. 全齐 → 创建 [OrderPrintTask](../../../data-model/design/t_order_print_task.md)，task_id = `int(time.time() * 100)`，落库
5. 有缺失 → `task_id=null`，返回缺失列表

## 关联

- 数据表：[t_sku_picking_note](../../../data-model/design/t_sku_picking_note.md)、[t_order_print_task](../../../data-model/design/t_order_print_task.md)
- 业务：[ec_erp_api/business/order_printing.py](../../../../../ec_erp_api/business/order_printing.py)
- 模块 spec：[warehouse_module_spec.md](../../../warehouse_module_spec.md)
- 业务文档：[docs/erp_api/warehouse/pre_submit_print_order.md](../../../../../docs/erp_api/warehouse/pre_submit_print_order.md)

## 注意事项

- `order_list` 必须是从 `search_wait_print_order` 拿到的完整数据
- task_id 生成规则：`int(time.time() * 100)`
- 仅在拣货备注齐全时落库

## Change-Log

### 初始版本 - 预提交打印订单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `pre_submit_print_order`
- 业务：`ec_erp_api/business/order_printing.py` `OrderAnalysis`
- 数据表：`t_order_print_task`、`t_sku_picking_note`
