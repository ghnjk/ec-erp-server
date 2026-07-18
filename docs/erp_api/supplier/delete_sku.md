# 删除SKU

## 接口信息

- **接口路径**: `/erp_api/supplier/delete_sku`
- **请求方法**: POST
- **接口描述**: 按当前项目和 SKU 逻辑删除商品主数据
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | 要删除的完整 SKU，首尾空白会被去除 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0 表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 成功时为空对象 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | SKU 为空 |
| 1004 | 当前项目中 SKU 不存在或已经删除 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "sku": "A-1-Green-Maple leaf"
}
```

## 响应示例

```json
{
  "data": {},
  "result": 0,
  "resultMsg": "success",
  "traceId": 1780000000002
}
```

## 业务逻辑说明

1. 校验 `PMS_SUPPLIER` 权限。
2. 去除 `sku` 首尾空白并校验非空。
3. 按当前 `project_id + sku` 查询记录，拒绝不存在或已删除的 SKU。
4. 将 `Fis_delete` 设置为 1 并更新 `Fmodify_time`。
5. `search_sku` 自动过滤该记录；再次通过 `add_sku` 添加同名 SKU 时可恢复。

## 注意事项

- 仅逻辑删除本地 SKU 主数据，不物理删除记录。
- 不级联删除采购价格、采购单或销售数据。
- 不修改 BigSeller/UpSeller 远端 SKU。
- SKU 列表要求用户精确输入目标 SKU 后才会发起此请求。
- 存量数据 `Fis_delete` 可能为 `NULL`，与 `0` 同等视为有效，可正常删除。
