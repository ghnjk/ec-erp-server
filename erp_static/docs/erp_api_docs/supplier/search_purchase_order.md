# 搜索采购单

## 接口信息

- **接口路径**: `/erp_api/supplier/search_purchase_order`
- **请求方法**: POST
- **接口描述**: 分页查询采购单列表
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码，从1开始 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ total | int | 总记录数 |
| ∟ list | array | 采购单列表 |
| &nbsp;&nbsp;∟ purchase_order_id | int | 采购单ID |
| &nbsp;&nbsp;∟ supplier_id | int | 供应商ID |
| &nbsp;&nbsp;∟ supplier_name | string | 供应商名称 |
| &nbsp;&nbsp;∟ purchase_step | string | 采购步骤：草稿/供应商捡货中/待发货/海运中/已入库/完成 |
| &nbsp;&nbsp;∟ sku_amount | int | SKU总金额（单位：分） |
| &nbsp;&nbsp;∟ pay_amount | int | 支付金额（单位：分） |
| &nbsp;&nbsp;∟ pay_state | int | 支付状态：0未支付，1已支付 |
| &nbsp;&nbsp;∟ purchase_date | string | 采购日期 |
| &nbsp;&nbsp;∟ expect_arrive_warehouse_date | string | 预计到达仓库日期 |
| &nbsp;&nbsp;∟ arrive_warehouse_date | string | 实际到达仓库日期 |
| &nbsp;&nbsp;∟ maritime_port | string | 海运港口 |
| &nbsp;&nbsp;∟ shipping_company | string | 物流公司 |
| &nbsp;&nbsp;∟ shipping_fee | string | 运费 |
| &nbsp;&nbsp;∟ remark | string | 备注 |
| &nbsp;&nbsp;∟ purchase_skus | array | 采购SKU列表 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku | string | SKU编码 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku_group | string | SKU分组 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku_name | string | SKU名称 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ quantity | int | 采购数量 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ unit_price | int | 单价（单位：分） |
| &nbsp;&nbsp;∟ store_skus | array | 入库SKU列表 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku | string | SKU编码 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku_group | string | SKU分组 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ sku_name | string | SKU名称 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ quantity | int | 采购数量 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ check_in_quantity | int | 实际入库数量 |
| &nbsp;&nbsp;&nbsp;&nbsp;∟ unit_price | int | 单价（单位：分） |
| &nbsp;&nbsp;∟ project_id | string | 所属项目ID |
| &nbsp;&nbsp;∟ create_time | string | 创建时间 |
| &nbsp;&nbsp;∟ modify_time | string | 修改时间 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "current_page": 1,
  "page_size": 10
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "list": [
      {
        "arrive_warehouse_date": null,
        "create_time": "2024-03-02 21:51:09",
        "expect_arrive_warehouse_date": "2024-04-01",
        "is_delete": null,
        "maritime_port": "广州",
        "modify_time": "2024-03-02 21:53:52",
        "modify_user": null,
        "op_log": null,
        "pay_amount": 90,
        "pay_state": 1,
        "project_id": "philipine",
        "purchase_date": "2024-03-02",
        "purchase_order_id": 2,
        "purchase_skus": [
          {
            "quantity": 1,
            "sku": "A-11-Beige Reed leaf",
            "sku_group": "藤条/芦苇叶",
            "sku_name": "米色芦苇叶",
            "unit_price": 30
          }
        ],
        "purchase_step": "完成",
        "remark": "test 1",
        "shipping_company": null,
        "shipping_fee": "0.3",
        "sku_amount": 90,
        "sku_summary": null,
        "store_skus": [
          {
            "check_in_quantity": 1,
            "quantity": 1,
            "sku": "A-11-Beige Reed leaf",
            "sku_group": "藤条/芦苇叶",
            "sku_name": "米色芦苇叶",
            "unit_price": 30
          }
        ],
        "supplier_id": 4,
        "supplier_name": "新草地厂家(麦森人造草坪）",
        "version": null
      }
    ],
    "total": 2
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991870811
}
```

## 采购流程说明

采购单有以下几个状态，按顺序流转：

1. **草稿**: 初始状态，选择采购物品
2. **供应商捡货中**: 提交采购单后，等待厂家提供采购清单
3. **待发货**: 采购单确认后，等待厂家发货
4. **海运中**: 厂家已发货，填写海运信息
5. **已入库**: 货物到达仓库，完成点货入库
6. **完成**: 同步到ERP系统

## 业务逻辑说明

1. 验证用户权限
2. 根据分页参数查询采购单列表
3. 返回分页结果，包含完整的采购SKU和入库SKU信息

## 注意事项

- 采购单按创建时间倒序排列（最新的在前）
- purchase_skus和store_skus可能不一致（实际入库数量可能与采购数量不同）
- 金额字段单位为"分"，显示时需要除以100
- 接口会根据当前项目ID自动过滤数据

