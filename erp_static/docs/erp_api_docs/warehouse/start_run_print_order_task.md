# 启动打印订单任务

## 接口信息

- **接口路径**: `/erp_api/warehouse/start_run_print_order_task`
- **请求方法**: POST
- **接口描述**: 启动订单打印任务，异步生成包含拣货清单的PDF文件
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 打印任务ID（从 pre_submit_print_order 接口获取） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ task | object | 任务信息（不包含order_list字段） |
| &nbsp;&nbsp;∟ project_id | string | 项目ID |
| &nbsp;&nbsp;∟ task_id | string | 任务ID |
| &nbsp;&nbsp;∟ current_step | string | 当前步骤描述 |
| &nbsp;&nbsp;∟ progress | int | 进度百分比（0-100） |
| &nbsp;&nbsp;∟ logs | array | 任务日志列表 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |
| 其他 | 打印任务不存在 |

## 请求示例

```json
{
  "task_id": "172766506566"
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
    "task": {
      "project_id": "dev",
      "task_id": "172766506566",
      "current_step": "启动打印任务",
      "progress": 0,
      "logs": [
        "2024-10-01 00:00:00 - 初始化打印任务.",
        "2024-10-01 00:00:01 - 启动打印任务"
      ]
    }
  }
}
```

## 业务逻辑说明

1. 验证用户权限
2. 根据task_id从数据库获取打印任务
3. 如果任务不存在，返回错误
4. 更新任务日志，添加"启动打印任务"
5. 创建后台线程执行打印任务
6. 立即返回任务信息（不等待任务完成）

## 打印任务执行流程

后台线程会执行以下步骤（异步）：
1. 解析订单列表，生成拣货清单
2. 调用BigSeller API获取订单详情和物流标签
3. 生成PDF文件，包含：
   - 订单信息
   - 收货地址
   - 拣货清单
   - 物流标签
4. 保存PDF文件到服务器
5. 更新任务状态和进度

## 使用流程

完整的打印流程为：
1. 调用 `search_wait_print_order` 获取待打印订单
2. 调用 `pre_submit_print_order` 预处理订单
3. 如果有缺失的拣货备注，调用 `submit_manual_mark_sku_picking_note` 补充
4. 再次调用 `pre_submit_print_order` 获取task_id
5. 调用 `start_run_print_order_task` 启动打印任务
6. 轮询调用 `query_print_order_task` 查询任务进度
7. 任务完成后，从返回的pdf_file_url下载PDF文件

## 注意事项

- 此接口立即返回，不等待任务完成
- 任务在后台异步执行
- 通过 `query_print_order_task` 接口查询任务进度和结果
- 打印任务可能需要几分钟才能完成（取决于订单数量）
- 返回的task对象中不包含order_list字段（节省流量）
- 任务失败时，可以通过logs字段查看错误信息

