# 提交销售订单

## 接口信息

- **接口路径**: `/erp_api/sale/submit_sale_order`
- **请求方法**: POST
- **接口描述**: 提交销售订单到 BigSeller ERP 出库，状态由"新建/待同步"变为"已同步"
- **权限要求**: 需要 `PMS_SALE` 权限
- **Handler**: [ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `submit_sale_order`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | int | 是 | 订单 ID |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | `{}` |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | 参数错误 |
| 1004 | 订单不存在 |
| 1005 | 订单已经提交过 |
| 1008 | 权限不足 / BigSeller 异常 |

## 请求示例

```json
{ "body": { "order_id": 1001 } }
```

## 响应示例

```json
{ "data": {}, "result": 0, "resultMsg": "success", "traceId": 1709991821760 }
```

错误：

```json
{ "result": 1005, "resultMsg": "订单已经提交过了", "traceId": 1709991821760 }
```

## 业务逻辑说明

1. 权限校验
2. 校验 `order_id`
3. `backend.get_sale_order(order_id)`，校验 project_id；不存在 → 1004
4. 状态为「已同步」 → 1005（防重复提交）
5. 调用 `sync_sale_order_to_erp(order, BigSellerClient)`：通过 BigSeller 出库扣减库存
6. 成功后将 `status` 置为 `已同步`，`backend.update_sale_order(order)`
7. 返回成功

## 关联

- 数据表：[t_sale_order](../../../data-model/design/t_sale_order.md)
- 第三方：[bigseller_integration_spec.md](../../../bigseller_integration_spec.md)
- 模块 spec：[sale_module_spec.md](../../../sale_module_spec.md)
- 业务文档：[docs/erp_api/sales/submit_sale_order.md](../../../../../docs/erp_api/sales/submit_sale_order.md)

## 注意事项

- **不可逆操作**：BigSeller 出库后无法回滚，调用前 UI 必须二次确认
- 同步失败会抛异常，状态不变
- 已同步订单再次提交会返回 1005

## Change-Log

### 初始版本 - 提交销售订单接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/sale.py](../../../../../ec_erp_api/apis/sale.py) `submit_sale_order`、`sync_sale_order_to_erp`
- 数据表：`t_sale_order`
- 第三方：BigSellerClient
