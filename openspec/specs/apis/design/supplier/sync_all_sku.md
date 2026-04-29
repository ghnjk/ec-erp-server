# 同步所有 SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/sync_all_sku`
- **请求方法**: POST
- **接口描述**: 同步当前项目所有 SKU 的库存、销量、ERP 信息
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `sync_all_sku`

## 请求参数

无

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.update_count | int | 成功更新数 |
| data.fail_count | int | 失败数 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{ "body": {} }
```

## 响应示例

```json
{
  "data": { "update_count": 150, "fail_count": 2 },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 权限校验
2. 查询当前项目所有 SKU（最多 10000 条）
3. 加载 BigSeller SKU 映射
4. 对每个 SKU：
   - 取 SKU ID（无则触发全量加载，仅一次）
   - `query_sku_inventory_detail` + `query_sku_detail` 拉库存与详情
   - 更新 `inventory` / `erp_sku_*` / `avg_sell_quantity` / `inventory_support_days`
   - `backend.store_sku`
   - `time.sleep(0.3)` 限速
5. 返回统计

## 关联

- 数据表：[t_sku_info](../../../data-model/design/t_sku_info.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/sync_all_sku.md](../../../../../docs/erp_api/supplier/sync_all_sku.md)
- 同步任务：[auto_sync_tools/sync_sku_inventory.py](../../../../../auto_sync_tools/sync_sku_inventory.py)（同等逻辑的离线版本）

## 计算规则

- 平均日销量：`BigSeller.avgDailySales × 1.1`
- 库存支撑天数：`库存 / 平均日销量`（avg ≤ 0.01 时按 0.01 兜底）

## 注意事项

- 耗时较长（数百到数千 SKU 时几分钟级别）
- 每个 SKU 间隔 0.3 秒，防止触发 BigSeller 风控
- 单条失败继续处理后续
- 推荐用定时任务（凌晨）调用，等同 `auto_sync_tools/sync_sku_inventory.py`

## Change-Log

### 初始版本 - 同步所有 SKU 接口

**变更类型**：新增接口

**变更原因**：手动触发当前项目的 SKU 全量同步。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `sync_all_sku`
- 第三方：BigSellerClient
