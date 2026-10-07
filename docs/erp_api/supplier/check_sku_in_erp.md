# 检查SKU是否在ERP

## 接口信息

- **接口路径**: `/erp_api/supplier/check_sku_in_erp`
- **请求方法**: POST
- **接口描述**: 查询当前登录国家的 ERP 是否存在该 SKU，不写入数据库
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sku | string | 是 | 商品 SKU，首尾空白会被去除 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0 表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 检查结果 |
| ∟ sku | string | 商品 SKU |
| ∟ exists | bool | ERP 中存在时为 true |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1003 | SKU 为空，或当前国 ERP 中不存在 |
| 1008 | 权限不足 |

## 请求示例

```json
{
  "sku": "A-1-Golden-Maple leaf"
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "sku": "A-1-Golden-Maple leaf",
    "exists": true
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

### 错误响应

```json
{
  "result": 1003,
  "resultMsg": "sku A-1-Golden-Maple leaf 不存在",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 校验 `PMS_SUPPLIER` 权限。
2. 去除 `sku` 首尾空白并校验非空。
3. 用当前国家的卖家客户端查询 ERP SKU。
4. 不存在则返回 1003，不创建、不恢复本地记录。

## 注意事项

- 导入新增 SKU 时，前端先调用本接口。ERP 没有该 SKU 时不调用写入接口。
- 不返回库存、图片等 ERP 明细。
