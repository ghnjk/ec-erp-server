# 自动同步任务规约

## 模块概述

`auto_sync_tools/` 目录存放定时执行的自动化同步脚本，配合 crontab 完成 SKU、订单、店铺统计、库存等数据的同步与缓存维护。

目录：[auto_sync_tools/](../../auto_sync_tools/)

## 脚本清单（6 个）

| 脚本 | 主要用途 | 同步目标 | 多 project |
| ---- | -------- | -------- | ---------- |
| `auto_preload_order.py` | 预拉取新订单与待打印订单详情到本地 JSON 缓存 | 本地 JSON 缓存 | 否 |
| `auto_return_refund_order_to_warehouse.py` | 退货自动入库 | BigSeller | 否 |
| `sync_all_sku.py` | 同步全部 SKU 主数据到本地 JSON | 本地 JSON | 否 |
| `sync_order_to_es.py` | 同步 SKU 销售估算到 ES + MySQL | ES + MySQL（philipine 写死） | 否 |
| `sync_shop_statics_to_es.py` | 同步店铺销售统计到 ES + 本地 JSON | ES + 本地 JSON | 否 |
| `sync_sku_inventory.py` | 同步 SKU 库存到 MySQL | MySQL | 通过 `sync_tool_project_id` 切换 |

## 各脚本规约

### 1. `auto_preload_order.py`

- 入口：`auto_preload_order()` → 顺序调用 `auto_preload_new_order()` 与 `auto_preload_wait_print_order()`，各自 try/except 隔离
- 流程：
  1. 读取配置 `big_seller_warehouse_id`
  2. `build_big_seller_client()` + `login`
  3. 新订单：最近 24 小时 `search_new_order` 分页，过滤 `marketPlaceState == "To Process(New)"`，将订单 ID 加入待缓存列表
  4. 待打印：`search_wait_print_order_by_warehouse_id` 分页
  5. `_cache_order_details_if_not_exist`：本地缓存不存在时 `get_order_detail`，校验 `allocated == allocating` 后写入 `{cookies_dir}/order_cache/{order_id}.json`
- 当前代码中"标待打印"步骤被注释，仅做缓存预热
- Logger：`set_file_logger("../logs/preload_order.log", logger=logging.getLogger("preload_order"))`（**专用 logger**，非 `async_task.log`）

### 2. `auto_return_refund_order_to_warehouse.py`

- 入口：`__main__` → `disable_urlib_warning()` → `auto_return_refund_order_to_warehouse()`
- 流程：
  1. 读取 `big_seller_warehouse_id`
  2. `build_big_seller_client()`（依赖已有 cookie）
  3. 遍历过去 15 天，每天：
     - `query_not_op_refund_order_tracking_no_list(refund_date)`
     - 对每个运单 `query_refund_order_info_by_tracking_no(tracking_no, warehouse_id)`
     - 补充 `historyOrder`、`origin_num` 字段
     - `return_refund_order_to_warehouse(refund_order, warehouse_id)`
     - `time.sleep(0.3)` 节流
- 同步目标：BigSeller 退单入库
- 日志：仅 `print` 到 stdout（建议生产环境重定向到日志文件）

### 3. `sync_all_sku.py`

- 入口：`sync_all_sku()`
- 流程：
  ```python
  build_sku_manager().load_and_update_all_sku(build_big_seller_client())
  ```
- 同步目标：本地 `cookies/all_sku.json` 等
- 日志：无专用 logger（依赖 INVOKER）

### 4. `sync_order_to_es.py`

- 入口：`main()` → `for i in range(1, 3)` 处理"昨天与前天"两个日期
- 每日处理：`sync_sku_orders_to_es(date_str, sku_manager)`
- 流程：
  1. `build_big_seller_client()`（无显式 login）
  2. `client.load_sku_estimate_by_date(date, date)` 拉取销售估算
  3. 每条记录 `enrich_sku_info`：`SkuGroupMatcher.get_product_label` + `ShopManager.get_shop_platform / get_shop_owner`
  4. ES `index("ec_analysis_sku", id=docId, body=...)`
  5. 通过 `sku_manager` 解析组合 SKU；若分组为 `UNKNOWN` 则触发一次 `sku_manager.load_and_update_all_sku(client)` 再处理
  6. 调用 `SkuSaleEstimate.add_sku_sale(...)` 累加，最终 `store()` 写入 MySQL `t_sku_sale_estimate`
