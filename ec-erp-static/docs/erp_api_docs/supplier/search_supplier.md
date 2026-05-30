# 搜索供应商

## 接口信息

- **接口路径**: `/erp_api/supplier/search_supplier`
- **请求方法**: POST
- **接口描述**: 分页查询供应商列表
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码，从1开始 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ total | int | 总记录数 |
| ∟ list | array | 供应商列表 |
| &nbsp;&nbsp;∟ supplier_id | int | 供应商ID |
| &nbsp;&nbsp;∟ supplier_name | string | 供应商名称 |
| &nbsp;&nbsp;∟ wechat_account | string | 微信账号 |
| &nbsp;&nbsp;∟ detail | string | 供应商详细信息（包含银行账号、联系方式等） |
| &nbsp;&nbsp;∟ project_id | string | 所属项目ID |
| &nbsp;&nbsp;∟ create_time | string | 创建时间 |
| &nbsp;&nbsp;∟ modify_time | string | 修改时间 |
| &nbsp;&nbsp;∟ modify_user | string | 修改人 |
| &nbsp;&nbsp;∟ is_delete | int | 是否删除，0未删除 |
| &nbsp;&nbsp;∟ version | int | 版本号 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "current_page": 1,
  "page_size": 10
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "list": [
      {
        "create_time": "2024-02-24 21:05:51",
        "detail": "6212260408009471538 中国工商银行 宗子龙\n18531712555",
        "is_delete": 0,
        "modify_time": "2024-02-24 21:05:51",
        "modify_user": "",
        "project_id": "dev",
        "supplier_id": 1,
        "supplier_name": "草地厂家(子龙)",
        "version": 0,
        "wechat_account": "-zilong"
      },
      {
        "create_time": "2024-02-24 21:06:21",
        "detail": "6212260408009471538 中国工商银行 宗子龙\n18531712555",
        "is_delete": 0,
        "modify_time": "2024-02-24 21:06:21",
        "modify_user": "",
        "project_id": "dev",
        "supplier_id": 2,
        "supplier_name": "草地厂家(子龙)",
        "version": 0,
        "wechat_account": "-zilong"
      }
    ],
    "total": 2
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1708844000800
}
```

## 业务逻辑说明

1. 验证用户是否有供应商管理权限
2. 根据分页参数查询供应商列表
3. 返回分页结果

## 注意事项

- 接口会根据当前项目ID自动过滤供应商数据
- 需要先登录并拥有供应商管理权限

