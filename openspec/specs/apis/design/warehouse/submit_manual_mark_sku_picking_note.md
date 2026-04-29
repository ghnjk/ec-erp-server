# 提交 SKU 拣货备注

## 接口信息

- **接口路径**: `/erp_api/warehouse/submit_manual_mark_sku_picking_note`
- **请求方法**: POST
- **接口描述**: 批量提交/更新 SKU 拣货备注
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限
- **Handler**: [ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `submit_manual_mark_sku_picking_note`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| manual_mark_sku_list[] | array | 是 | 拣货备注列表 |
| ∟ sku | string | 是 | SKU 编码 |
| ∟ picking_unit | float | 是 | 拣货单位换算（1 个 SKU 等于多少拣货单位） |
| ∟ picking_unit_name | string | 是 | 拣货单位名 |
| ∟ picking_sku_name | string | 是 | 拣货 SKU 名称（PDF 上标注） |
| ∟ support_pkg_picking | bool | 否 | 是否支持整包，默认 false |
| ∟ pkg_picking_unit | float | 否 | 整包单位换算，默认 0 |
| ∟ pkg_picking_unit_name | string | 否 | 整包单位名，默认 `""` |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.manual_mark_sku_list | array | 原样回显已提交的列表 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "manual_mark_sku_list": [
      {
        "sku": "G-10",
        "picking_unit": 10,
        "picking_unit_name": "个",
        "picking_sku_name": "葡萄叶",
        "support_pkg_picking": true,
        "pkg_picking_unit": 100,
        "pkg_picking_unit_name": "包"
      }
    ]
  }
}
```

## 响应示例

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "manual_mark_sku_list": [
      { "sku": "G-10", "picking_unit": 10, "picking_unit_name": "个", "picking_sku_name": "葡萄叶", "support_pkg_picking": true, "pkg_picking_unit": 100, "pkg_picking_unit_name": "包" }
    ]
  }
}
```

## 业务逻辑说明

1. 权限校验
2. 遍历 `manual_mark_sku_list`：
   - 构造 `SkuPickingNote`，设置 project_id
   - 自动校正：若 `support_pkg_picking=true` 且 `picking_unit > pkg_picking_unit`，**交换** picking 与 pkg_picking 的单位与名称
   - `backend.store_sku_picking_note(note)` upsert
3. 返回原始列表

## 自动校正规则

```
if support_pkg_picking and picking_unit > pkg_picking_unit:
    swap(picking_unit, pkg_picking_unit)
    swap(picking_unit_name, pkg_picking_unit_name)
```

## 关联

- 数据表：[t_sku_picking_note](../../../data-model/design/t_sku_picking_note.md)
- 模块 spec：[warehouse_module_spec.md](../../../warehouse_module_spec.md)
- 业务文档：[docs/erp_api/warehouse/submit_manual_mark_sku_picking_note.md](../../../../../docs/erp_api/warehouse/submit_manual_mark_sku_picking_note.md)
- 兄弟接口：[search_manual_mark_sku_picking_note](./search_manual_mark_sku_picking_note.md)、[pre_submit_print_order](./pre_submit_print_order.md)

## 注意事项

- 同一 (project, sku) 重复提交会覆盖原有配置
- 整包单位数量必须是基础单位的整数倍
- 通常配合 `pre_submit_print_order` 返回的 `need_manual_mark_sku_list` 使用

## Change-Log

### 初始版本 - 提交 SKU 拣货备注接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `submit_manual_mark_sku_picking_note`
- 数据表：`t_sku_picking_note`
