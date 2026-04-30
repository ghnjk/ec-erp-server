# 搜索 SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/search_sku`
- **请求方法**: POST
- **接口描述**: 多条件分页搜索 SKU 商品列表，支持模糊匹配与多字段排序
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_sku`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码 |
| page_size | int | 是 | 每页记录数 |
| sku | string | 否 | SKU 编码，模糊匹配（空字符串视为不限制） |
| sku_group | string | 否 | SKU 分组，模糊匹配 |
| sku_name | string | 否 | SKU 名称，模糊匹配 |
| inventory_support_days | int | 否 | 库存支撑天数，默认 0（不限制）；> 0 时筛选 `<=` 该值的 SKU |
| sort | object | 否 | 排序规则 `{sortBy, descending}` |

### sort 对象结构

```json
{
  "sortBy": "inventory_support_days",
  "descending": false
}
```

服务端将拼接 ORDER BY `F<sortBy> ASC|DESC`。

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.total | int | 总记录数 |
| data.list[] | array | SKU 列表 |
| ∟ sku | string | SKU 编码 |
| ∟ sku_group | string | SKU 分组 |
| ∟ sku_name | string | SKU 名称 |
| ∟ sku_unit_name | string | 拣货/采购单位名 |
| ∟ sku_unit_quantity | int | 单位换算数量 |
| ∟ sku_pack_length | int | 每个采购单位的打包长度（cm），0 = 未填写 |
| ∟ sku_pack_width | int | 每个采购单位的打包宽度（cm），0 = 未填写 |
| ∟ sku_pack_height | int | 每个采购单位的打包高度（cm），0 = 未填写 |
| ∟ inventory | int | 库存数量 |
| ∟ avg_sell_quantity | float | 平均日销量 |
| ∟ inventory_support_days | int | 库存支撑天数 |
| ∟ shipping_stock_quantity | int | 在途库存 |
| ∟ erp_sku_id | string | ERP SKU ID |
| ∟ erp_sku_name | string | ERP 商品名 |
| ∟ erp_sku_image_url | string | 图片 URL |
| ∟ erp_sku_info | object | ERP 扩展信息 |
| ∟ project_id | string | 项目 ID |
| ∟ create_time / modify_time | string | 时间字段 |
| ∟ modify_user, is_delete, version | - | 通用审计字段 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

### 基本查询

```json
{
  "body": {
    "current_page": 1,
    "page_size": 10
  }
}
```

### 带条件查询

```json
{
  "body": {
    "current_page": 1,
    "page_size": 10,
    "sku": "A-1",
    "sku_group": "藤条",
    "inventory_support_days": 30,
    "sort": {
      "sortBy": "inventory_support_days",
      "descending": false
    }
  }
}
```

## 响应示例

```json
{
  "data": {
    "list": [
      {
        "avg_sell_quantity": 18.4286,
        "create_time": "2024-03-01 22:33:04",
        "erp_sku_id": "27410427",
        "erp_sku_image_url": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/xxx.jpg",
        "erp_sku_info": {},
        "erp_sku_name": "金色枫叶1pcs",
        "inventory": 4725,
        "inventory_support_days": 256,
        "is_delete": null,
        "modify_time": "2024-03-09 08:00:03",
        "modify_user": null,
        "project_id": "philipine",
        "shipping_stock_quantity": 0,
        "sku": "A-1-Golden-Maple leaf",
        "sku_group": "藤条/枫叶",
        "sku_name": "金色枫叶",
        "sku_unit_name": "",
        "sku_unit_quantity": 1,
        "sku_pack_length": 30,
        "sku_pack_width": 20,
        "sku_pack_height": 15,
        "version": null
      }
    ],
    "total": 1
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 权限校验
2. 解析查询条件（空字符串转 `None`，由 `request_util.get_str_param(..., erase_empty_str=True)` 实现）
3. 调用 `backend.search_sku(sku_group, sku_name, sku, offset, page_size, inventory_support_days, sort_types)`
4. 返回 `pack_pagination_result(total, records)`

## 关联

- 数据表：[t_sku_info](../../../data-model/design/t_sku_info.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/search_sku.md](../../../../../docs/erp_api/supplier/search_sku.md)

## 注意事项

- 所有字符串条件支持模糊匹配
- 空字符串等同未传
- `inventory_support_days = 库存 / 平均日销量`，**该字段不会实时计算，需要 `sync_all_sku` 后才更新**
- 接口自动按 project_id 过滤

## Change-Log

### 2026-04-30 - 响应新增打包体积字段（长 / 宽 / 高，cm）

**变更类型**：响应字段扩展（兼容）

**变更原因**：配合 `t_sku_info` 新增打包体积字段，详见 OpenSpec change `add-sku-pack-volume`。

**变更内容**：
- 响应 `data.list[*]` 新增 3 个 int 字段：`sku_pack_length` / `sku_pack_width` / `sku_pack_height`
- 服务端无新增逻辑，依赖 `SkuDto.columns` 自动透传

**前端影响**：旧前端可忽略新字段；新前端可用于列展示与排序（建议 `0` 视为"未填写"，UI 上灰显或提示）。

**回滚方式**：与 `t_sku_info` 字段回滚同步即可。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_sku`
- ORM：`SkuDto`

### 初始版本 - 搜索 SKU 接口

**变更类型**：新增接口

**变更原因**：SKU 主数据查询基础。

**变更内容**：
- 新增 `POST /erp_api/supplier/search_sku`
- 支持 sku/sku_group/sku_name 模糊匹配
- 支持 inventory_support_days 阈值过滤
- 支持自定义排序

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_sku`
- 数据表：[t_sku_info](../../../data-model/design/t_sku_info.md)
