# Warehouse 模块规约（仓库/订单打印）

## 模块概述

Warehouse 模块提供仓库订单查询、订单打印任务全流程管理、SKU 拣货备注管理。

- 文件：[ec_erp_api/apis/warehouse.py](../../ec_erp_api/apis/warehouse.py)
- Blueprint：`warehouse_apis`
- url_prefix：`/erp_api/warehouse`
- 权限：`PMS_WAREHOUSE` (`"warehouse"`)
- 核心业务：[ec_erp_api/business/order_printing.py](../../ec_erp_api/business/order_printing.py)

## 接口清单（7 个）

每个接口的详细字段、示例与 Change-Log 见 [apis/design/warehouse/](./apis/design/warehouse/)。接口规约与变更管理流程见 [apis/spec.md](./apis/spec.md)。

| 路径 | 函数 | 说明 | Design |
| ---- | ---- | ---- | ------ |
| `/erp_api/warehouse/get_wait_print_order_ship_provider_list` | `get_order_statics` | 获取待打印订单的物流商分布（注意函数名与路径名不一致，以路径为准） | [get_wait_print_order_ship_provider_list.md](./apis/design/warehouse/get_wait_print_order_ship_provider_list.md) |
| `/erp_api/warehouse/search_wait_print_order` | `search_wait_print_order` | 按物流商查待打印订单分页 | [search_wait_print_order.md](./apis/design/warehouse/search_wait_print_order.md) |
| `/erp_api/warehouse/pre_submit_print_order` | `pre_submit_print_order` | 预提交打印任务（可能产生需补备注的 SKU 列表） | [pre_submit_print_order.md](./apis/design/warehouse/pre_submit_print_order.md) |
| `/erp_api/warehouse/search_manual_mark_sku_picking_note` | `search_manual_mark_sku_picking_note` | 搜索 SKU 拣货备注 | [search_manual_mark_sku_picking_note.md](./apis/design/warehouse/search_manual_mark_sku_picking_note.md) |
| `/erp_api/warehouse/submit_manual_mark_sku_picking_note` | `submit_manual_mark_sku_picking_note` | 提交 SKU 拣货备注 | [submit_manual_mark_sku_picking_note.md](./apis/design/warehouse/submit_manual_mark_sku_picking_note.md) |
| `/erp_api/warehouse/start_run_print_order_task` | `start_run_print_order_task` | 启动打印任务（异步线程） | [start_run_print_order_task.md](./apis/design/warehouse/start_run_print_order_task.md) |
| `/erp_api/warehouse/query_print_order_task` | `query_print_order_task` | 查询打印任务进度 | [query_print_order_task.md](./apis/design/warehouse/query_print_order_task.md) |

## 接口定义

### 1. `get_wait_print_order_ship_provider_list`

- 参数：无
- 业务：调用 BigSeller `get_wait_print_order_ship_provider_list(big_seller_warehouse_id)`
- 返回：`pack_json_response({ship_provider_list: [...]})`

### 2. `search_wait_print_order`

- 参数：
  - `shipping_provider_id` (string)
  - `current_page` (int)，`page_size` (int)
- 业务：调用 BigSeller `search_wait_print_order` 后裁剪字段
- 返回：`{total, list: [{id, shopId, platformOrderId, ...}]}`

### 3. `pre_submit_print_order`

- 参数：
  - `order_list` (array, **必填**)：订单对象列表
- 业务：
  1. `OrderAnalysis.parse_all_orders(order_list)` 提取所有 SKU 与数量
  2. 检查 SKU 是否需要补充拣货备注（`t_sku_picking_note` 中不存在或 `picking_unit_name` 为空）
  3. 若**无需**补备注：创建 `OrderPrintTask` 落库（`task_id` UUID）
  4. 若**需要**补备注：返回 `need_manual_mark_sku_list`，前端跳转补录页
- 返回：`{task_id, need_manual_mark_sku_list}`

### 4. `search_manual_mark_sku_picking_note`

- 参数：
  - `current_page` (int)，`page_size` (int)
  - `search_sku` (string, 可空)
- 业务：分页查询 `t_sku_picking_note`
- 返回：`{total, list: [SkuPickingNote...]}`

### 5. `submit_manual_mark_sku_picking_note`

- 参数：
  - `manual_mark_sku_list` (array, 必填)，每项需含：
    - `sku` (string)
    - `picking_unit` (int) / `picking_unit_name` (string)
    - `pkg_picking_unit` (int) / `pkg_picking_unit_name` (string)
    - `picking_sku_name` (string)
    - `support_pkg_picking` (bool, 默认 False)
