# 查询打印订单任务

## 接口信息

- **接口路径**: `/erp_api/warehouse/query_print_order_task`
- **请求方法**: POST
- **接口描述**: 查询打印任务的执行状态、进度、日志、最终 PDF URL
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限
- **Handler**: [ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `query_print_order_task`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 任务 ID |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.task | object | 任务信息（**不含** `order_list`） |
| ∟ project_id | string | 项目 ID |
| ∟ task_id | string | 任务 ID |
| ∟ current_step | string | 当前步骤文案 |
| ∟ progress | int | 0-100 |
| ∟ logs | array | 时戳日志列表 |
| ∟ pdf_file_url | string / null | 完成后 PDF URL |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | task_id 无对应任务 |
| 1008 | 权限不足 |

## 请求示例

```json
{ "body": { "task_id": "172766506566" } }
```

## 响应示例

### 进行中

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "task": {
      "project_id": "philipine",
      "task_id": "172766506566",
      "current_step": "正在生成 PDF 文件...",
      "progress": 50,
      "logs": [
        "2024-10-01 00:00:00 - 初始化打印任务.",
        "2024-10-01 00:00:01 - 启动打印任务",
        "2024-10-01 00:00:05 - 开始解析订单",
        "2024-10-01 00:00:10 - 正在生成 PDF 文件..."
      ],
      "pdf_file_url": null
    }
  }
}
```

### 完成

```json
{
  "data": {
    "task": {
      "project_id": "philipine",
      "task_id": "172766506566",
      "current_step": "已就绪",
      "progress": 100,
      "logs": ["...", "2024-10-01 00:00:30 - 打印的 PDF 文件生成 OK。"],
      "pdf_file_url": "/print/172766506566/172766506566.all.pdf"
    }
  }
}
```

### 失败

```json
{
  "data": {
    "task": {
      "current_step": "下载面单失败",
      "progress": 0,
      "logs": ["...", "2024-10-01 00:00:05 - 错误: SKU 不存在"],
      "pdf_file_url": null
    }
  }
}
```

## 业务逻辑说明

1. 权限校验
2. 调用 `backend.get_order_print_task_summary(task_id)`（**排除 `order_list`** 大字段）
3. 不存在返回 1003

## 任务状态说明

| current_step | 含义 | progress |
|--------------|------|----------|
| 初始化... | 任务创建 | 0 |
| 启动打印任务 | 已启动 | 0-10 |
| 开始解析订单 | 解析中 | 10-30 |
| 下载面单中 | 调用 BigSeller | 30-60 |
| 合并 PDF 中 | 合并 + overlay | 60-80 |
| 标记已打印 | BigSeller mark | 80-90 |
| 压缩中 | 压缩输出 | 90-99 |
| 已就绪 | 完成 | 100 |
| 任意「失败」字样 | 错误终止 | 任意 |

## 关联

- 数据表：[t_order_print_task](../../../data-model/design/t_order_print_task.md)
- 业务：[ec_erp_api/business/order_printing.py](../../../../../ec_erp_api/business/order_printing.py)
- 模块 spec：[warehouse_module_spec.md](../../../warehouse_module_spec.md)
- 业务文档：[docs/erp_api/warehouse/query_print_order_task.md](../../../../../docs/erp_api/warehouse/query_print_order_task.md)
- 兄弟接口：[start_run_print_order_task](./start_run_print_order_task.md)

## 轮询建议

- 间隔：2-3 秒
- 终止条件：
  - `progress == 100` → 成功
  - `current_step` 含「失败」字样 → 失败

## 注意事项

- 响应**不含** `order_list`（节省流量）
- `pdf_file_url` 是相对路径，前端需拼接服务器域名
- PDF 文件生成路径：`static/print/{task_id}/{task_id}.all.pdf`

## Change-Log

### 初始版本 - 查询打印任务接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `query_print_order_task`
- 数据表：`t_order_print_task`
