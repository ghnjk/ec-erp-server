# 搜索SKU拣货备注

## 接口信息

- **接口路径**: `/erp_api/warehouse/search_manual_mark_sku_picking_note`
- **请求方法**: POST
- **接口描述**: 分页查询SKU的拣货备注信息，支持SKU编码模糊搜索
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码，从1开始 |
| page_size | int | 是 | 每页记录数 |
| search_sku | string | 否 | SKU编码，模糊搜索 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ total | int | 总记录数 |
| ∟ list | array | 拣货备注列表 |
| &nbsp;&nbsp;∟ project_id | string | 项目ID |
| &nbsp;&nbsp;∟ sku | string | SKU编码 |
| &nbsp;&nbsp;∟ picking_unit | float | 拣货单位数量 |
| &nbsp;&nbsp;∟ picking_unit_name | string | 拣货单位名称 |
| &nbsp;&nbsp;∟ support_pkg_picking | bool | 是否支持整包拣货 |
| &nbsp;&nbsp;∟ pkg_picking_unit | float | 整包拣货单位数量 |
| &nbsp;&nbsp;∟ pkg_picking_unit_name | string | 整包拣货单位名称 |
| &nbsp;&nbsp;∟ picking_sku_name | string | 拣货SKU名称 |
| &nbsp;&nbsp;∟ erp_sku_name | string | ERP系统中的SKU名称 |
| &nbsp;&nbsp;∟ erp_sku_image_url | string | SKU图片URL |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

### 查询所有
```json
{
  "current_page": 1,
  "page_size": 10,
  "search_sku": ""
}
```

### 模糊搜索
```json
{
  "current_page": 1,
  "page_size": 10,
  "search_sku": "G-10"
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "list": [
      {
        "project_id": "dev",
        "sku": "test",
        "picking_unit": 1,
        "picking_unit_name": "pcs",
        "support_pkg_picking": false,
        "pkg_picking_unit": 0,
        "pkg_picking_unit_name": "",
        "picking_sku_name": "G-20",
        "erp_sku_name": "2m*0.5m(一平方米草地)",
        "erp_sku_image_url": "https://res.bigseller.pro/sku/images/merchantsku/279590/1674962429302.jpg?imageView2/1/w/300/h/300"
      }
    ],
    "total": 1
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991729751
}
```

## 拣货备注字段说明

### 基础拣货单位
- `picking_unit`: 基础拣货单位数量（如：1个ERP SKU = 10个实际SKU）
- `picking_unit_name`: 基础拣货单位名称（如：个、片、条）
- `picking_sku_name`: 拣货时显示的SKU名称

### 整包拣货（可选）
- `support_pkg_picking`: 是否支持整包拣货
- `pkg_picking_unit`: 整包拣货单位数量（如：1包 = 100个）
- `pkg_picking_unit_name`: 整包拣货单位名称（如：包、箱）

## 拣货计算示例

假设SKU拣货备注配置如下：
- picking_unit: 10
- picking_unit_name: "个"
- support_pkg_picking: true
- pkg_picking_unit: 100
- pkg_picking_unit_name: "包"

订单需要250个该SKU，则拣货清单为：
- 2包（200个）
- 5个（50个）

## 业务逻辑说明

1. 验证用户权限
2. 根据search_sku参数模糊搜索SKU编码
3. 从数据库查询拣货备注
4. 从BigSeller获取SKU的图片和名称（如果SKU存在）
5. 返回分页结果

## 使用场景

此接口用于：
- 查看和管理已配置的SKU拣货备注
- 在补充拣货备注前，查看是否已存在
- 拣货备注的查询和维护

## 注意事项

- 每个SKU在一个项目中只能有一条拣货备注
- 拣货备注决定了打印订单时如何展示拣货清单
- 支持整包拣货时，会优先按整包计算，剩余部分按基础单位计算
- 如果SKU在BigSeller中不存在，erp_sku_name和erp_sku_image_url为空

