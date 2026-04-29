# 搜索 SKU 拣货备注

## 接口信息

- **接口路径**: `/erp_api/warehouse/search_manual_mark_sku_picking_note`
- **请求方法**: POST
- **接口描述**: 分页查询 SKU 拣货备注，支持 SKU 编码模糊搜索
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限
- **Handler**: [ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `search_manual_mark_sku_picking_note`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码 |
| page_size | int | 是 | 每页记录数 |
| search_sku | string | 否 | SKU 编码模糊匹配（空字符串视为不限制） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.total | int | 总记录数 |
| data.list[] | array | 拣货备注列表 |
| ∟ project_id | string | 项目 ID |
| ∟ sku | string | SKU 编码 |
| ∟ picking_unit | float | 拣货单位换算 |
| ∟ picking_unit_name | string | 拣货单位名 |
| ∟ support_pkg_picking | bool | 是否支持整包 |
| ∟ pkg_picking_unit | float | 整包单位换算 |
| ∟ pkg_picking_unit_name | string | 整包单位名 |
| ∟ picking_sku_name | string | 拣货 SKU 名称 |
| ∟ erp_sku_name | string | ERP 名称（来自 BigSeller） |
| ∟ erp_sku_image_url | string | ERP 图片 URL |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "current_page": 1,
    "page_size": 10,
    "search_sku": "G-10"
  }
}
```

## 响应示例

```json
{
  "data": {
    "list": [
      {
        "project_id": "philipine",
        "sku": "G-10",
        "picking_unit": 10,
        "picking_unit_name": "片",
        "support_pkg_picking": true,
        "pkg_picking_unit": 100,
        "pkg_picking_unit_name": "包",
        "picking_sku_name": "葡萄叶",
        "erp_sku_name": "葡萄叶 1pcs",
        "erp_sku_image_url": "https://res.bigseller.pro/sku/images/merchantsku/279590/xxx.jpg"
      }
    ],
    "total": 1
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991729751
}
```

## 业务逻辑说明

1. 权限校验
2. 调用 `backend.search_sku_picking_note(search_sku, offset, page_size)` 模糊查询
3. 通过 SkuManager 补充 `erp_sku_name` / `erp_sku_image_url`
4. 返回分页结果

## 拣货计算示例

picking_unit=10/「个」，pkg_picking_unit=100/「包」时，订单需 250 个：

- 2 包（200 个）
- 5 个（50 个）

## 关联

- 数据表：[t_sku_picking_note](../../../data-model/design/t_sku_picking_note.md)
- 第三方：[bigseller_integration_spec.md](../../../bigseller_integration_spec.md)
- 模块 spec：[warehouse_module_spec.md](../../../warehouse_module_spec.md)
- 业务文档：[docs/erp_api/warehouse/search_manual_mark_sku_picking_note.md](../../../../../docs/erp_api/warehouse/search_manual_mark_sku_picking_note.md)

## 注意事项

- 每个 (project, sku) 仅一条拣货备注（主键约束）
- BigSeller 中找不到的 SKU，erp_* 字段为空

## Change-Log

### 初始版本 - 搜索 SKU 拣货备注接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `search_manual_mark_sku_picking_note`
- 数据表：`t_sku_picking_note`
