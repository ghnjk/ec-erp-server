# 启动打印订单任务

## 接口信息

- **接口路径**: `/erp_api/warehouse/start_run_print_order_task`
- **请求方法**: POST
- **接口描述**: 启动异步订单打印线程，立即返回任务元数据，不等待执行完成
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限
- **Handler**: [ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `start_run_print_order_task`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 来自 [pre_submit_print_order](./pre_submit_print_order.md) 的 task_id |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.task | object | 任务摘要（**不含** `order_list`） |
| ∟ project_id | string | 项目 ID |
| ∟ task_id | string | 任务 ID |
| ∟ current_step | string | 当前步骤 |
| ∟ progress | int | 0-100 |
| ∟ logs | array | 日志列表 |
| ∟ pdf_file_url | string / null | 完成时为 PDF URL |

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

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "task": {
      "project_id": "philipine",
      "task_id": "172766506566",
      "current_step": "启动打印任务",
      "progress": 0,
      "logs": [
        "2024-10-01 00:00:00 - 初始化打印任务.",
        "2024-10-01 00:00:01 - 启动打印任务"
      ],
      "pdf_file_url": null
    }
  }
}
```

## 业务逻辑说明

1. 权限校验
2. `backend.get_order_print_task(task_id)` 取任务，不存在返回 1003
3. 追加日志「启动打印任务」
4. 创建 `PrintOrderThread(daemon=True)` 异步执行
5. 立即返回任务摘要

## 异步流水线

详见 [warehouse_module_spec.md - PrintOrderThread](../../../warehouse_module_spec.md#订单打印流水线printorderthread) 与 [business/order_printing.py](../../../../../ec_erp_api/business/order_printing.py)：

```
parsed_all_order_info → downloading_order_pdf → merging_pdf → marking_printed → compressing_pdf → pdf_ready
```

## 关联

- 数据表：[t_order_print_task](../../../data-model/design/t_order_print_task.md)
- 业务：[ec_erp_api/business/order_printing.py](../../../../../ec_erp_api/business/order_printing.py) `PrintOrderThread`
- 模块 spec：[warehouse_module_spec.md](../../../warehouse_module_spec.md)
- 业务文档：[docs/erp_api/warehouse/start_run_print_order_task.md](../../../../../docs/erp_api/warehouse/start_run_print_order_task.md)
- 兄弟接口：[pre_submit_print_order](./pre_submit_print_order.md)、[query_print_order_task](./query_print_order_task.md)

## 注意事项

- 立即返回，不等待
- 后台线程执行，单台机器并发任务数 ≤ 2（防止 PDF 内存压力）
- 通过轮询 `query_print_order_task` 查询进度
- 响应中**不含** `order_list`，避免大字段传输

## Change-Log

### 初始版本 - 启动打印任务接口

**变更类型**：新增接口

**关联代码改动**：
- handler：[ec_erp_api/apis/warehouse.py](../../../../../ec_erp_api/apis/warehouse.py) `start_run_print_order_task`
- 业务：`ec_erp_api/business/order_printing.py` `PrintOrderThread`
- 数据表：`t_order_print_task`
