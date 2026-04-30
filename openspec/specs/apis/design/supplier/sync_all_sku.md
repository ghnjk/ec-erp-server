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
- **不修改打包体积字段**：`sku_pack_length / sku_pack_width / sku_pack_height` 由人工通过 `save_sku` 维护，本接口仅显式覆盖 `inventory / erp_sku_* / avg_sell_quantity / inventory_support_days`，体积字段保留旧值
- 推荐用定时任务（凌晨）调用，等同 `auto_sync_tools/sync_sku_inventory.py`

## Change-Log

### 2026-04-30 - 显式声明不覆盖打包体积字段

**变更类型**：行为约定 + 注释强化（无功能变化）

**变更原因**：配合 `t_sku_info` 新增打包体积字段，避免同步任务把人工录入的体积清零。详见 OpenSpec change `add-sku-pack-volume`。

**变更内容**：
- 在 handler 内部加注释，明确仅显式覆盖既有字段，不动 `sku_pack_*`
- 文档与同步任务（`auto_sync_tools/sync_sku_inventory.py`）保持一致约束

**前端影响**：无。

**回滚方式**：注释删除即可。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `sync_all_sku`
- 同步任务：[auto_sync_tools/sync_sku_inventory.py](../../../../../auto_sync_tools/sync_sku_inventory.py)

### 初始版本 - 同步所有 SKU 接口

**变更类型**：新增接口

**变更原因**：手动触发当前项目的 SKU 全量同步。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `sync_all_sku`
- 第三方：BigSellerClient
