# 提交SKU拣货备注

## 接口信息

- **接口路径**: `/erp_api/warehouse/submit_manual_mark_sku_picking_note`
- **请求方法**: POST
- **接口描述**: 批量提交或更新SKU的拣货备注信息
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| manual_mark_sku_list | array | 是 | SKU拣货备注列表 |
| ∟ sku | string | 是 | SKU编码 |
| ∟ picking_unit | float | 是 | 拣货单位数量 |
| ∟ picking_unit_name | string | 是 | 拣货单位名称 |
| ∟ picking_sku_name | string | 是 | 拣货SKU名称 |
| ∟ support_pkg_picking | bool | 否 | 是否支持整包拣货，默认false |
| ∟ pkg_picking_unit | float | 否 | 整包拣货单位数量，默认0 |
| ∟ pkg_picking_unit_name | string | 否 | 整包拣货单位名称，默认空字符串 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ manual_mark_sku_list | array | 提交的SKU拣货备注列表（原样返回） |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

### 基础拣货备注
```json
{
  "manual_mark_sku_list": [
    {
      "sku": "G-10",
      "picking_unit": 10,
      "picking_unit_name": "个",
      "picking_sku_name": "葡萄叶",
      "support_pkg_picking": false,
      "pkg_picking_unit": 0,
      "pkg_picking_unit_name": ""
    }
  ]
}
```

### 支持整包拣货的备注
```json
{
  "manual_mark_sku_list": [
    {
      "sku": "A-1-Golden-Maple leaf",
      "picking_unit": 10,
      "picking_unit_name": "片",
      "picking_sku_name": "金色枫叶",
      "support_pkg_picking": true,
      "pkg_picking_unit": 100,
      "pkg_picking_unit_name": "包"
    }
  ]
}
```

### 批量提交
```json
{
  "manual_mark_sku_list": [
    {
      "sku": "G-10",
      "picking_unit": 10,
      "picking_unit_name": "个",
      "picking_sku_name": "葡萄叶"
    },
    {
      "sku": "A-1-Red-Maple leaf",
      "picking_unit": 5,
      "picking_unit_name": "片",
      "picking_sku_name": "红色枫叶",
      "support_pkg_picking": true,
      "pkg_picking_unit": 50,
      "pkg_picking_unit_name": "袋"
    }
  ]
}
```

## 响应示例

### 成功响应

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "manual_mark_sku_list": [
      {
        "sku": "G-10",
        "picking_unit": 10,
        "picking_unit_name": "个",
        "picking_sku_name": "葡萄叶"
      }
    ]
  }
}
```

## 业务逻辑说明

1. 验证用户权限
2. 遍历manual_mark_sku_list，对每个SKU：
   - 创建拣货备注对象
   - 设置项目ID
   - 如果支持整包拣货，确保pkg_picking_unit是较大的单位
     - 如果设置错误（picking_unit > pkg_picking_unit），自动交换
   - 保存到数据库（如果已存在则更新）
3. 返回提交的列表

## 拣货单位配置说明

### 基础拣货单位（必填）
表示ERP系统中的1个SKU对应实际多少个商品。

**示例1**：
- ERP中"葡萄叶1片"对应实际10片葡萄叶
- picking_unit = 10
- picking_unit_name = "片"

**示例2**：
- ERP中"草地1平方米"对应实际1平方米
- picking_unit = 1
- picking_unit_name = "平方米"

### 整包拣货单位（可选）
当商品可以按整包/整箱拣货时配置。

**示例**：
- 基础单位：10片/个
- 整包单位：100片/包
- support_pkg_picking = true
- picking_unit = 10
- picking_unit_name = "个"
- pkg_picking_unit = 100
- pkg_picking_unit_name = "包"

订单需要250片时，拣货清单显示：
- 2包（200片）
- 5个（50片）

## 自动校正规则

如果配置错误，系统会自动校正：
```
如果 support_pkg_picking = true 且 picking_unit > pkg_picking_unit:
  交换 picking_unit 和 pkg_picking_unit
  交换 picking_unit_name 和 pkg_picking_unit_name
```

## 使用场景

此接口用于：
1. 补充缺失的SKU拣货备注（从pre_submit_print_order返回的need_manual_mark_sku_list）
2. 修改已有的SKU拣货备注
3. 批量配置多个SKU的拣货备注

## 注意事项

- 同一个SKU在同一个项目中只能有一条拣货备注
- 重复提交会覆盖原有配置
- 拣货备注直接影响打印订单时的拣货清单展示
- 建议在配置前先调用 `search_manual_mark_sku_picking_note` 检查是否已存在
- 整包单位数量必须是基础单位数量的整数倍

