# 批量添加 SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/add_sku`
- **请求方法**: POST
- **接口描述**: 批量添加 SKU，从 BigSeller 同步信息和库存，自动计算平均销量与库存支撑天数
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `add_sku`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skus | string | 是 | SKU 编码列表，每行一个，换行分隔 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.success_count | int | 成功添加数量 |
| data.ignore_count | int | 已存在被忽略的数量 |
| data.fail_count | int | 失败数量 |
| data.detail | object | 详细结果 `{sku: status}`，status 为 `success` / `ignored` / 错误信息 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "skus": "A-1-Golden-Maple leaf\nA-1-Green-Maple leaf\nA-1-Red-Maple leaf"
  }
}
```

## 响应示例

```json
{
  "data": {
    "success_count": 2,
    "ignore_count": 1,
    "fail_count": 1,
    "detail": {
      "A-1-Golden-Maple leaf": "ignored",
      "A-1-Green-Maple leaf": "success",
      "A-1-Red-Maple leaf": "success",
      "INVALID-SKU": "sku INVALID-SKU 不存在"
    }
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 权限校验
2. 按换行符切分 `skus` 字符串
3. 对每个 SKU：
   - 数据库已存在 → 跳过（`ignored`）
   - `SkuManager.get_sku_id` 找不到 → 触发一次全量加载（仅一次）
   - 仍找不到 → 失败（记录错误信息）
   - `query_sku_detail` 拉详情、累计库存
   - `query_sku_inventory_detail` 拉销量预测
   - 计算 `avg_sell_quantity = avgDailySales * 1.1`
   - 计算 `inventory_support_days = inventory / max(avg_sell_quantity, 0.01)`
   - 组装 `SkuDto` 落库（默认 `sku_group="待定"`、`sku_name=""`、`sku_unit_name=""`、`sku_unit_quantity=1`、`shipping_stock_quantity=0`）
4. 返回统计 + detail

## 关联

- 数据表：[t_sku_info](../../../data-model/design/t_sku_info.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/add_sku.md](../../../../../docs/erp_api/supplier/add_sku.md)

## 计算规则

- 平均日销量：`BigSeller.avgDailySales × 1.1`
- 库存支撑天数：`库存 / 平均日销量`（avg ≤ 0.01 时按 0.01 兜底）

## 注意事项

- 已存在的 SKU 不会重复添加，需要更新走 `save_sku`
- 默认值需要后续通过 `save_sku` 完善
- 新增的打包体积字段（`sku_pack_length / sku_pack_width / sku_pack_height`）默认 0（cm），需通过 `save_sku` 单独维护
- 单条失败不影响其他 SKU

## Change-Log

### 2026-04-30 - 默认体积字段为 0

**变更类型**：写入默认值（不引入新参数）

**变更原因**：配合 `t_sku_info` 新增打包体积字段，详见 OpenSpec change `add-sku-pack-volume`。

**变更内容**：
- 不修改请求参数；批量构造 `SkuDto(...)` 时显式传 `sku_pack_length=0, sku_pack_width=0, sku_pack_height=0`
- 后续可通过 `/erp_api/supplier/save_sku` 完善体积

**前端影响**：无。

**回滚方式**：移除 `SkuDto(...)` 中的 3 个体积参数即可，ORM 默认值会兜底为 0。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `add_sku`

### 初始版本 - 批量添加 SKU 接口

**变更类型**：新增接口

**变更原因**：批量初始化 SKU 主数据。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `add_sku`
- 第三方：BigSellerClient