- 同步目标：
  - **ES** index：`ec_analysis_sku`
  - **MySQL**：`build_backend("philipine")` （**project_id 写死**，需注意）
- 日志：`print` + urllib3 静默

### 5. `sync_shop_statics_to_es.py`

- 入口：`sync_shop_statics_to_es()`
- 流程：
  1. `build_big_seller_client()`
  2. `shop_manager.load_an_update_sm(client)` 更新本地店铺 JSON
  3. 遍历最近 3 天：
     - `client.query_shop_sell_static(begin_date, end_date)`
     - `enrich_shop_static_info`（分组、负责人、平台）
     - ES `index("ec_shop_sell_static", body=...)`
- 同步目标：ES `ec_shop_sell_static` + 本地 `shop_group.json`
- 日志：`print`

### 6. `sync_sku_inventory.py`

- 入口：`sync_sku_inventory()`
- 流程：
  1. `build_backend(config.get("sync_tool_project_id", "philipine"))` 获取后端
  2. `build_big_seller_client()`
  3. `load_all_shipping_sku_info(backend)` 加载在途 SKU
  4. `backend.search_sku(...)` 批量
  5. 每条 SKU：`query_sku_inventory_detail` + `query_sku_detail` 计算 `available`、`avg_sell_quantity`、`inventory_support_days`、`shipping_stock_quantity`
  6. `backend.store_sku(sku_dto)` 落库
  7. `time.sleep(0.3)` 节流
- 同步目标：MySQL `t_sku_info`
- 多 project：通过 `sync_tool_project_id` 切换，单次仍处理一个 project
- 日志：`print`

## 部署与定时任务

推荐 crontab 配置（按业务节奏调整）：

```
# SKU 主数据同步：每天早上 8:00
0 8 * * * cd /path/to/ec-erp-server/auto_sync_tools && python sync_all_sku.py >> std.log 2>&1

# SKU 库存同步：每天 8:30
30 8 * * * cd /path/to/ec-erp-server/auto_sync_tools && python sync_sku_inventory.py >> std.log 2>&1

# 订单销售估算同步：每天凌晨 2:00
0 2 * * * cd /path/to/ec-erp-server/auto_sync_tools && python sync_order_to_es.py >> std.log 2>&1

# 店铺统计：每天凌晨 2:30
30 2 * * * cd /path/to/ec-erp-server/auto_sync_tools && python sync_shop_statics_to_es.py >> std.log 2>&1

# 退单入库：每小时
0 * * * * cd /path/to/ec-erp-server/auto_sync_tools && python auto_return_refund_order_to_warehouse.py >> std.log 2>&1

# 订单预热：每 5 分钟
*/5 * * * * cd /path/to/ec-erp-server/auto_sync_tools && python auto_preload_order.py >> std.log 2>&1
```

## 日志规范（建议）

- 定时任务标准输出统一重定向：`>> std.log 2>&1`
- 推荐迁移到统一 `set_file_logger("logs/async_task.log", logger=logging.getLogger("ASYNC_TASK"))`，与 Web 服务保持一致
- 当前 `auto_preload_order.py` 已使用专用 `preload_order.log`，其它脚本仅 `print`，存在差异

## 异常处理

- 单条 SKU/订单异常应捕获并继续处理下一个，不中断整体任务
- 任务级异常应进入 try/except 并记录详细堆栈
- 退单入库等关键链路应在失败时触发告警（当前未实现，需补充）

## 常见问题

| 问题 | 处理 |
| ---- | ---- |
| BigSeller 登录失效 | `build_big_seller_client()` 自动重新登录（cookie 过期） |
| ES 写入失败 | 当前 `print` 异常并继续，不会重试 |
| MySQL 锁冲突 | 适当 `sleep` + 重试 |
| 验证码识别消耗过快 | 检查是否频繁重新登录、cookie 持久化是否生效 |

## 注意事项

- `sync_order_to_es.py` 中 MySQL 后端 project_id 写死为 `philipine`，**多 project 部署时需要重构**为读取 `sync_tool_project_id`
- 所有脚本默认从项目根 `conf/application.json` 读取配置，运行时需保证 cwd 正确（脚本里 `set_file_logger` 路径是 `../logs/...`）
- ES 必填配置：`es_hosts`, `es_user`, `es_passwd`
