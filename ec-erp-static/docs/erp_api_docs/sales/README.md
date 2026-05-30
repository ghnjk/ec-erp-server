# Sales 模块接口文档

销售管理模块，包含SKU销售价格管理和销售订单管理功能。

## 模块概述

Sales模块主要负责：
- SKU销售价格的设置和查询
- 销售订单的创建、修改、删除和查询
- 销售订单的状态流转（待同步 → 已同步）

## 接口列表

### SKU销售价格管理

1. **保存SKU销售价格** - [save_sku_sale_price.md](./save_sku_sale_price.md)
   - 接口路径: `/erp_api/sale/save_sku_sale_price`
   - 功能: 保存或更新SKU销售价格

2. **搜索SKU销售价格** - [search_sku_sale_price.md](./search_sku_sale_price.md)
   - 接口路径: `/erp_api/sale/search_sku_sale_price`
   - 功能: 查询SKU销售价格列表，支持模糊搜索和分页

### 销售订单管理

3. **创建销售订单** - [create_sale_order.md](./create_sale_order.md)
   - 接口路径: `/erp_api/sale/create_sale_order`
   - 功能: 创建新的销售订单，默认状态为"待同步"

4. **更新销售订单** - [update_sale_order.md](./update_sale_order.md)
   - 接口路径: `/erp_api/sale/update_sale_order`
   - 功能: 更新现有销售订单的信息

5. **删除销售订单** - [delete_sale_order.md](./delete_sale_order.md)
   - 接口路径: `/erp_api/sale/delete_sale_order`
   - 功能: 删除销售订单（物理删除）

6. **确认提交销售订单** - [submit_sale_order.md](./submit_sale_order.md)
   - 接口路径: `/erp_api/sale/submit_sale_order`
   - 功能: 确认提交订单，将状态从"待同步"改为"已同步"

7. **搜索销售订单** - [search_sale_order.md](./search_sale_order.md)
   - 接口路径: `/erp_api/sale/search_sale_order`
   - 功能: 搜索销售订单，支持多条件筛选和分页

## 权限要求

所有接口都需要 **PMS_SALE** 权限。

## 数据表结构

### t_sku_sale_price - SKU销售价格表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Fproject_id | VARCHAR(128) | 所属项目ID（主键） |
| Fsku | VARCHAR(128) | SKU编码（主键） |
| Funit_price | FLOAT | 销售单价 |
| Fcreate_time | DATETIME | 创建时间 |
| Fmodify_time | DATETIME | 修改时间 |

### t_sale_order - 销售订单表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Fproject_id | VARCHAR(128) | 所属项目ID |
| Forder_id | INT | 订单ID（主键、自增） |
| Forder_date | DATETIME | 订单日期 |
| Fsale_sku_list | JSON | 销售SKU列表 |
| Funit_price | FLOAT | 单价 |
| Fquantity | INT | 数量 |
| Ftotal_amount | FLOAT | 订单总金额 |
| Fstatus | VARCHAR(128) | 订单状态（待同步、已同步） |
| Fcreate_time | DATETIME | 创建时间 |
| Fmodify_time | DATETIME | 修改时间 |

## 业务流程

### 销售订单流程

```
创建订单（待同步） → 确认提交（已同步）
```

1. **创建订单**: 使用 `create_sale_order` 创建订单，初始状态为"待同步"
2. **修改订单**（可选）: 使用 `update_sale_order` 修改订单信息
3. **确认提交**: 使用 `submit_sale_order` 将订单状态改为"已同步"
4. **查询订单**: 使用 `search_sale_order` 查询订单列表

## 使用示例

### 1. 设置SKU销售价格

```bash
curl -X POST http://localhost:5000/erp_api/sale/save_sku_sale_price \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "A-1-Golden-Maple leaf",
    "unit_price": 150.5
  }'
```

### 2. 创建销售订单

```bash
curl -X POST http://localhost:5000/erp_api/sale/create_sale_order \
  -H "Content-Type: application/json" \
  -d '{
    "order_date": "2024-10-05 15:30:00",
    "sku": "A-1-Golden-Maple leaf",
    "unit_price": 150.5,
    "quantity": 100
  }'
```

### 3. 搜索订单

```bash
curl -X POST http://localhost:5000/erp_api/sale/search_sale_order \
  -H "Content-Type: application/json" \
  -d '{
    "status": "待同步",
    "current_page": 1,
    "page_size": 20
  }'
```

## 注意事项

1. **SKU销售价格表是全局表**，不区分项目（project_id）
2. **销售订单的总金额自动计算**：total_amount = unit_price * quantity
3. **订单状态只有两种**：待同步、已同步
4. **删除操作是物理删除**，不可恢复，请谨慎使用
5. **已同步的订单不能重复提交**，会返回错误
6. **订单日期支持两种格式**：YYYY-MM-DD 和 YYYY-MM-DD HH:MM:SS

## 相关资源

- [API总览](../README.md)
- [Sample响应数据](../../sample_response/sales/)
- [数据库建表语句](../../ec_erp_db.sql)
