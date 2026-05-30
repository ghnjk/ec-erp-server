# 提交采购单并进入下一步

## 接口信息

- **接口路径**: `/erp_api/supplier/submit_purchase_order_and_next_step`
- **请求方法**: POST
- **接口描述**: 提交采购单并根据当前状态自动流转到下一个采购步骤
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

请求参数与 `/erp_api/supplier/save_purchase_order` 完全相同，参考该接口文档。

关键参数：
- `purchase_step`: 当前采购步骤
- 其他参数根据不同步骤有不同要求

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 更新后的完整采购单对象 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1004 | 业务逻辑错误（如存在未确定数量的SKU） |
| 1008 | 权限不足 |

## 采购流程状态转换

### 1. 草稿 → 供应商捡货中

**操作**：
- 去除数量为0的SKU
- 提交采购单

**要求**：无特殊要求

### 2. 供应商捡货中 → 待发货

**操作**：
- 确认所有SKU的采购数量
- 保存供应价到数据库
- 设置采购日期为当前日期

**要求**：
- 所有purchase_skus的quantity不能为null
- 必须确认所有待定数量

### 3. 待发货 → 海运中

**操作**：
- 复制purchase_skus到store_skus
- 设置check_in_quantity = quantity（预设实际入库数量等于采购数量）

**要求**：
- 需要填写海运信息（maritime_port、shipping_company、expect_arrive_warehouse_date）

### 4. 海运中 → 已入库

**操作**：
- 确认实际入库数量
- 更新store_skus的check_in_quantity

**要求**：
- 需要填写arrive_warehouse_date

### 5. 已入库 → 完成

**操作**：
- 同步库存到BigSeller ERP系统
- 生成入库单

**要求**：
- store_skus必须有数据

## 请求示例

### 从草稿提交到供应商捡货中

```json
{
  "purchase_order_id": 2,
  "supplier_id": 4,
  "purchase_step": "草稿",
  "purchase_skus": [
    {
      "sku": "A-11-Beige Reed leaf",
      "quantity": 10,
      "unit_price": 30
    }
  ],
  "remark": "test"
}
```

### 从供应商捡货中到待发货

```json
{
  "purchase_order_id": 2,
  "supplier_id": 4,
  "purchase_step": "供应商捡货中",
  "purchase_skus": [
    {
      "sku": "A-11-Beige Reed leaf",
      "quantity": 10,
      "unit_price": 30
    }
  ]
}
```

### 从已入库同步到ERP完成

```json
{
  "purchase_order_id": 2,
  "supplier_id": 4,
  "purchase_step": "已入库",
  "purchase_skus": [...],
  "store_skus": [
    {
      "sku": "A-11-Beige Reed leaf",
      "quantity": 10,
      "check_in_quantity": 10,
      "unit_price": 30
    }
  ]
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "purchase_order_id": 2,
    "supplier_id": 4,
    "supplier_name": "新草地厂家(麦森人造草坪）",
    "purchase_step": "供应商捡货中",
    "sku_amount": 300,
    "pay_amount": 0,
    "pay_state": 0,
    "purchase_date": null,
    "expect_arrive_warehouse_date": "2024-04-01",
    "maritime_port": "广州",
    "purchase_skus": [
      {
        "sku": "A-11-Beige Reed leaf",
        "sku_group": "藤条/芦苇叶",
        "sku_name": "米色芦苇叶",
        "quantity": 10,
        "unit_price": 30
      }
    ],
    "store_skus": [],
    "project_id": "philipine"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 错误响应

```json
{
  "result": 1004,
  "resultMsg": "存在未确定数量的sku",
  "traceId": 1709991821760
}
```

## 同步到ERP的逻辑

当采购步骤为"已入库"并提交时，系统会：

1. 调用BigSeller API创建入库单
2. 入库单备注格式：`ec-erp 采购单：{purchase_order_id} [入库单=IN-EC-{purchase_order_id}]`
3. 对每个store_sku：
   - 转换价格：unit_price / 100（分转元）
   - 计算入库数量：check_in_quantity * sku_unit_quantity
4. 返回同步结果

## 业务逻辑说明

1. 验证用户权限
2. 根据当前purchase_step执行对应的业务逻辑
3. 自动流转到下一个状态
4. 保存采购单
5. 返回更新后的采购单完整信息

## 注意事项

- 每次提交只会前进一步，不能跨步骤
- 从"已入库"到"完成"会调用BigSeller API，可能失败
- "供应商捡货中"步骤会自动保存供应价格
- 状态流转不可逆，请谨慎操作
- 同步到ERP失败会返回错误，不会更新状态