- 业务：批量 upsert `t_sku_picking_note`
- 返回：`{manual_mark_sku_list}`

### 6. `start_run_print_order_task`

- 参数：`task_id` (string, **必填**)
- 业务：启动 `PrintOrderThread`（daemon 线程）执行打印流水线
- 返回：`pack_json_response({task})`（不含 `order_list` 字段，避免响应过大）

### 7. `query_print_order_task`

- 参数：`task_id` (string)
- 业务：查询当前任务状态、进度与生成的 PDF URL
- 返回：`pack_json_response({task})`

## 订单打印流水线（PrintOrderThread）

**实现**：[ec_erp_api/business/order_printing.py](../../ec_erp_api/business/order_printing.py)

- 类：`PrintOrderThread(threading.Thread, daemon=True)`
- 入口：`run()`
- 状态字段：`current_step`、`progress`、`logs`（追加时戳）
- 关键参数：`download_pdf_batch_size = 250`

### 流水线步骤

```mermaid
flowchart LR
    A[parsed_all_order_info]
    B[downloading_order_pdf]
    C[merging_pdf]
    D[marking_printed]
    E[compressing_pdf]
    F[pdf_ready]
    A --> B --> C --> D --> E --> F
```

| step_id | 含义 |
| ------- | ---- |
| `parsed_all_order_info` | 已解析订单信息 |
| `downloading_order_pdf` | 分批从 BigSeller 下载面单 PDF |
| `merging_pdf` | 合并并加注拣货备注 |
| `marking_printed` | 调用 BigSeller 标记已打印 |
| `compressing_pdf` | 压缩输出 PDF |
| `pdf_ready` | 完成，可下载 |

### 批处理

- `_download_all_order_pdf` → 按 `download_pdf_batch_size` 分批
- 每批：`download_order_mask_pdf_file(order_id, mark_id, platform, local_path)`
- `_split_and_note_pdf`：按页文本 `Order No:` 拆分订单 PDF，叠加拣货备注 overlay，并入总 `print_pdf_writer`
- `_mark_all_order_printed`：每批 `mark_order_printed`

### 输出

- 目录：`get_static_dir()/print/{task_id}/`
- 合并文件：`{task_id}.all.pdf`
- 访问 URL：`/print/{task_id}/{task_id}.all.pdf`
- 中文字体：`WeChatSansStd-Regular.ttf`

### 进度更新

`_update_task_step(step_id)`：
1. 查询步骤定义表（含中文文案）
2. 更新 `current_step`、`progress`、`logs`
3. 调用 `backend.update_order_print_task_without_order_list(task)` 持久化

## 错误码

| 错误码 | 含义 |
| ------ | ---- |
| 1001 | 系统异常 |
| 1003 | 参数错误（如 task_id 不存在） |

## 与 BigSeller 的交互

| 调用方 | BigSeller 方法 | 用途 |
| ------ | -------------- | ---- |
| `get_wait_print_order_ship_provider_list` | `get_wait_print_order_ship_provider_list` | 物流商列表 |
| `search_wait_print_order` | `search_wait_print_order` | 待打印订单 |
| `PrintOrderThread._download_all_order_pdf` | `download_order_mask_pdf_file` | 下载面单 |
| `PrintOrderThread._mark_all_order_printed` | `mark_order_printed` | 标记打印 |

BigSellerClient 通过 `big_seller_util.build_big_seller_client()` 获取（300s 缓存）。

## 数据表

| 表 | 用途 |
| -- | ---- |
| `t_order_print_task` | 打印任务（task_id, current_step, progress, order_list, logs, pdf_file_url） |
| `t_sku_picking_note` | SKU 拣货备注（拣货单位、外层包装单位、拣货 SKU 名称） |

## 文件存储与清理

- 打印 PDF 存放于 `static/print/{task_id}/`
- 临时文件存放于 `data/pdf/`
- 定时任务每天 5:20 清理 10 天前的打印文件（按部署计划，需在 crontab 配置）

## 注意事项

- `start_run_print_order_task` 启动后线程独立运行，HTTP 请求立即返回 task 元数据
- 前端通过轮询 `query_print_order_task` 获取进度
- 大批量订单（>2000 条）下载耗时较长，需关注 BigSeller 接口限流
- PDF 合并过程内存占用较大，建议单台机器并发任务数 ≤ 2
