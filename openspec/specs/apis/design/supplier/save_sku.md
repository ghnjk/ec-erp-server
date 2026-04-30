# 保存 SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/save_sku`
- **请求方法**: POST
- **接口描述**: 保存或更新 SKU 信息，从 BigSeller 同步库存与详情
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `save_sku`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | SKU 编码 |
| sku_group | string | 是 | SKU 分组 |
| sku_name | string | 是 | SKU 名称 |
| sku_unit_name | string | 是 | 单位名称（如"包"/"个"/"箱"） |
| sku_unit_quantity | int | 是 | 单位换算数量 |
| sku_pack_length | int | 否 | 每个采购单位的打包长度（cm），默认 0；0 = 未填写 |
| sku_pack_width | int | 否 | 每个采购单位的打包宽度（cm），默认 0；0 = 未填写 |
| sku_pack_height | int | 否 | 每个采购单位的打包高度（cm），默认 0；0 = 未填写 |
| avg_sell_quantity | int | 是 | 平均日销量 |
| shipping_stock_quantity | int | 是 | 在途库存 |
| inventory_support_days | int | 是 | 库存支撑天数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | 保存后的 SkuDto |
| ∟ 同 [search_sku](./search_sku.md) 响应中的单条 list 项 | - | - |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | SKU 在 BigSeller 中不存在 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "sku": "A-1-Golden-Maple leaf",
    "sku_group": "藤条/枫叶",
    "sku_name": "金色枫叶",
    "sku_unit_name": "包",
    "sku_unit_quantity": 100,
    "sku_pack_length": 30,
    "sku_pack_width": 20,
    "sku_pack_height": 15,
    "avg_sell_quantity": 20,
    "shipping_stock_quantity": 0,
    "inventory_support_days": 30
  }
}
```

## 响应示例

```json
{
  "data": {
    "sku": "A-1-Golden-Maple leaf",
    "sku_group": "藤条/枫叶",
    "sku_name": "金色枫叶",
    "sku_unit_name": "包",
    "sku_unit_quantity": 100,
    "sku_pack_length": 30,
    "sku_pack_width": 20,
    "sku_pack_height": 15,
    "inventory": 4725,
    "avg_sell_quantity": 20,
    "inventory_support_days": 30,
    "shipping_stock_quantity": 0,
    "erp_sku_id": "27410427",
    "erp_sku_name": "金色枫叶1pcs",
    "erp_sku_image_url": "https://...",
    "erp_sku_info": {},
    "project_id": "philipine"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

错误响应：

```json
{ "result": 1003, "resultMsg": "sku xxx 不存在", "traceId": 1709991821760 }
```

## 业务逻辑说明

1. 权限校验
2. 通过 `SkuManager.get_sku_id(sku)` 查 BigSeller 内部 ID；找不到则触发一次全量加载 (`load_and_update_all_sku`)
3. 仍找不到 → 返回 1003
4. 调用 `BigSellerClient.query_sku_detail(sku_id)` 拉详情
5. 累加所有仓库的可用库存
6. 组装 `SkuDto`，调用 `backend.store_sku(sku)` upsert
7. 返回保存后的 dict

## 关联

- 数据表：[t_sku_info](../../../data-model/design/t_sku_info.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/save_sku.md](../../../../../docs/erp_api/supplier/save_sku.md)
- 第三方：[bigseller_integration_spec.md](../../../bigseller_integration_spec.md)

## 注意事项

- SKU 必须在 BigSeller 系统中存在
- 库存数量实时从 BigSeller 同步
- ERP 字段（erp_sku_id/erp_sku_name/erp_sku_image_url）自动填充

## Change-Log

### 2026-04-30 - 新增打包体积字段（长 / 宽 / 高，cm）

**变更类型**：新增可选请求参数 + 响应字段扩展

**变更原因**：配合 `t_sku_info` 新增打包体积字段，详见 OpenSpec change `add-sku-pack-volume`。

**变更内容**：
- 请求新增 3 个 **可选** int 参数：`sku_pack_length` / `sku_pack_width` / `sku_pack_height`，默认 0
- 响应 `data` 字段（`SkuDto.to_dict`）新增同名 3 个字段
- 服务端通过 `request_util.get_int_param("xxx", 0)` 读取，未传 / 为 `null` / 为空字符串均按 0 处理

**前端影响**：
- 旧前端不传该字段仍可调用，落库为 0（**注意**：覆盖式 upsert 时旧值会被覆盖为 0，前端如需保留旧体积请显式回传）
- 新前端可在 SKU 编辑表单中加入 3 个尺寸输入框（cm），并将原值连同其他字段一并回传

**回滚方式**：移除 `request_util.get_int_param("sku_pack_*", 0)` 与 `SkuDto(...)` 中的 3 个参数即可。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `save_sku`
- ORM：`SkuDto`

### 初始版本 - 保存 SKU 接口

**变更类型**：新增接口

**变更原因**：将 BigSeller SKU 落库到本地，建立主数据。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `save_sku`
- 第三方：BigSellerClient
