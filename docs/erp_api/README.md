# EC-ERP API 接口文档

本文档包含EC-ERP系统的所有API接口说明。

## 接口规范

### 通用说明

- **接口前缀**: `/erp_api/`
- **请求方法**: POST
- **Content-Type**: application/json
- **认证方式**: Session（需要先登录）

### 响应格式

所有接口统一返回格式：

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857,
  "data": {}
}
```

- `result`: 响应码，0表示成功，其他表示失败
- `resultMsg`: 响应消息
- `traceId`: 追踪ID，用于问题排查
- `data`: 响应数据（具体结构见各接口文档）

### 通用错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 系统异常/用户未登录 |
| 1002 | 用户认证失败 |
| 1003 | 参数错误 |
| 1004 | 业务逻辑错误 |
| 1008 | 权限不足 |

## 接口列表

### System 模块（系统管理）

用户登录和认证相关接口。

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [通过Token登录](./system/login_user_with_token.md) | `/erp_api/system/login_user_with_token` | 通过Base64编码的token进行登录 |
| [用户登录](./system/login_user.md) | `/erp_api/system/login_user` | 用户名密码登录 |
| [获取登录用户信息](./system/get_login_user_info.md) | `/erp_api/system/get_login_user_info` | 获取当前登录用户信息 |

### Supplier 模块（供应商管理）

供应商、SKU、采购单等管理接口。

#### 供应商管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [搜索供应商](./supplier/search_supplier.md) | `/erp_api/supplier/search_supplier` | 分页查询供应商列表 |

#### SKU管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [搜索SKU](./supplier/search_sku.md) | `/erp_api/supplier/search_sku` | 搜索SKU商品列表，支持多条件和排序 |
| [保存SKU](./supplier/save_sku.md) | `/erp_api/supplier/save_sku` | 保存或更新SKU信息 |
| [批量添加SKU](./supplier/add_sku.md) | `/erp_api/supplier/add_sku` | 批量添加SKU，自动同步BigSeller数据 |
| [同步所有SKU](./supplier/sync_all_sku.md) | `/erp_api/supplier/sync_all_sku` | 同步所有SKU的库存和销量信息 |

#### 采购价格管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [搜索SKU采购价格](./supplier/search_sku_purchase_price.md) | `/erp_api/supplier/search_sku_purchase_price` | 分页查询SKU采购价格 |
| [查询SKU采购价格](./supplier/query_sku_purchase_price.md) | `/erp_api/supplier/query_sku_purchase_price` | 查询指定供应商的SKU采购价格 |

#### 采购单管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [搜索采购单](./supplier/search_purchase_order.md) | `/erp_api/supplier/search_purchase_order` | 分页查询采购单列表 |
| [保存采购单](./supplier/save_purchase_order.md) | `/erp_api/supplier/save_purchase_order` | 保存采购单草稿 |
| [提交采购单并进入下一步](./supplier/submit_purchase_order_and_next_step.md) | `/erp_api/supplier/submit_purchase_order_and_next_step` | 提交采购单并流转状态 |

### Warehouse 模块（仓库管理）

订单打印、拣货备注等仓库操作接口。

#### 订单查询

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [获取待打印订单的物流商列表](./warehouse/get_wait_print_order_ship_provider_list.md) | `/erp_api/warehouse/get_wait_print_order_ship_provider_list` | 获取物流商列表及订单数量 |
| [搜索待打印订单](./warehouse/search_wait_print_order.md) | `/erp_api/warehouse/search_wait_print_order` | 根据物流商查询待打印订单 |

#### 拣货备注管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [搜索SKU拣货备注](./warehouse/search_manual_mark_sku_picking_note.md) | `/erp_api/warehouse/search_manual_mark_sku_picking_note` | 查询SKU拣货备注配置 |
| [提交SKU拣货备注](./warehouse/submit_manual_mark_sku_picking_note.md) | `/erp_api/warehouse/submit_manual_mark_sku_picking_note` | 批量提交SKU拣货备注 |

#### 打印任务管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [预提交打印订单](./warehouse/pre_submit_print_order.md) | `/erp_api/warehouse/pre_submit_print_order` | 预处理订单，检查拣货备注 |
| [启动打印订单任务](./warehouse/start_run_print_order_task.md) | `/erp_api/warehouse/start_run_print_order_task` | 启动异步打印任务 |
| [查询打印订单任务](./warehouse/query_print_order_task.md) | `/erp_api/warehouse/query_print_order_task` | 查询打印任务状态和结果 |

### Sales 模块（销售管理）

SKU销售价格、销售订单管理接口。

#### SKU销售价格管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [保存SKU销售价格](./sales/save_sku_sale_price.md) | `/erp_api/sale/save_sku_sale_price` | 保存或更新SKU销售价格 |
| [搜索SKU销售价格](./sales/search_sku_sale_price.md) | `/erp_api/sale/search_sku_sale_price` | 查询SKU销售价格列表 |

#### 销售订单管理

| 接口名称 | 接口路径 | 说明 |
|---------|---------|------|
| [创建销售订单](./sales/create_sale_order.md) | `/erp_api/sale/create_sale_order` | 创建新的销售订单 |
| [更新销售订单](./sales/update_sale_order.md) | `/erp_api/sale/update_sale_order` | 更新现有销售订单 |
| [删除销售订单](./sales/delete_sale_order.md) | `/erp_api/sale/delete_sale_order` | 删除销售订单 |
| [确认提交销售订单](./sales/submit_sale_order.md) | `/erp_api/sale/submit_sale_order` | 确认提交订单（待同步→已同步） |
| [搜索销售订单](./sales/search_sale_order.md) | `/erp_api/sale/search_sale_order` | 搜索销售订单列表 |

## 业务流程

### 采购流程

```
草稿 → 供应商捡货中 → 待发货 → 海运中 → 已入库 → 完成
```

1. **草稿**: 创建采购单，选择SKU和数量
2. **供应商捡货中**: 提交采购单，等待供应商确认
3. **待发货**: 确认采购清单和价格
4. **海运中**: 供应商发货，填写物流信息
5. **已入库**: 货物到达，点货入库
6. **完成**: 同步到ERP系统

### 打印流程

```
选择订单 → 预处理 → [补充拣货备注] → 启动打印 → 查询进度 → 下载PDF
```

1. **选择订单**: 通过 `get_wait_print_order_ship_provider_list` 和 `search_wait_print_order` 选择要打印的订单
2. **预处理**: 调用 `pre_submit_print_order` 检查SKU拣货备注
3. **补充备注**（如果需要）: 通过 `submit_manual_mark_sku_picking_note` 补充缺失的拣货备注
4. **启动打印**: 调用 `start_run_print_order_task` 启动异步任务
5. **查询进度**: 轮询 `query_print_order_task` 查看任务进度
6. **下载PDF**: 任务完成后，从返回的URL下载PDF文件

## 权限说明

系统中有以下权限角色：

- **PMS_SUPPLIER**: 供应商管理权限
  - 可以管理供应商、SKU、采购单
  
- **PMS_WAREHOUSE**: 仓库管理权限
  - 可以查询订单、配置拣货备注、打印订单

- **PMS_SALE**: 销售管理权限
  - 可以管理销售价格、销售订单

用户可以拥有多个角色，每个角色对应一个项目（国家/地区）。

## 数据隔离

系统支持多项目部署，通过 `project_id` 区分不同国家/地区：
- malaysia: 马来西亚
- philipine: 菲律宾
- india: 印度
- thailand: 泰国

所有接口会自动根据当前登录用户的项目ID过滤数据。

## 第三方集成

系统集成了以下第三方服务：

### BigSeller ERP
- SKU管理和库存同步
- 订单查询和打印
- 物流信息管理

配置项：
- `big_seller_mail`: BigSeller账号
- `big_seller_encoded_passwd`: 加密后的密码
- `big_seller_warehouse_id`: 仓库ID
- `big_seller_shelf_id`: 货架ID

## 开发指南

### 添加新接口

1. 在 `ec_erp_api/apis/` 下对应模块文件中添加路由
2. 使用 `@api_post_request()` 装饰器
3. 通过 `request_util` 获取参数
4. 通过 `request_context.get_backend()` 访问数据库
5. 使用 `response_util` 返回响应
6. 在本目录下创建接口文档

### 接口文档模板

```markdown
# 接口名称

## 接口信息
- **接口路径**: `/erp_api/模块/接口名`
- **请求方法**: POST
- **接口描述**: 接口功能说明
- **权限要求**: 需要的权限

## 请求参数
## 响应参数
## 错误码
## 请求示例
## 响应示例
## 业务逻辑说明
## 注意事项
```

## 更新日志

- 2024-10-07: 新增Sales模块，包含7个销售管理接口（SKU销售价格管理、销售订单管理）
- 2024-10: 生成初始API文档，包含20个接口

