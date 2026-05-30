# 预提交打印订单

## 接口信息

- **接口路径**: `/erp_api/warehouse/pre_submit_print_order`
- **请求方法**: POST
- **接口描述**: 预处理打印订单，解析订单中的SKU，检查是否所有SKU都有拣货备注，如果有缺失则返回需要手动标记的SKU列表
- **权限要求**: 需要 `PMS_WAREHOUSE` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_list | array | 是 | 订单列表（从 search_wait_print_order 接口获取的订单数据） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ task_id | string | 打印任务ID（如果所有SKU都有拣货备注），否则为null |
| ∟ need_manual_mark_sku_list | array | 需要手动标记拣货备注的SKU列表 |
| &nbsp;&nbsp;∟ sku | string | SKU编码 |
| &nbsp;&nbsp;∟ image_url | string | SKU图片URL |
| &nbsp;&nbsp;∟ desc | string | 辅助说明（案例） |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "order_list": [
    {
      "id": 5133175528,
      "shopId": 2100179,
      "platformOrderId": "908069598574548",
      "orderItemList": [
        {
          "varSku": "Yellow(CW-7)-2*4m",
          "quantity": 1
        }
      ]
    }
  ]
}
```

## 响应示例

### 所有SKU都有拣货备注

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "task_id": "172766506566",
    "need_manual_mark_sku_list": []
  }
}
```

### 有SKU缺少拣货备注

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760,
  "data": {
    "task_id": null,
    "need_manual_mark_sku_list": [
      {
        "sku": "Lawn-3.5m*5m",
        "image_url": "https://cf.shopee.ph/file/ph-11134207-7r98v-lzg47xuonptmd6",
        "desc": "案例：买家购买3个[G-10-TWO] => 实际扣除sku: 20个[G-10]"
      }
    ]
  }
}
```

## 业务逻辑说明

1. 验证用户权限
2. 解析订单列表，分析每个订单的SKU：
   - 查询订单详情，获取SKU匹配信息
   - 处理单一SKU和组合SKU
   - 检查每个SKU是否有拣货备注
3. 如果所有SKU都有拣货备注：
   - 创建打印任务
   - 保存到数据库
   - 返回task_id
4. 如果有SKU缺少拣货备注：
   - 收集缺少备注的SKU列表
   - 返回need_manual_mark_sku_list供用户补充

## SKU解析规则

### 单一SKU
直接从订单详情的`inventorySku`字段获取实际SKU

### 组合SKU
从订单详情的`varSkuGroupVoList`中解析出所有子SKU：
- 如果组合SKU本身有拣货备注（标记为不可拆分），则不拆分
- 否则拆分为多个子SKU，并计算实际数量

## 使用场景

此接口是打印流程的第一步：
1. 用户选择要打印的订单
2. 调用此接口预处理
3. 如果返回task_id，直接调用 `start_run_print_order_task` 开始打印
4. 如果返回need_manual_mark_sku_list，引导用户补充拣货备注

## 注意事项

- 订单数据需要从 `search_wait_print_order` 接口获取完整数据
- task_id生成规则：当前时间戳 * 100
- 需要先确保所有SKU都有拣货备注才能打印
- 拣货备注包含：拣货数量、拣货单位、拣货SKU名称

