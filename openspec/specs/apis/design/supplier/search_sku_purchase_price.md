# 搜索 SKU 采购价格

## 接口信息

- **接口路径**: `/erp_api/supplier/search_sku_purchase_price`
- **请求方法**: POST
- **接口描述**: 分页查询 SKU 采购价格信息
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_sku_purchase_price`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.total | int | 总记录数 |
| data.list[] | array | 采购价格列表 |
| ∟ sku | string | SKU 编码 |
| ∟ sku_group | string | SKU 分组 |
| ∟ sku_name | string | SKU 名称 |
| ∟ supplier_id | int | 供应商 ID |
| ∟ supplier_name | string | 供应商名 |
| ∟ purchase_price | int | 采购价（**单位：分**） |
| ∟ erp_sku_image_url | string | 图片 URL |
| ∟ project_id | string | 项目 ID |
| ∟ create_time / modify_time / modify_user / is_delete / version | - | 通用字段 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{ "body": { "current_page": 1, "page_size": 10 } }
```

## 响应示例

```json
{
  "data": {
    "list": [
      {
        "create_time": "2024-03-02 21:51:42",
        "erp_sku_image_url": "https://...",
        "is_delete": 0,
        "modify_time": "2024-03-02 21:51:42",
        "modify_user": "",
        "project_id": "philipine",
        "purchase_price": 30,
        "sku": "A-11-Beige Reed leaf",
        "sku_group": "藤条/芦苇叶",
        "sku_name": "米色芦苇叶",
        "supplier_id": 4,
        "supplier_name": "新草地厂家(麦森人造草坪）",
        "version": 0
      }
    ],
    "total": 5
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 权限校验
2. 调用 `backend.search_sku_purchase_price(offset, page_size)`
3. 返回 `pack_pagination_result`

## 关联

- 数据表：[t_sku_purchase_price](../../../data-model/design/t_sku_purchase_price.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/search_sku_purchase_price.md](../../../../../docs/erp_api/supplier/search_sku_purchase_price.md)

## 注意事项

- 价格单位：**分**（前端展示需 / 100）
- 同一 SKU 可能多供应商各有价格记录
- 价格在采购单 `供应商捡货中 → 待发货` 时自动更新

## Change-Log

### 初始版本 - 搜索 SKU 采购价格接口

**变更类型**：新增接口

**变更原因**：为采购价比对/分析提供数据。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_sku_purchase_price`
- 数据表：[t_sku_purchase_price](../../../data-model/design/t_sku_purchase_price.md)
